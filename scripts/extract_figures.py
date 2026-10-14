"""Export visually reviewed figure regions from frontier reports without redrawing."""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path

import pymupdf
from archive_reports import VENDORS

ROOT = Path(__file__).resolve().parents[1]
ROLES = {'architecture', 'results', 'safety_evaluation', 'example', 'overview'}
LABELS = {
    'architecture': ('Architecture', '架构'), 'results': ('Results', '主要结果'),
    'safety_evaluation': ('Safety evaluation', '安全评测'),
    'example': ('Examples', '示例'), 'overview': ('Overview', '整体概览'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_selection(selection, report, document):
    if selection['source_sha256'] != report['source_sha256']:
        raise ValueError(f"Stale selection: {report['id']}")
    seen = set()
    for figure in selection['figures']:
        page = figure['page']
        if not isinstance(page, int) or not 1 <= page <= len(document):
            raise ValueError('Invalid source page')
        box = pymupdf.Rect(figure['bbox'])
        if box.is_empty or box.is_infinite or not document[page-1].rect.contains(box):
            raise ValueError('Figure bounds must lie inside the source page')
        if figure['role'] not in ROLES or figure.get('visual_review') is not True:
            raise ValueError('A supported role and visual review are required')
        if figure.get('caption_bbox') and figure.get('caption_in_crop', True):
            if not box.contains(pymupdf.Rect(figure['caption_bbox'])):
                raise ValueError('The full original caption must fit inside the crop')
        caption = figure.get('caption', '')
        normalize = lambda t: re.sub(r'\s+', '', unicodedata.normalize('NFKC', t))
        if caption and normalize(caption) not in normalize(document[page-1].get_text()):
            raise ValueError(f'Caption does not match native source text: {report["id"]}, page {page}')
        for block in document[page-1].get_text('dict')['blocks']:
            for line in block.get('lines', []):
                for span in line['spans']:
                    bounds = pymupdf.Rect(span['bbox'])
                    if span['text'].strip() and not (bounds & box).is_empty and not box.contains(bounds):
                        raise ValueError(f'Crop cuts source text: {report["id"]}, page {page}, {span["text"]!r}')
        key = (page, tuple(figure['bbox']))
        if key in seen:
            raise ValueError('Duplicate figure region')
        seen.add(key)


def export(output, selections, reports):
    lookup = {r['id']: r for r in reports}
    ids = [s['id'] for s in selections]
    if len(set(ids)) != len(ids) or set(ids) != set(lookup):
        raise ValueError('Selections must cover every current report exactly once')
    records = []
    for selection in selections:
        report = lookup[selection['id']]
        if report.get('source_kind') == 'html':
            from web_sources import export_figures
            folder, record = export_figures(ROOT, output, report, selection)
            write_report(folder, record)
            records.append(record)
            continue
        source = ROOT / report['source_pdf']
        if sha(source) != report['source_sha256']:
            raise ValueError(f'Changed source PDF: {source}')
        with pymupdf.open(source) as document:
            validate_selection(selection, report, document)
            record = {k: report[k] for k in ('id', 'vendor', 'title', 'models', 'document_type', 'source_pdf', 'source_url', 'source_sha256', 'source_version')}
            record.update(status='available' if selection['figures'] else 'no_suitable_figure_identified',
                          inspected_pages=selection['inspected_pages'],
                          reason_en=selection.get('reason_en', ''), reason_cn=selection.get('reason_cn', ''), figures=[])
            folder = output / report['vendor'] / report['id'].split(':', 1)[1]
            folder.mkdir(parents=True, exist_ok=True)
            for index, selected in enumerate(selection['figures'], 1):
                box = pymupdf.Rect(selected['bbox'])
                stem = f'figure-{index:02d}'
                pdf, png = folder / (stem + '.pdf'), folder / (stem + '.png')
                # Copy page content into a clipped form: preserve vectors, fonts and native bitmaps.
                with pymupdf.open() as cropped:
                    page = cropped.new_page(width=box.width, height=box.height)
                    page.show_pdf_page(page.rect, document, selected['page']-1, clip=box)
                    cropped.save(pdf, garbage=4, deflate=True, reproducible=True, no_new_id=True)
                    dpi = min(600, int(10000 * 72 / max(box.width, box.height)))
                    pix = page.get_pixmap(dpi=dpi, alpha=False, annots=False)
                    pix.save(png)
                item = {k: selected[k] for k in ('page', 'figure_number', 'role', 'caption', 'bbox')}
                if selected.get('source_kind'):
                    item['source_kind'] = selected['source_kind']
                item.update(coordinate_system='PDF points, top-left origin',
                            page_size=list(document[selected['page']-1].rect)[2:],
                            review_method='agent_visual_source_page_review',
                            caption_in_crop=selected.get('caption_in_crop', True),
                            caption_bbox=selected.get('caption_bbox'),
                            png_dpi=dpi, png_size=[pix.width, pix.height],
                            pdf_path=str(pdf.relative_to(ROOT)), png_path=str(png.relative_to(ROOT)),
                            pdf_sha256=sha(pdf), png_sha256=sha(png))
                record['figures'].append(item)
        write_report(folder, record)
        records.append(record)
    payload = {'schema_version': 1, 'method': 'native_pdf_regions_and_official_web_assets', 'reports': records}
    (output / 'index.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    write_index(output, records)
    return records


def write_report(folder, report):
    slug = report['id'].split(':', 1)[1]
    for cn in (False, True):
        home = 'README_CN.md' if cn else 'README.md'
        label = '阅读报告' if cn else 'Read report'
        target = f"../../../abstracts/{report['vendor']}/{slug}.md"
        (folder / home).write_text(f"# {report['title']}\n\n[{label}]({target})\n")


def write_index(output, reports):
    for cn in (False, True):
        home = 'README_CN.md' if cn else 'README.md'
        label = '阅读报告' if cn else 'Read reports'
        (output / home).write_text(f"[{label}](../abstracts/{home})\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selections', type=Path, default=ROOT / 'figures/selections.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'figures')
    args = parser.parse_args()
    reports = json.loads((ROOT / 'abstracts/index.json').read_text())['reports']
    selections = json.loads(args.selections.read_text())
    args.output.mkdir(parents=True, exist_ok=True)
    records = export(args.output, selections, reports)
    print(f"{len(records)} reports; {sum(len(r['figures']) for r in records)} figures exported")


if __name__ == '__main__':
    main()
