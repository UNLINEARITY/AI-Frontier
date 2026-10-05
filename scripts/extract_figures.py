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
    payload = {'schema_version': 1, 'method': 'native_pdf_region_export', 'reports': records}
    (output / 'index.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    write_index(output, records)
    return records


def write_report(folder, report):
    for cn in (False, True):
        home = 'README_CN.md' if cn else 'README.md'
        other = 'README.md' if cn else 'README_CN.md'
        lines = [f"# {report['title']}", '',
                 f'[English]({other}) · [核心图片](../../{home})' if cn else f'[中文]({other}) · [Core figures](../../{home})', '',
                 f"[{'原始 PDF' if cn else 'Original PDF'}](../../../{report['source_pdf']}) · [{'官方来源' if cn else 'Official source'}]({report['source_url']})", '']
        if not report['figures']:
            lines += ['本报告未选出适合作为核心图片的独立图示。模型信息与评测请阅读原始 PDF。' if cn else
                      'No standalone core figure selected from this report. Read the original PDF for model details and evaluations.', '']
        for i, figure in enumerate(report['figures'], 1):
            number = f"Figure {figure['figure_number']}" if figure['figure_number'] is not None else ('未编号图' if cn else 'Unnumbered graphic')
            lines += [f"## {LABELS[figure['role']][int(cn)]} · {number}", '',
                      f"{'原文第' if cn else 'Source page: '}{figure['page']}{'页' if cn else ''} · [PNG](figure-{i:02d}.png) · [{'保留原始图形的 PDF' if cn else 'PDF with original graphics'}](figure-{i:02d}.pdf)", '',
                      f"[{'查看原页' if cn else 'View source page'}](../../../{report['source_pdf']}#page={figure['page']})", '',
                      f"![{LABELS[figure['role']][int(cn)]}](figure-{i:02d}.png)", '', figure['caption'], '']
        (folder / home).write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()).rstrip() + '\n')


def write_index(output, reports):
    for cn in (False, True):
        home = 'README_CN.md' if cn else 'README.md'
        sibling = 'README.md' if cn else 'README_CN.md'
        count = sum(len(r['figures']) for r in reports)
        available = sum(bool(r['figures']) for r in reports)
        lines = ['# 前沿模型核心图片' if cn else '# Core figures from frontier reports', '',
                 f'[English]({sibling}) · [原文概要](../abstracts/{home}) · [首页](../{home})' if cn else f'[中文]({sibling}) · [Source summaries](../abstracts/{home}) · [Home](../{home})', '',
                 '直接查看报告中的架构、主要结果与安全评测。保留原图和图注，高清 PNG 便于阅读，裁切 PDF 保留原始图形。' if cn else
                 'See architectures, headline results, and safety evaluations straight from the reports. Original graphics and captions, with high-resolution PNGs and cropped PDFs.', '',
                 f"**{count} {'张图片' if cn else 'figures'} · {available} {'份报告提供图片' if cn else 'reports with selected figures'} · {len(reports)} {'份报告已检查' if cn else 'reports inspected'}**", '',
                 'PNG 的像素数不等于原始位图的分辨率；裁切不会增加原图细节。版权与使用条款仍归原发布者所有。' if cn else
                 'Rendering at high DPI does not add detail to embedded low-resolution bitmaps. Copyright and terms remain with the original publishers.', '']
        for vendor in dict.fromkeys(r['vendor'] for r in reports):
            label = 'Z.ai / Zhipu AI' if vendor == 'zai' and not cn else VENDORS[vendor]
            lines += [f'## {label}', '', '| 报告 | 图片 |' if cn else '| Report | Figures |', '| --- | --- |']
            for r in reports:
                if r['vendor'] != vendor:
                    continue
                slug = r['id'].split(':', 1)[1]
                roles = ' · '.join(LABELS[f['role']][int(cn)] for f in r['figures']) or ('未选出合适图片' if cn else 'No suitable figure selected')
                lines.append(f"| [{r['title']}]({vendor}/{slug}/{home}) | {roles} |")
            lines.append('')
        (output / home).write_text('\n'.join(lines))


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
