"""Source-bound official web passages and native assets for the unified readers."""
import hashlib
import json
import re
import shutil
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin


def digest(data):
    return hashlib.sha256(data).hexdigest()


def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()


class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.parts = []
        self.asset_references = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'img', 'source'}:
            if attrs.get('src'):
                self.asset_references.add(attrs['src'])
            for candidate in (attrs.get('srcset') or '').split(','):
                if candidate.strip():
                    self.asset_references.add(candidate.strip().split()[0])
        hidden = tag in {'script', 'style', 'noscript'} or 'sr-only' in (attrs.get('class') or '').split()
        if tag not in {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'wbr', 'area', 'embed'}:
            self.stack.append((tag, hidden or any(h for _, h in self.stack)))
        if tag in {'p', 'div', 'h1', 'h2', 'h3', 'br', 'li', 'figcaption'}:
            self.parts.append('\n')

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if tag in {'p', 'div', 'h1', 'h2', 'h3', 'li', 'figcaption'}:
            self.parts.append('\n')

    def handle_data(self, data):
        if not any(h for _, h in self.stack):
            self.parts.append(data)


def load_sources(root):
    path = root / 'abstracts/web-sources.json'
    sources = json.loads(path.read_text())['sources'] if path.exists() else []
    ids = [s['id'] for s in sources]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate official web source ID')
    for source in sources:
        if (not source['id'].startswith(source['vendor'] + ':') or not source['models']
                or not source['source_url'].startswith('https://')
                or not re.fullmatch('[0-9a-f]{64}', source['snapshot']['sha256'])
                or source['snapshot']['bytes'] <= 0 or not source['paragraphs']
                or source['review'].get('paragraph_boundaries_verified') is not True):
            raise ValueError(f"Invalid/unreviewed official web source: {source['id']}")
        if source.get('reader_scope') not in (None, 'archive'):
            raise ValueError(f"Invalid web reader scope: {source['id']}")
        assets = source['assets']
        if len({a['asset_url'] for a in assets}) != len(assets):
            raise ValueError(f"Duplicate native web asset: {source['id']}")
        for asset in assets:
            if (not asset['asset_url'].startswith('https://') or asset.get('visual_review') is not True
                    or not re.fullmatch('[0-9a-f]{64}', asset['asset_sha256'])
                    or asset['role'] not in {'architecture', 'results', 'safety_evaluation', 'example', 'overview'}):
                raise ValueError(f"Invalid/unreviewed native web asset: {source['id']}")
    return {s['id']: s for s in sources}


def local_path(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Web source path escapes project: {value}')
    return path


def verify_snapshot(root, source):
    snapshot = source['snapshot']
    data = local_path(root, snapshot['path']).read_bytes()
    if digest(data) != snapshot['sha256'] or len(data) != snapshot['bytes']:
        raise ValueError(f"Changed HTML snapshot: {source['id']}")
    parser = VisibleText()
    parser.feed(data.decode('utf-8'))
    visible = normalize(''.join(parser.parts))
    for paragraph in source['paragraphs']:
        if normalize(paragraph['text']) not in visible:
            raise ValueError(f"Passage does not match visible HTML: {source['id']}")
    for asset in source['assets']:
        for text in (asset.get('caption'), asset.get('lead_in')):
            if text and normalize(text) not in visible:
                raise ValueError(f"Caption/lead-in does not match HTML: {source['id']}")
        reference = asset.get('html_asset_reference', asset['asset_url'])
        resolved = {unquote(urljoin(source['source_url'], value)) for value in parser.asset_references}
        if (unquote(reference) not in unquote(data.decode('utf-8').replace('&amp;', '&'))
                and unquote(reference) not in resolved):
            raise ValueError(f"Asset URL not in captured HTML: {source['id']}")


def summary(source):
    text = '\n\n'.join(p['text'] for p in source['paragraphs'])
    record = dict(id=source['id'], vendor=source['vendor'], title=source['title'], models=source['models'],
                document_type=None, source_kind='html', source_pdf=None, source_url=source['source_url'],
                source_sha256=source['snapshot']['sha256'], source_version=source['retrieved_at'],
                method='reviewed_visible_html', manual_review=True, status='source_reviewed',
                source_heading=source.get('source_heading'), section_type='web_overview', pages=[],
                raw_text=text, text=text, text_sha256=digest(text.encode()),
                word_count=len(text.split()), source_fragments=source['paragraphs'],
                source_review=source['review'], review_reasons=[])
    if source.get('reader_scope'):
        record['reader_scope'] = source['reader_scope']
    return record


def validate_summary(root, report):
    source = load_sources(root).get(report['id'])
    if not source:
        raise ValueError(f"Unregistered official web source: {report['id']}")
    expected = summary(source)
    for key, value in expected.items():
        if report.get(key) != value:
            raise ValueError(f"Stale web summary {key}: {report['id']}")
    return source


def current_summaries(root, models):
    active = {(m['vendor'], m['model']) for m in models if m.get('lifecycle', 'active') == 'active'
              and (m.get('latest_categories') or m.get('frontier_categories'))}
    reports = []
    for source in load_sources(root).values():
        if source.get('reader_scope') == 'archive' or any((source['vendor'], name) in active for name in source['models']):
            verify_snapshot(root, source)
            reports.append(summary(source))
    return reports


def validate_figures(root, report, exported):
    source = validate_summary(root, report)
    figures = exported['figures'] if exported else []
    if len(figures) != len(source['assets']):
        raise ValueError(f"Incomplete native web asset export: {report['id']}")
    for asset, figure in zip(source['assets'], figures):
        expected = dict(asset_url=asset['asset_url'], asset_sha256=asset['asset_sha256'],
                        role=asset['role'], caption=asset.get('caption', ''), alt=asset.get('alt', ''),
                        lead_in=asset.get('lead_in', ''), png_size=asset['dimensions'],
                        source_kind=asset.get('source_kind', 'image'))
        if any(figure.get(k) != v for k, v in expected.items()):
            raise ValueError(f"Stale native web asset export: {report['id']}")
        if figure.get('page') is not None or figure.get('bbox') is not None or figure.get('pdf_path'):
            raise ValueError(f"Fabricated PDF provenance: {report['id']}")
        if asset.get('display_background') and figure.get('transform') != 'alpha_composite:' + asset['display_background']:
            raise ValueError(f"Changed web asset display transform: {report['id']}")


def export_figures(root, output, report, selection):
    from PIL import Image
    source = validate_summary(root, report)
    verify_snapshot(root, source)
    if selection['source_sha256'] != report['source_sha256'] or selection['figures'] != source['assets']:
        raise ValueError(f"Stale native web asset selection: {report['id']}")
    record = {k: report[k] for k in ('id', 'vendor', 'title', 'models', 'document_type', 'source_kind',
                                   'source_pdf', 'source_url', 'source_sha256', 'source_version')}
    record.update(status='available' if source['assets'] else 'no_native_static_figure_available',
                  inspected_pages=[], reason_en=selection.get('reason_en', ''),
                  reason_cn=selection.get('reason_cn', ''), figures=[])
    folder = output / report['vendor'] / report['id'].split(':', 1)[1]
    folder.mkdir(parents=True, exist_ok=True)
    for index, asset in enumerate(source['assets'], 1):
        original = local_path(root, asset['local_path'])
        if digest(original.read_bytes()) != asset['asset_sha256'] or asset.get('visual_review') is not True:
            raise ValueError(f"Changed/unreviewed native web asset: {original}")
        target = folder / f'figure-{index:02d}.png'
        with Image.open(original) as image:
            if list(image.size) != asset['dimensions']:
                raise ValueError(f'Native asset dimensions changed: {original}')
            if asset.get('display_background'):
                background = Image.new('RGBA', image.size, asset['display_background'])
                background.alpha_composite(image.convert('RGBA'))
                background.convert('RGB').save(target)
                transform = 'alpha_composite:' + asset['display_background']
            elif image.format == 'PNG':
                shutil.copyfile(original, target)
                transform = 'original_bytes'
            else:
                image.convert('RGB').save(target)
                transform = 'lossless_png_from_decoded_pixels'
        record['figures'].append(dict(page=None, bbox=None, figure_number=asset.get('figure_number'),
            role=asset['role'], source_kind=asset.get('source_kind', 'image'), caption=asset.get('caption', ''),
            alt=asset.get('alt', ''), lead_in=asset.get('lead_in', ''), asset_url=asset['asset_url'],
            asset_sha256=asset['asset_sha256'], png_size=asset['dimensions'], transform=transform,
            review_method='agent_visual_official_asset_review', png_path=str(target.relative_to(root)),
            png_sha256=digest(target.read_bytes())))
    return folder, record
