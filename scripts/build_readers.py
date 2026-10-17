"""Render the existing abstracts Markdown with inline figure previews."""
import hashlib
import html
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import quote

from model_groups import CATEGORY_GROUPS

from PIL import Image

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


def reader_navigation(nav, prefix, chinese):
    """Build-time previous/next links along the release timeline, with wrap-around."""
    if not nav:
        return ''
    t = lambda en, cn: cn if chinese else en

    def target(entry):
        return prefix + ('cn/' if chinese else '') + entry['path']

    def keys(relation):
        return 'ArrowLeft' if relation == 'prev' else 'ArrowRight'

    def step(entry, relation):
        label = t('Previous report', '上一份报告') if relation == 'prev' else t('Next report', '下一份报告')
        hint = escape(f'{label}: {entry["model"]}')
        rotation = 'M15 5l-7 7 7 7' if relation == 'prev' else 'M9 5l7 7-7 7'
        return (f'<a class="reader-step reader-step--{relation}" href="{escape(target(entry))}" rel="{relation}" '
                f'aria-label="{hint}" title="{hint}" aria-keyshortcuts="{keys(relation)}">'
                f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="{rotation}"/></svg></a>')

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
            + step(nav['prev'], 'prev') + step(nav['next'], 'next')
            + '<div class="reader-pager-links">' + link(nav['prev'], 'prev') + link(nav['next'], 'next') + '</div>'
            + '</nav>')


def build_readers(root, output, summaries, figure_reports, catalog, reader_meta=None, reader_nav=None):
    template = (root / 'site/reader.html').read_text()
    by_pdf = {r['local_path']: r for r in catalog}
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
            values = {
                'lang': t('en', 'zh-CN'), 'prefix': prefix, 'home': home,
                'reports_home': prefix + ('cn/reports.html' if chinese else 'reports.html'),
                'switch': prefix + ('' if chinese else 'cn/') + reader_path(report),
                'switch_label': t('Switch to 中文', '切换至 English'), 'name': 'AI Frontier', 'repository': REPOSITORY,
                'switch_compact': t('EN → 中', '中 → EN'),
                'title': escape(report['title']), 'description': escape(report['title']),
                'body': inject_reader_meta(body.replace('{{asset_prefix}}', prefix), meta, chinese), 'vendor': vendor,
                'reader_nav': reader_navigation(reader_nav.get(report['id']) if reader_nav else None, prefix, chinese),
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
