"""Extract source summaries without generation; retain provenance and review flags."""
import argparse
import csv
import hashlib
import json
import logging
import re
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTChar, LTTextContainer
from pypdf import PdfReader

from archive_reports import VENDORS

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = {
    'abstract': ('abstract', 0), 'executive summary': ('executive_summary', 1),
    'model overview': ('overview', 2), 'overview': ('overview', 2),
    'model description': ('description', 3), 'description': ('description', 3),
    'summary': ('summary', 4), 'introduction': ('introduction', 5),
    'model architecture': ('model_architecture', 6),
}
KNOWN_BOUNDARIES = re.compile(r'^(?:model dependencies|model architecture|architecture|modalities|context length|total model size|inputs|outputs|training|training data|limitations|intended use|intended uses|model details|evaluation|evaluations|capabilities|safety|contents|table of contents|open-source code|open-weight model checkpoint|open synthetic dataset|open evaluation benchmark)$', re.I)
OPENING = re.compile(r'^(?:We (?:introduce|present|describe|propose)|This (?:paper|report)|State[- ]of[- ]the[- ]art)', re.I)


def compact(text):
    # Comparison only: preserve the original Unicode and hyphens in published text.
    text = unicodedata.normalize('NFKC', text).replace('\u00ad', '')
    return re.sub(r'\s+', '', re.sub(r'-\s*\n\s*(?=[a-z])', '', text))


def source_agrees(fragment, page):
    # Word-positioned PDFs can insert a newline after a genuine word hyphen.
    # Compare literal glyph order before normalizing line-wrap hyphens.
    glyphs = lambda value: re.sub(r'\s+', '', unicodedata.normalize('NFKC', value))
    return glyphs(fragment) in glyphs(page) or compact(fragment) in compact(page)


def heading(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    first = lines[0]
    prefix = re.sub(r'^(?:\d+(?:\.\d+)*\.?|[IVX]+\.)\s*', '', first).strip()
    # A heading can wrap, or share its first text box with the paragraph.
    for name, (kind, rank) in HEADINGS.items():
        if re.fullmatch(re.escape(name) + r'[.:—–-]?', prefix, re.I):
            return kind, rank, first, '\n'.join(lines[1:])
    if len(lines) >= 2 and (first + ' ' + lines[1]).lower() == 'executive summary':
        return 'executive_summary', 1, first + ' ' + lines[1], '\n'.join(lines[2:])
    match = re.match(r'^Abstract[.:—–-]\s*(.+)$', first, re.I)
    if match:
        return 'abstract', 0, first[:first.index(match[1])].strip(), match[1] + '\n' + '\n'.join(lines[1:])
    inline = re.match(r'^(Description|Model description|Overview):\s*(.+)$', first, re.I)
    if inline:
        kind, rank = HEADINGS[inline[1].lower()]
        return kind, rank, inline[1] + ':', inline[2] + '\n' + '\n'.join(lines[1:])
    table = re.match(r'^(Model architecture)\s{2,}(.+)$', first, re.I)
    if table:
        kind, rank = HEADINGS[table[1].lower()]
        return kind, rank, table[1], table[2] + '\n' + '\n'.join(lines[1:])
    if re.match(r'^\d+\.?\s+Safety Overview\b', first, re.I):
        return 'overview', 2, first, '\n'.join(lines[1:])
    return None


def contents_page(page):
    blocks = [b for b in page['blocks'] if b['bbox'][2] >= page['width'] * .08]
    text = '\n'.join(b['text'] for b in blocks)
    numbered_lines = len(re.findall(r'(?m)^\s*\d+(?:\.\d+)*\.?\s+[A-Z]', text))
    number_column = any(len(re.findall(r'(?m)^\s*\d+\s*$', b['text'])) >= 8 for b in blocks)
    return (number_column and numbered_lines >= 4) or bool(re.search(r'(?im)^\s*(?:table of )?contents\s*$', text)) or len(re.findall(r'\.{3,}', text)) > 5


def usable(block, page):
    text = block['text'].strip()
    if not text or re.fullmatch(r'\d+|[ivx]+', text, re.I):
        return False
    if block['bbox'][2] < page['width'] * .08:
        return False  # Rotated arXiv margin stamps are not summary text.
    if block['bbox'][3] < page['height'] * .055:
        return False
    if block['font_size'] < 8.5 and len(text) < 500:
        return False
    return True


def boundary(block, start_font):
    lines = [line.strip() for line in block['text'].splitlines() if line.strip()]
    if not lines:
        return False
    first = lines[0]
    if heading(block['text']):
        return True
    if re.match(r'^(?:Figure|Table)\s+\d+[:.]|^(?:Webpage|Model weights):', first, re.I):
        return True
    if KNOWN_BOUNDARIES.fullmatch(first.split(':', 1)[0]):
        return True
    if re.match(r'^\d+(?:\.\d+)*\.?\s+[A-Z]', first) and len(first) < 140:
        return True
    return (len(lines) == 1 and len(first) < 100 and len(first.split()) < 12
            and not re.search(r'[.!?,;:]$', first) and block['font_size'] >= max(start_font * .98, 12))


def choose_section(pages):
    candidates = []
    for pi, page in enumerate(pages):
        if contents_page(page):
            continue
        for bi, block in enumerate(page['blocks']):
            found = heading(block['text'])
            if found and usable(block, page) and not (found[0] == 'description' and pi > 2):
                kind, rank, label, remainder = found
                candidates.append((rank, pi, bi, kind, label, remainder))
    # Some technical reports place an unlabelled abstract before Introduction.
    if pages and not contents_page(pages[0]):
        for bi, block in enumerate(pages[0]['blocks']):
            if heading(block['text']) or boundary(block, 14):
                if candidates and any(c[1] == 0 and c[2] == bi for c in candidates):
                    break
            if usable(block, pages[0]) and len(block['text']) > 220 and OPENING.match(block['text'].strip()):
                candidates.append((0, 0, bi, 'opening_summary', None, block['text']))
                break
    if not candidates:
        return None
    for _, pi, bi, kind, label, remainder in sorted(candidates):
        fragments = []
        start_block = pages[pi]['blocks'][bi]
        start_font = start_block['font_size']
        body_font = start_font if len(remainder) > 120 else next((b['font_size'] for b in pages[pi]['blocks'][bi+1:] if usable(b, pages[pi]) and len(b['text']) > 120), start_font)
        # Label/value model-card tables require row geometry rather than text order.
        if kind in {'description', 'model_architecture'} and not remainder and start_block['bbox'][2] < pages[pi]['width'] * .35:
            values = [b for b in pages[pi]['blocks'] if b['bbox'][0] > start_block['bbox'][2] + 15
                      and abs(b['bbox'][3] - start_block['bbox'][3]) < 5 and len(b['text']) > 120]
            if len(values) == 1:
                return dict(section_type=kind, source_heading=label,
                            fragments=[{'page': pi + 1, 'text': values[0]['text'].strip()}],
                            raw_text=values[0]['text'].strip(), boundary_found=True)
        ended = False
        for pn in range(pi, len(pages)):
            page = pages[pn]
            if pn != pi and contents_page(page):
                ended = True
                break
            for bn in range(bi if pn == pi else 0, len(page['blocks'])):
                block = page['blocks'][bn]
                # IEEE section headings can be smaller than the paragraph font.
                # Recognize their boundary before filtering small body/annotation text.
                if (pn != pi or bn != bi) and block['bbox'][2] >= page['width'] * .08 and boundary(block, start_font):
                    ended = True
                    break
                if not usable(block, page) or (pn != pi or bn != bi) and block['font_size'] < body_font * .9:
                    continue
                if pn == pi and bn == bi:
                    text = remainder
                else:
                    # Exclude repeated running headers, not body text.
                    if block['bbox'][1] > page['height'] * .93 and len(block['text']) < 160:
                        continue
                    text = block['text']
                if text.strip():
                    fragments.append({'page': pn + 1, 'text': text.strip()})
            if ended:
                break
        if kind == 'model_architecture':
            grouped = []
            for fragment in fragments:
                if grouped and grouped[-1]['page'] == fragment['page'] and not re.match(r'^\(\d+\)', fragment['text']):
                    grouped[-1]['text'] += '\n' + fragment['text']
                else:
                    grouped.append(dict(fragment))
            fragments = grouped
        raw = '\n\n'.join(f['text'] for f in fragments)
        if len(raw) >= 40 and len(raw.split()) >= 8:
            return dict(section_type=kind, source_heading=label, fragments=fragments,
                        raw_text=raw, boundary_found=ended)
    return None


def font_sizes(node):
    if isinstance(node, LTChar):
        yield node.size
    elif hasattr(node, '__iter__'):
        for child in node:
            yield from font_sizes(child)


def extract_cached(path, sha256, cache, scan_pages):
    key = f'{sha256}-pypdf6.19.0-pdfminer20260107-pages{scan_pages}.json'
    target = cache / key
    if target.exists():
        return json.loads(target.read_text())
    reader = PdfReader(path)
    native = [page.extract_text() or '' for page in reader.pages[:scan_pages]]
    layouts = []
    for layout in extract_pages(path, page_numbers=range(scan_pages)):
        blocks = []
        for block in layout:
            if isinstance(block, LTTextContainer):
                sizes = list(font_sizes(block))
                blocks.append(dict(text=block.get_text(), bbox=list(block.bbox),
                                   font_size=sum(sizes) / len(sizes) if sizes else 0))
        layouts.append(dict(width=layout.width, height=layout.height, blocks=blocks))
    result = dict(pypdf_pages=native, pdfminer_pages=layouts, page_count=len(reader.pages))
    target.write_text(json.dumps(result, ensure_ascii=False))
    return result


def extract_report(item, cache, scan_pages):
    row = item['row']
    path = ROOT / row['local_path']
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != row['sha256']:
        raise ValueError(f"Source PDF checksum mismatch: {row['local_path']}")
    extracted = extract_cached(path, digest, cache, scan_pages)
    section = choose_section(extracted['pdfminer_pages'])
    result = dict(id=f"{row['vendor']}:{item['slug']}", vendor=row['vendor'], title=row['title'],
                  models=item['models'], document_type=row['document_type'], source_pdf=row['local_path'],
                  source_url=row['source_url'], source_sha256=digest, source_version=row['version'],
                  reader_scope=item.get('reader_scope', 'frontier'),
                  method='native_text', extractors={'primary': 'pdfminer.six 20260107', 'comparison': 'pypdf 6.19.0'},
                  manual_review=False, status='no_summary_identified', review_reasons=[],
                  section_type=None, source_heading=None, pages=[], raw_text='', text='',
                  source_fragments=[], text_sha256=None, cross_check=None, initial_cross_check=None,
                  source_review=None, inspected_pages=min(scan_pages, extracted['page_count']))
    if not section:
        result['review_reasons'] = ['No supported summary heading or opening paragraph identified in inspected pages.']
        return result
    result.update({k: section[k] for k in ('section_type', 'source_heading', 'raw_text')})
    result['source_fragments'] = section['fragments']
    result['pages'] = sorted({f['page'] for f in section['fragments']})
    result['text'] = '\n\n'.join(re.sub(r'\s+', ' ', f['text']).strip() for f in section['fragments'])
    matches = [source_agrees(f['text'], extracted['pypdf_pages'][f['page'] - 1])
               for f in section['fragments']]
    result['cross_check'] = {'matched_fragments': sum(matches), 'total_fragments': len(matches),
                             'comparison': 'literal_glyph_order_or_line_wrap_normalization'}
    if not all(matches):
        result['review_reasons'].append('Independent text extractors disagree on one or more paragraphs.')
    if not section['boundary_found'] and result['pages'][-1] < extracted['page_count']:
        result['review_reasons'].append('Section reaches scan limit without a confirmed ending.')
    if re.search(r'\ufffd|[A-Za-z]{45,}', re.sub(r'https?://\S+', '', result['text'])):
        result['review_reasons'].append('Possible encoding or word-spacing issue.')
    if len(result['text'].split()) > 2000:
        result['review_reasons'].append('Unusually long selection; section boundary needs review.')
    result['status'] = 'needs_review' if result['review_reasons'] else 'cross_checked'
    result['text_sha256'] = hashlib.sha256(result['text'].encode()).hexdigest()
    return result


def apply_source_review(report, cache, scan_pages):
    path = ROOT / 'abstracts/reviews.json'
    if not path.exists():
        return report
    reviews = json.loads(path.read_text())['reviews']
    for review in reviews:
        if review['id'] != report['id'] or review['source_sha256'] != report['source_sha256']:
            continue
        row = dict(local_path=report['source_pdf'])
        source = extract_cached(ROOT / row['local_path'], report['source_sha256'], cache, scan_pages)
        parts = []
        for region in review.get('ranges', [review]):
            raw = source['pypdf_pages'][region['page'] - 1][region['start_offset']:region['end_offset']]
            if hashlib.sha256(raw.encode()).hexdigest() != region['raw_text_sha256']:
                raise ValueError('Reviewed source text changed; do not reuse the review.')
            parts.append({'page': region['page'], 'text': raw})
        raw = '\n'.join(part['text'] for part in parts)
        # A moved glyph can change reading order without changing source characters.
        if Counter(compact(raw)) != Counter(compact(report['raw_text'])):
            raise ValueError('Reviewed alternate extraction changes source characters.')
        report['initial_cross_check'] = report['cross_check']
        report['cross_check'] = {'method': 'normalized_character_inventory', 'agrees': True, 'reading_order_check': 'visual_source_page'}
        report['extractors'] = {'primary': 'pypdf 6.19.0', 'comparison': 'pdfminer.six 20260107'}
        report.update(raw_text=raw, text=re.sub(r'\s+', ' ', raw).strip(), pages=sorted({p['page'] for p in parts}),
                      status='source_reviewed', source_review=review,
                      source_fragments=parts,
                      review_reasons=[])
        report['text_sha256'] = hashlib.sha256(report['text'].encode()).hexdigest()
    return report


def current_reports():
    models = json.loads((ROOT / 'model-coverage.json').read_text())['models']
    models = [m for m in models if m.get('lifecycle', 'active') == 'active'
              and (m.get('latest_categories') or m.get('frontier_categories'))]
    sources = {(s['vendor'], s['slug']): s for s in json.loads((ROOT / 'sources.json').read_text())}
    with (ROOT / 'catalog.csv').open(newline='', encoding='utf-8') as stream:
        rows = list(csv.DictReader(stream))
    reports, missing = {}, []
    for model in models:
        found = False
        for slug in model.get('report_slugs', []):
            source = sources[(model['vendor'], slug)]
            matches = [r for r in rows if r['vendor'] == model['vendor'] and r['title'] == source['title'] and r['status'] == 'archived']
            if matches:
                row = max(matches, key=lambda r: (r['source_updated_date'], r['retrieved_at']))
                reports.setdefault(row['local_path'], dict(row=row, slug=slug, models=[]))['models'].append(model['model'])
                found = True
        if not found:
            missing.append(dict(vendor=model['vendor'], model=model['model'],
                                source_url=model.get('frontier_source_url', model['source_url'])))
    # Keep previously extracted report URLs usable when a latest model is superseded.
    # They remain archive readers, separate from the active frontier navigation.
    previous = ROOT / 'abstracts/index.json'
    if previous.exists():
        by_path = {r['local_path']: r for r in rows if r['status'] == 'archived'}
        selected_ids = {(i['row']['vendor'], i['slug']) for i in reports.values()}
        for old in json.loads(previous.read_text())['reports']:
            if not old.get('source_pdf') or tuple(old['id'].split(':', 1)) in selected_ids:
                continue
            row = by_path.get(old['source_pdf'])
            if not row or row['sha256'] != old['source_sha256']:
                raise ValueError(f"Stale historical reader binding: {old['id']}")
            reports[row['local_path']] = dict(row=row, slug=old['id'].split(':', 1)[1],
                                              models=old['models'], reader_scope='historical')
    return list(reports.values()), missing


def write_outputs(output, reports, missing, write_index=True):
    output.mkdir(parents=True, exist_ok=True)
    figure_index = ROOT / 'figures/index.json'
    figures = {r['id']: r for r in json.loads(figure_index.read_text())['reports']} if figure_index.exists() else {}
    for report in reports:
        slug = report['id'].split(':', 1)[1]
        target = output / report['vendor'] / f'{slug}.md'
        target.parent.mkdir(exist_ok=True)
        report['markdown_path'] = str(target.relative_to(ROOT))
        lines = [f"# {report['title']}", '',
                 f"[Official source]({report['source_url']})", '']
        if report['text']:
            if report['source_heading']:
                lines += [f"## {report['source_heading']}", '']
            lines += [report['text'], '']
        selected = figures.get(report['id'], {})
        if selected.get('source_sha256') == report['source_sha256']:
            for figure in selected.get('figures', []):
                number = figure.get('figure_number')
                if number is not None:
                    number = str(number) if re.match(r'^(?:Figure|Fig\.|Table)\s', str(number)) else f"Figure {number}"
                else:
                    number = ('Table' if figure.get('source_kind') == 'table' else
                              'Image' if figure.get('source_kind') == 'image' and figure.get('page') is None else 'Figure')
                if figure.get('lead_in'):
                    lines += [figure['lead_in'], '']
                alt = figure.get('alt') or number
                alt = alt.replace('[', '\\[').replace(']', '\\]')
                lines += [f"![{alt}](../../{figure['png_path']})", '']
                if figure.get('caption'):
                    lines += [figure['caption'], '']
                if figure.get('page') is not None:
                    lines += [f"p. {figure['page']}", '']
        target.write_text('\n'.join(line.rstrip() for line in '\n'.join(lines).splitlines()).rstrip() + '\n')
    payload = dict(schema_version=1, extracted_at=date.today().isoformat(), reports=reports,
                   models_without_archived_reports=missing)
    if write_index:
        (output / 'index.json').write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    for chinese in (False, True):
        name = 'README_CN.md' if chinese else 'README.md'
        frontier = [r for r in reports if r.get('reader_scope') != 'historical']
        figure_count = sum(len(figures.get(r['id'], {}).get('figures', [])) for r in frontier
                           if figures.get(r['id'], {}).get('source_sha256') == r['source_sha256'])
        lines = ['# 前沿阅读' if chinese else '# Frontier reading', '',
                 '[English](README.md) · [首页](../README_CN.md)' if chinese else '[中文](README_CN.md) · [Home](../README.md)', '',
                 f"**{len(frontier)} {'篇原文概要' if chinese else 'source overviews'} · {figure_count} {'张核心图片' if chinese else 'core figures'}**", '']
        for vendor, label in VENDORS.items():
            group = [r for r in frontier if r['vendor'] == vendor]
            if not group:
                continue
            lines += [f"## {label if chinese or vendor != 'zai' else 'Z.ai / Zhipu AI'}", '']
            lines += [f"- [{r['title']}]({vendor}/{r['id'].split(':', 1)[1]}.md)" for r in group]
            lines.append('')
        (output / name).write_text('\n'.join(lines).rstrip() + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'abstracts')
    parser.add_argument('--render-only', action='store_true', help='Render existing source results without extracting again.')
    parser.add_argument('--scan-pages', type=int, default=12)
    args = parser.parse_args()
    if args.render_only:
        payload = json.loads((args.output / 'index.json').read_text())
        write_outputs(args.output.resolve(), payload['reports'], payload['models_without_archived_reports'], write_index=False)
        return
    logging.getLogger('pypdf').setLevel(logging.ERROR)
    logging.getLogger('pdfminer').setLevel(logging.ERROR)
    cache = ROOT / '.cache/abstracts'
    cache.mkdir(parents=True, exist_ok=True)
    items, missing = current_reports()
    reports = [apply_source_review(extract_report(item, cache, args.scan_pages), cache, args.scan_pages) for item in items]
    from web_sources import current_summaries
    web = current_summaries(ROOT, json.loads((ROOT / 'model-coverage.json').read_text())['models'])
    reports.extend(web)
    write_outputs(args.output.resolve(), reports, missing)
    print(json.dumps(dict(reports=len(reports), statuses=dict(Counter(r['status'] for r in reports)),
                          sections=dict(Counter(r['section_type'] for r in reports)), models_without_pdf=len(missing))))


if __name__ == '__main__':
    main()
