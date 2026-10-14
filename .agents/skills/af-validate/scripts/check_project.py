#!/usr/bin/env python3
"""Read-only project validation, independent of PDF/parsing dependencies."""
import argparse
import ast
import csv
import hashlib
import json
import math
import os
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'scripts'))
from web_sources import validate_summary, validate_figures, verify_snapshot

SHA = re.compile(r'^[0-9a-f]{64}$')
MD_LINK = re.compile(r'!?\[[^\]\n]*\]\(([^\s\)]+)\)')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vocabulary(root):
    tree = ast.parse((root / 'scripts/archive_reports.py').read_text())
    names = {'VENDORS', 'DOCUMENT_TYPES', 'MODEL_CATEGORIES'}
    return {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
            if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in names}


def repository_pdf(url):
    parsed = urlsplit(url)
    return (parsed.hostname in {'github.com', 'raw.githubusercontent.com'}
            and parsed.path.lower().startswith('/unlinearity/ai-frontier/')
            and parsed.path.lower().endswith('.pdf'))


def validate(root, site=None, local_pdfs=False):
    root = root.resolve()
    site = site.resolve() if site else None
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)
    def local(value):
        path = (root / value).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f'Path escapes project: {value}')
        return path
    def load(name):
        return json.loads(local(name).read_text())
    vocab = vocabulary(root)
    vendors, types, categories = (vocab[n] for n in ('VENDORS', 'DOCUMENT_TYPES', 'MODEL_CATEGORIES'))
    sources = load('sources.json')
    source_ids = [(s['vendor'], s['slug']) for s in sources]
    require(len(set(source_ids)) == len(source_ids), 'Duplicate publisher/report slug in sources.json')
    for source in sources:
        require(source['vendor'] in vendors and source['document_type'] in types, f'Unknown source publisher/type: {source["slug"]}')
        require(bool(source.get('source_url')), f'Missing official source: {source["slug"]}')
    coverage = load('model-coverage.json')
    latest = {}
    for model in coverage['models']:
        name = model['model']
        require(model['vendor'] in vendors, f'Unknown model publisher: {name}')
        for slug in model.get('report_slugs', []):
            require((model['vendor'], slug) in source_ids, f'Unregistered model report: {name}: {slug}')
        for category in model.get('latest_categories', []) + model.get('frontier_categories', []):
            require(category in categories, f'Unknown model category: {name}: {category}')
        if model.get('lifecycle', 'active') != 'active':
            require(bool(model.get('lifecycle_source_url')), f'Missing lifecycle evidence: {name}')
            continue
        for category in model.get('latest_categories', []):
            slot = (model['vendor'], category)
            require(slot not in latest, f'Duplicate active latest slot: {slot}')
            latest[slot] = name
    with local('catalog.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    catalog = {}
    for row in rows:
        if row['status'] != 'archived':
            continue
        name = row['local_path']
        require(name not in catalog, f'Duplicate archived path: {name}')
        require(bool(SHA.fullmatch(row['sha256'])), f'Invalid catalog checksum: {name}')
        catalog[name] = row
        if local_pdfs:
            path = local(name)
            require(path.is_file() and sha(path) == row['sha256'], f'Missing/changed local source PDF: {name}')
    reports = load('abstracts/index.json')['reports']
    figures = load('figures/index.json')['reports']
    selections = load('figures/selections.json')
    ids = [r['id'] for r in reports]
    figure_ids = [r['id'] for r in figures]
    selection_ids = [s['id'] for s in selections]
    require(len(set(ids)) == len(ids), 'Duplicate source-summary ID')
    require(len(set(figure_ids)) == len(figure_ids) and set(figure_ids) == set(ids), 'Figure records do not match source summaries')
    require(len(set(selection_ids)) == len(selection_ids) and set(selection_ids) == set(ids), 'Selections do not match source summaries')
    figure_lookup = {r['id']: r for r in figures}
    selection_lookup = {s['id']: s for s in selections}
    count = 0
    for report in reports:
        key = report['id']
        web = report.get('source_kind') == 'html'
        row = catalog.get(report['source_pdf'])
        web_source = None
        if web:
            try:
                web_source = validate_summary(root, report)
                if local(web_source['snapshot']['path']).exists():
                    verify_snapshot(root, web_source)
            except (ValueError, OSError) as error:
                require(False, str(error))
        else:
            require(bool(row) and row['sha256'] == report['source_sha256'], f'Stale summary source: {key}')
        if row:
            require(all(isinstance(p, int) and 1 <= p <= int(row['pages']) for p in report['pages']), f'Invalid summary source pages: {key}')
        require((not report['text'] and report['text_sha256'] is None) or sha_text(report['text']) == report['text_sha256'], f'Changed source-summary text checksum: {key}')
        require(report['status'] in {'cross_checked', 'source_reviewed', 'no_summary_identified'}, f'Unresolved source-summary review: {key}')
        if report['status'] == 'source_reviewed':
            require(bool(report.get('source_review')), f'Missing source review record: {key}')
        markdown = local(report['markdown_path'])
        require(markdown.is_file(), f'Missing source Markdown: {key}')
        text = markdown.read_text() if markdown.exists() else ''
        require(' '.join(report['text'].split()) in ' '.join(text.split()), f'Source passage missing from Markdown: {key}')
        exported, selected = figure_lookup.get(key), selection_lookup.get(key)
        if not exported or not selected:
            continue
        require(exported['source_sha256'] == selected['source_sha256'] == report['source_sha256'], f'Stale figure source: {key}')
        require(len(exported['figures']) == len(selected['figures']), f'Export/selection count differs: {key}')
        if web:
            require(web_source is not None and selected['figures'] == web_source['assets'], f'Stale web asset selection: {key}')
            try:
                validate_figures(root, report, exported)
            except ValueError as error:
                require(False, str(error))
        for figure, selection in zip(exported['figures'], selected['figures']):
            count += 1
            require(selection.get('visual_review') is True, f'Missing visual figure review: {key}')
            if web:
                require(web_source is not None and selected['figures'] == web_source['assets'], f'Stale web asset selection: {key}')
                require(figure.get('page') is None and figure.get('bbox') is None and not figure.get('pdf_path'), f'Fabricated PDF provenance: {key}')
                for field in ('asset_url', 'asset_sha256', 'role', 'caption'):
                    require(figure.get(field, '') == selection.get(field, ''), f'Web asset export differs: {key}: {field}')
                if local(selection['local_path']).exists():
                    require(sha(local(selection['local_path'])) == selection['asset_sha256'], f'Changed original web asset: {key}')
            else:
                require(figure['bbox'] == selection['bbox'] and figure['page'] == selection['page'], f'Export differs from selected region: {key}')
                require(row is not None and 1 <= figure['page'] <= int(row['pages']), f'Invalid figure source page: {key}')
                require(all(math.isfinite(x) for x in figure['bbox']), f'Invalid figure rectangle: {key}')
            image = local(figure['png_path'])
            require(image.is_file() and sha(image) == figure['png_sha256'], f'Missing/changed PNG: {figure["png_path"]}')
            require(' '.join(figure['caption'].split()) in ' '.join(text.split()), f'Original caption missing from Markdown: {key}')
            reference = Path(os.path.relpath(image, markdown.parent)).as_posix()
            require(f']({reference})' in text, f'Figure is not embedded in source Markdown: {key}')
            if local_pdfs and not web:
                pdf = local(figure['pdf_path'])
                require(pdf.is_file() and sha(pdf) == figure['pdf_sha256'], f'Missing/changed local cropped PDF: {figure["pdf_path"]}')
    public = [root / n for n in ('README.md', 'README_CN.md', 'LATEST_MODELS.md', 'LATEST_MODELS_CN.md')]
    for folder in ('abstracts', 'figures', 'pdfs', 'reports'):
        public.extend((root / folder).rglob('*.md'))
    for path in public:
        if not path.exists():
            continue
        for url in MD_LINK.findall(path.read_text()):
            url = url.strip('<>')
            parsed = urlsplit(url)
            require(not repository_pdf(url), f'Public repository PDF link: {path}: {url}')
            if parsed.scheme or url.startswith('#'):
                continue
            target = (path.parent / unquote(parsed.path)).resolve()
            require(target.is_relative_to(root) and target.exists(), f'Broken Markdown link: {path}: {url}')
            require(target.suffix.lower() != '.pdf', f'Public local PDF link: {path}: {url}')
    git = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'], capture_output=True, text=True)
    if git.returncode == 0 and Path(git.stdout.strip()).resolve() == root:
        tracked = subprocess.check_output(['git', '-C', str(root), 'ls-files', '-z']).decode().split('\0')
        for name in tracked:
            require(not name.lower().endswith('.pdf'), f'PDF entered Git: {name}')
            require(name not in {'log.md', 'git-log.md', 'assets/branding/prompt.md', 'assets/branding/metadata.json'}
                    and not name.startswith('.cache/') and 'node_modules/' not in name, f'Private/cache file entered Git: {name}')
    if site:
        require((site / 'index.html').is_file() and (site / 'cn/index.html').is_file(), 'Both language homepages are required')
        require(not any(p.suffix.lower() == '.pdf' for p in site.rglob('*') if p.is_file()), 'Pages artifact contains a PDF')
        for path in site.rglob('*.html'):
            parser = SiteLinks()
            parser.feed(path.read_text())
            for url in parser.urls:
                parsed = urlsplit(url)
                require(not repository_pdf(url), f'Website repository PDF link: {path}: {url}')
                if parsed.scheme or url.startswith('#'):
                    continue
                target = (path.parent / unquote(parsed.path)).resolve()
                require(target.is_relative_to(site) and target.exists(), f'Broken website link: {path}: {url}')
    return errors, dict(reports=len(catalog), summaries=len(reports), figures=count, latest_slots=len(latest))


def sha_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


class SiteLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attributes):
        self.urls.extend(value for key, value in attributes if key in {'href', 'src'} and value)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--site', type=Path)
    parser.add_argument('--local-pdfs', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    site = (root / args.site).resolve() if args.site else None
    try:
        errors, counts = validate(root, site, args.local_pdfs)
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f'Validation could not complete: {error}\n')
    for error in errors:
        print(f'FAIL: {error}')
    if errors:
        parser.exit(1)
    print('PASS: ' + ', '.join(f'{key}={value}' for key, value in counts.items()))
