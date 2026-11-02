"""Render full-text readers with metadata, falling back to source passages."""
import hashlib
import html
import json
import re
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote

from archive_reports import DOCUMENT_TYPES, VENDORS
from model_groups import CATEGORY_GROUPS

from PIL import Image
from textfold_sources import load_document, load_textfold_index, package_path
from textfold_static import copy_static_assets, write_static_reader

REPOSITORY = 'https://github.com/UNLINEARITY/AI-Frontier'
RENDERER = Path(__file__).resolve().parents[1] / 'site/render-markdown.mjs'


def escape(value):
    return html.escape(str(value), quote=True)


def reader_path(summary):
    return str(Path(summary['markdown_path']).with_suffix('.html'))


def inject_reader_meta(body, meta, chinese):
    """Date and browse-group labels under the title; assembled from model records."""
    if not meta or not meta.get('groups') or '</h1>' not in body:
        return body
    t = lambda en, cn: cn if chinese else en
    parts = []
    if meta.get('date'):
        parts.append(f'<time datetime="{meta["date"]}">{meta["date"]}</time>')
    labels = ' / '.join(CATEGORY_GROUPS[g][1 if chinese else 0] for g in meta['groups'])
    parts.append(f'<span>{escape(labels)}</span>')
    sep = f' <span class="reader-meta-sep" aria-hidden="true">{t("·", "·")}</span> '
    line = '<p class="reader-meta">' + sep.join(parts) + '</p>'
    return body.replace('</h1>', '</h1>\n' + line, 1)


ROOT = Path(__file__).resolve().parents[1]
TYPE_LABELS_CN = {'technical_report': '技术报告', 'model_card': '模型卡', 'system_card': '系统卡'}
SOURCE_LINE = re.compile(r'^\s*<h1[^>]*>.*?</h1>\s*(?:<p>\s*<a [^>]*>[^<]*</a>\s*</p>\s*)?', re.S)


def reader_header(report, row, meta, home, prefix, chinese):
    """Title first, then the facts a reader looks for: who published it, what it is, when."""
    t = lambda en, cn: cn if chinese else en
    vendor = report.get('vendor') or report['id'].split(':', 1)[0]
    publisher = 'Z.ai / Zhipu AI' if vendor == 'zai' and not chinese else VENDORS.get(vendor, vendor)
    mark = {'qwen': 'alibaba', 'amazon': 'aws'}.get(vendor, vendor)
    logo = (f'<img class="reader-mark" src="{escape(prefix)}assets/vendors/{mark}.svg" alt="" width="28" height="28">'
            if (ROOT / f'assets/vendors/{mark}.svg').is_file() else '')
    kind = (row or {}).get('document_type') or report.get('document_type')
    kind_label = (TYPE_LABELS_CN.get(kind) if chinese else DOCUMENT_TYPES.get(kind, ('',))[0]) if kind else t('Official web page', '官方网页')
    facts = [(t('Publisher', '厂商'), f'{logo}<span>{escape(publisher)}</span>'), (t('Document', '文档类型'), escape(kind_label))]
    released, published = (meta or {}).get('date'), (row or {}).get('published_date')
    if released:
        facts.append((t('Model released', '模型发布'), f'<time datetime="{released}">{released}</time>'))
    if published and published != released:
        facts.append((t('Report date', '报告日期'), f'<time datetime="{published}">{published}</time>'))
    if (meta or {}).get('groups'):
        facts.append((t('Category', '分类'), '<span>' + escape(' / '.join(CATEGORY_GROUPS[g][1 if chinese else 0] for g in meta['groups'])) + '</span>'))
    if (row or {}).get('pages'):
        facts.append((t('Length', '篇幅'), escape(f'{row["pages"]} ' + t('pages', '页'))))
    version = (row or {}).get('version', '')
    if version.startswith('arxiv-'):
        facts.append((t('Version', '版本'), escape(version.replace('arxiv-', 'arXiv '))))
    items = ''.join(f'<div><dt>{label}</dt><dd>{value}</dd></div>' for label, value in facts)
    return (f'<div class="reader-head" id="document-header">'
            f'<h1>{escape(report["title"])}</h1>'
            f'<dl class="reader-facts">{items}</dl></div>')


def reader_navigation(nav, prefix, chinese):
    """Build-time previous/next links along the release timeline, with wrap-around."""
    if not nav:
        return ''
    t = lambda en, cn: cn if chinese else en

    def target(entry):
        return prefix + ('cn/' if chinese else '') + entry['path']

    def keys(relation):
        return 'ArrowLeft' if relation == 'prev' else 'ArrowRight'

    def link(entry, relation):
        label = t('Previous', '上一份') if relation == 'prev' else t('Next', '下一份')
        arrow = '←' if relation == 'prev' else '→'
        stamp = f'<time datetime="{escape(entry["date"])}">{escape(entry["date"])}</time>' if entry['date'] else ''
        publisher = escape(entry['publisher_cn' if chinese else 'publisher_en'])
        meta = ' <span aria-hidden="true">·</span> '.join(filter(None, [stamp, publisher]))
        return (f'<a class="reader-pager-link reader-pager-link--{relation}" href="{escape(target(entry))}" '
                f'rel="{relation}" aria-keyshortcuts="{keys(relation)}">'
                f'<span class="reader-pager-direction"><span aria-hidden="true">{arrow}</span> {escape(label)}</span>'
                f'<span class="reader-pager-title">{escape(entry["model"])}</span>'
                f'<span class="reader-pager-meta">{meta}</span></a>')

    label = escape(t('Timeline navigation', '时间线浏览'))
    return (f'<nav class="reader-pager" aria-label="{label}">'
            + '<div class="reader-pager-links">' + link(nav['prev'], 'prev') + link(nav['next'], 'next') + '</div>'
            + '</nav>')


ICONS = {
    'prev': '<path d="M15 5l-7 7 7 7"/>', 'next': '<path d="M9 5l7 7-7 7"/>',
    'home': '<path d="M4 11.5 12 5l8 6.5"/><path d="M6.5 10v9h11v-9"/>',
    'source': '<path d="M14 5h5v5"/><path d="M19 5l-8 8"/><path d="M17 14v5H5V7h5"/>',
    'github': '<path d="M9 19c-4 1.3-4-2-6-2.5m12 4.5v-3.4a3 3 0 0 0-.8-2.3c2.7-.3 5.5-1.3 5.5-6a4.6 4.6 0 0 0-1.3-3.2 4.3 4.3 0 0 0-.1-3.2s-1-.3-3.4 1.3a11.6 11.6 0 0 0-6 0C6.5 2.6 5.5 2.9 5.5 2.9a4.3 4.3 0 0 0-.1 3.2A4.6 4.6 0 0 0 4 9.3c0 4.6 2.8 5.7 5.5 6a3 3 0 0 0-.8 2.3V21"/>',
    'star': '<path d="m12 3 2.8 5.6 6.2.9-4.5 4.4 1 6.2-5.5-2.9-5.5 2.9 1-6.2L3 9.5l6.2-.9Z"/>',
}


# Must match the local level names in site/vendor/textfold/reader.js (full text first).
FOLD_LEVELS = {'en': ('Full', 'Lead', 'Gist', 'Skim', 'Peek'), 'zh': ('全文', '首句', '重点', '速读', '关键词')}


def reader_toolbar(nav, report, source_url, prefix, home, chinese, fulltext=False):
    """A bottom toolbar, symmetric around the full-text detail control:
    previous, home and official source on the left; this page on GitHub, star and next on the right."""
    t = lambda en, cn: cn if chinese else en

    def tool(kind, href, label, extra=''):
        external = ' target="_blank" rel="noopener"' if href.startswith('https://') else ''
        return (f'<a class="reader-tool reader-tool--{kind}" href="{escape(href)}"{external}{extra} aria-label="{escape(label)}" title="{escape(label)}">'
                f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[kind]}</svg><span class="reader-tool-label">{escape(label)}</span></a>')

    def step(relation):
        if not nav or not nav.get(relation):
            return ''
        entry = nav[relation]
        label = t('Previous report', '上一份报告') if relation == 'prev' else t('Next report', '下一份报告')
        href = prefix + ('cn/' if chinese else '') + entry['path']
        keys = 'ArrowLeft' if relation == 'prev' else 'ArrowRight'
        return (f'<a class="reader-tool reader-tool--step reader-tool--{relation}" href="{escape(href)}" rel="{relation}" '
                f'aria-label="{escape(label + ": " + entry["model"])}" title="{escape(label + ": " + entry["model"])}" aria-keyshortcuts="{keys}">'
                f'<svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[relation]}</svg></a>')

    start = step('prev') + tool('home', home, t('Home', '首页'), ' data-reader-home')
    if source_url:
        start += tool('source', source_url, t('Official source', '官方来源'))
    end = (tool('github', f'{REPOSITORY}/blob/main/{quote(report["markdown_path"])}', t('View on GitHub', '在 GitHub 查看本页'))
           + tool('star', REPOSITORY, t('Star', '点个 Star')) + step('next'))
    labels = FOLD_LEVELS['zh' if chinese else 'en']
    ghost = '<span class="on">' + escape(labels[0]) + '</span>' + ''.join(f'<span>{escape(label)}</span>' for label in labels[1:])
    return (f'<nav class="reader-toolbar" aria-label="{escape(t("Reading tools", "阅读工具栏"))}"><div class="reader-toolbar-bar">'
            f'<div class="reader-tools reader-tools--start">{start}</div>'
            '<div class="reader-fold-slot" aria-hidden="true">'
            # A still copy of the detail control holds its place until TextFold draws the live one on top.
            + (f'<div class="reader-fold-ghost">{ghost}</div>' if fulltext else '') + '</div>'
            f'<div class="reader-tools reader-tools--end">{end}</div></div></nav>')


def build_readers(root, output, summaries, figure_reports, catalog, reader_meta=None, reader_nav=None):
    template = (root / 'site/reader.html').read_text()
    by_pdf = {r['local_path']: r for r in catalog}
    fulltexts = load_textfold_index(root, catalog)
    full_by_pdf, full_documents = {}, {}
    if fulltexts:
        copy_static_assets(root, output)
        for record in fulltexts.values():
            doc = load_document(root, record)
            full_documents[record['id']] = (write_static_reader(root, output, record, doc), doc['chunks'])
            full_by_pdf[record['source_pdf']] = record
            for asset in record['images']:
                if asset.get('recovery') and not asset.get('visual_review'):
                    raise ValueError(f'Unreviewed TextFold recovered table: {asset["path"]}')
                target = (output / asset['site_path']).resolve()
                if not target.is_relative_to((output / 'assets/textfold-images').resolve()):
                    raise ValueError('TextFold image target escapes the website assets')
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(package_path(root, asset['path']), target)
    articles, reports, previews = [], [], {}
    for report in summaries.values():
        if report.get('source_kind') == 'html':
            from web_sources import validate_summary
            validate_summary(root, report)
        else:
            row = by_pdf.get(report['source_pdf'])
            if not row or row['sha256'] != report['source_sha256']:
                raise ValueError(f"Stale summary: {report['id']}")
        selected = figure_reports.get(report['id'])
        if selected and selected['source_sha256'] != report['source_sha256']:
            raise ValueError(f"Stale figure selection: {report['id']}")
        if report.get('source_kind') == 'html':
            from web_sources import validate_figures
            validate_figures(root, report, selected)
        markdown_path = root / report['markdown_path']
        images = {}
        for figure in selected['figures'] if selected else []:
            source = root / figure['png_path']
            if hashlib.sha256(source.read_bytes()).hexdigest() != figure['png_sha256']:
                raise ValueError(f'Figure checksum mismatch: {source}')
            relative = Path('assets') / Path(figure['png_path']).with_suffix('.webp')
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(source) as image:
                image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
                image.save(target, 'WEBP', quality=92, method=6)
                size = image.size
            previews[figure['png_path']] = relative.as_posix()
            href = Path(os.path.relpath(source, markdown_path.parent)).as_posix()
            images[href] = dict(preview=relative.as_posix(), width=size[0], height=size[1],
                                full=REPOSITORY + '/raw/refs/heads/main/' + quote(figure['png_path']))
        articles.append(dict(markdown=markdown_path.read_text(), markdown_path=report['markdown_path'],
                             repository=REPOSITORY, images=images))
        reports.append(report)
    rendered = json.loads(subprocess.run(['node', str(RENDERER)], input=json.dumps(articles),
                                        text=True, capture_output=True, check=True).stdout)
    for report, body in zip(reports, rendered, strict=True):
        vendor, slug = report['id'].split(':', 1)
        meta = (reader_meta or {}).get(slug, {})
        for chinese in (False, True):
            t = lambda en, cn: cn if chinese else en
            path = Path(('cn/' if chinese else '') + reader_path(report))
            prefix = '../' * (len(path.parts) - 1)
            home = prefix + ('cn/index.html' if chinese else 'index.html')
            fulltext = full_by_pdf.get(report.get('source_pdf'))
            contents, fulltext_section = '', ''
            if fulltext:
                full_path, chunks = full_documents[fulltext['id']]
                entries = []
                for chunk in chunks:
                    heading = ' '.join(filter(None, [chunk.get('num'), chunk.get('title')]))
                    if not heading:
                        heading = t('Opening', '开篇')
                    entries.append(f'<li class="toc-depth-{min(4, max(1, int(chunk.get("level", 2))-1))}">'
                                   f'<a href="#{escape(chunk["id"])}" '
                                   f'data-fold-section="{escape(chunk["id"])}">{escape(heading)}</a></li>')
                contents = (f'<details class="reader-toc" id="contents"><summary>{t("Contents", "目录")} '
                            f'<span>({len(chunks)})</span></summary><ol>{"".join(entries)}</ol></details>')
                fulltext_section = (
                    f'<section id="fulltext" class="textfold-inline" data-textfold-inline '
                    f'data-ui="{t("en", "zh")}" data-document="{escape(prefix + str(Path(full_path).with_suffix(".tfd")))}" '
                    f'data-assets="{escape(prefix)}assets/textfold/" aria-label="{t("Full text", "全文")}" aria-busy="true">'
                    f'<p class="textfold-loading">{t("Loading full text…", "正在载入全文…")}</p>'
                    f'<noscript><p><a href="{escape(fulltext["source_url"])}">'
                    f'{t("Read the official report", "阅读官方报告")}</a></p></noscript></section>'
                    f'<script src="{escape(prefix)}assets/textfold/inline.js" defer></script>')
            values = {
                'lang': t('en', 'zh-CN'), 'prefix': prefix, 'home': home,
                'reports_home': prefix + ('cn/reports.html' if chinese else 'reports.html'),
                'switch': prefix + ('' if chinese else 'cn/') + reader_path(report),
                'switch_label': t('Switch to 中文', '切换至 English'), 'name': 'AI Frontier', 'repository': REPOSITORY,
                'switch_compact': t('EN → 中', '中 → EN'),
                'title': escape(report['title']), 'description': escape(report['title']),
                'reader_head': reader_header(report,
                                             by_pdf.get(report.get('source_pdf')), meta, home, prefix, chinese),
                # The summary keeps its own passage; its title and source line now live in the header.
                'reader_body': '' if fulltext else
                    f'<article class="markdown-body" id="summary">{SOURCE_LINE.sub("", body.replace("{{asset_prefix}}", prefix), count=1)}</article>',
                'vendor': vendor,
                'reader_class': ' reader--fulltext' if fulltext else '',
                'reader_contents': contents, 'fulltext_section': fulltext_section,
                'reader_nav': reader_navigation(reader_nav.get(report['id']) if reader_nav else None, prefix, chinese),
                'reader_toolbar': reader_toolbar(reader_nav.get(report['id']) if reader_nav else None, report,
                                                 (fulltext or report).get('source_url') or report.get('source_url'), prefix, home, chinese,
                                                 bool(fulltext)),
                'back': t('Back', '返回'), 'zoom': t('Figure', '图片'), 'close': t('Close', '关闭'),
                'theme_label': t('Appearance', '外观'), 'light_theme': t('Light', '浅色'),
                'dark_theme': t('Dark', '深色'), 'system_theme': t('System', '跟随系统'),
                'star': t('Star on GitHub', '给项目点个 Star'), 'skip': t('Skip to content', '跳到内容'),
                'top': t('Back to top', '回到顶部'),
            }
            page = template
            for key, value in values.items():
                page = page.replace('{{' + key + '}}', value)
            target = output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page, encoding='utf-8')
            # Keep previously shared reading URLs usable without another content copy.
            previous = output / ('cn/' if chinese else '') / f'read/{vendor}/{slug}/index.html'
            previous.parent.mkdir(parents=True, exist_ok=True)
            redirect = Path(os.path.relpath(target, previous.parent)).as_posix()
            previous.write_text(f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={escape(redirect)}"><a href="{escape(redirect)}">{escape(report["title"])}</a>\n')
    return len(reports) * 2, len(previews)
