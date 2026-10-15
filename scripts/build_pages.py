"""Build a small bilingual Pages site from the archive's curated data."""
import argparse
import csv
import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

from PIL import Image

from build_readers import build_readers, reader_path
from archive_reports import DOCUMENT_TYPES, MODEL_CATEGORIES, VENDORS
from model_timeline import timeline_models

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/UNLINEARITY/AI-Frontier'
SITE_URL = 'https://unlinearity.github.io/AI-Frontier'
ICON_FILES = ('favicon.svg', 'favicon.ico', 'apple-touch-icon.png')
TYPE_LABELS_CN = {'technical_report': '技术报告', 'model_card': '模型卡', 'system_card': '系统卡'}
MARKS = {v: {'qwen': 'alibaba', 'amazon': 'aws'}.get(v, v) for v in VENDORS}

NOT_FOUND_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found — AI Frontier</title><meta name="robots" content="noindex"><meta name="theme-color" content="#09121e">
<link rel="icon" href="__SITE__/favicon.svg" type="image/svg+xml"><link rel="icon" href="__SITE__/favicon.ico" sizes="32x32"><link rel="apple-touch-icon" href="__SITE__/apple-touch-icon.png">
<style>
:root{color-scheme:light dark;--bg:#f6f8fb;--ink:#172c3d;--muted:#526779;--accent:#106f64;--line:#d5dfe8}
@media(prefers-color-scheme:dark){:root{--bg:#09121e;--ink:#edf4fa;--muted:#94a9ba;--accent:#65dfcc;--line:#263747}}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:grid;place-items:center;padding:32px;background:var(--bg);color:var(--ink);font:16px/1.7 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{width:100%;max-width:640px}
p.eyebrow{margin:0 0 10px;font-size:12px;letter-spacing:.14em;color:var(--accent);font-weight:600}
h1{margin:0 0 16px;font-size:clamp(26px,5vw,38px);line-height:1.25;letter-spacing:-.6px}
p{margin:0 0 14px;color:var(--muted)}
p.zh{color:var(--ink)}
nav{display:flex;flex-wrap:wrap;gap:10px;margin-top:26px}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
a.primary{background:var(--accent);color:var(--bg);padding:11px 18px;border-radius:9px;font-weight:600}
a.plain{border:1px solid var(--line);padding:11px 18px;border-radius:9px;color:var(--ink)}
hr{border:0;border-top:1px solid var(--line);margin:30px 0}
</style>
</head>
<body>
<main>
<p class="eyebrow">404</p>
<h1>This page is not part of the archive.</h1>
<p>AI Frontier indexes official publisher documents; it does not host report files. Start from the archive home, or search the collection for the report you need.</p>
<p class="zh" lang="zh-CN">这个页面不在档案中。档案只索引发布方的官方文档，不存放报告文件。请从首页进入，或在首页搜索你需要的报告。</p>
<nav><a class="primary" href="__SITE__/">Back to the archive</a><a class="plain" href="__SITE__/cn/">返回中文首页</a></nav>
<hr>
<p>Every entry in the <a href="__SITE__/">collection</a> links to its official source.</p>
</main>
</body>
</html>
"""


def escape(value):
    return html.escape(str(value), quote=True)


def link(url, label):
    attributes = ' target="_blank" rel="noopener"' if str(url).startswith('http') else ''
    return f'<a href="{escape(url)}"{attributes}>{escape(label)}</a>'


def card_link_attributes(target):
    return ' target="_blank" rel="noopener"' if str(target).startswith('http') else ''


def card_link_mark(target):
    return '<span class="external-mark" aria-hidden="true">↗</span>' if str(target).startswith('http') else ''


def card_link_hint(target, chinese):
    if not str(target).startswith('http'):
        return ''
    return '<span class="sr-only">' + ('（在新标签页打开）' if chinese else '(opens in a new tab)') + '</span>'


def lab_count(report_total, model_total, chinese):
    segments = []
    if report_total:
        segments.append(f'{report_total} ' + ('份报告' if chinese else ('report' if report_total == 1 else 'reports')))
    if model_total:
        segments.append(f'{model_total} ' + ('个模型' if chinese else ('model' if model_total == 1 else 'models')))
    if not segments:
        segments.append('无记录' if chinese else 'No records')
    return '<span class="lab-count">' + ''.join(f'<span>{segment}</span>' for segment in segments) + '</span>'


def publisher_mark(vendor, prefix='', loading='lazy'):
    filename = f'{MARKS[vendor]}.svg'
    if not (ROOT / 'assets/vendors' / filename).is_file():
        return ''
    return f'<img class="publisher-mark" src="{prefix}assets/vendors/{filename}" alt="" loading="{loading}">'


def report_target(row, summaries):
    summary = summaries.get(row['local_path'])
    if summary and summary['source_sha256'] == row['sha256']:
        return reader_path(summary)
    return row['source_url']


def model_documents(model, reports, sources, summaries):
    documents = []
    for slug in model.get('report_slugs', []):
        source = sources[(model['vendor'], slug)]
        archived = [r for r in reports if r['vendor'] == model['vendor'] and r['title'] == source['title']]
        if archived:
            row = max(archived, key=lambda r: (r['source_updated_date'], r['retrieved_at']))
            summary = summaries.get(row['local_path'])
            available = summary and summary['source_sha256'] == row['sha256']
            documents.append((not bool(available), list(DOCUMENT_TYPES).index(row['document_type']),
                              report_target(row, summaries), source['title']))
        elif source.get('pdf_url'):
            documents.append((True, list(DOCUMENT_TYPES).index(source['document_type']), source['source_url'], source['title']))
    return sorted(documents, key=lambda d: d[:2])


def model_target(model, documents, web_readers):
    if documents and documents[0][0] is False:
        return documents[0][2]
    for name in [model['model']] + model.get('reading_aliases', []):
        if (model['vendor'], name) in web_readers:
            return reader_path(web_readers[(model['vendor'], name)])
    if documents:
        return documents[0][2]
    return model.get('frontier_source_url', model['source_url'])


def current_model_keys(models, history):
    aliases = {(entry['vendor'], entry['coverage_model'].casefold()): entry['models']
               for entry in history.get('coverage_aliases', [])}
    return {(model['vendor'], name.casefold()) for model in models
            for name in aliases.get((model['vendor'], model['model'].casefold()), [model['model']])}


def model_card(model, target, labels, current_keys, chinese, prefix):
    categories = [key for key in MODEL_CATEGORIES if key in model.get('categories', [])]
    category_text = ' / '.join(MODEL_CATEGORIES[key][int(chinese)] for key in categories)
    search = ' '.join([model['model'], labels[model['vendor']]] + model.get('search_aliases', []))
    current = (model['vendor'], model['model'].casefold()) in current_keys
    date = model['release_date']
    date_markup = f'<time datetime="{date}">{date}</time>' if date else ('日期待确认' if chinese else 'Date unconfirmed')
    return (f'<article class="card model-row" data-vendor="{model["vendor"]}" data-category="{escape(" ".join(categories))}" '
            f'data-frontier="{int(current)}" data-date="{date}" data-title="{escape(model["model"])}" data-search="{escape(search)}">'
            f'<div class="card-heading"><div class="publisher">{publisher_mark(model["vendor"], prefix)}'
            f'<span>{escape(labels[model["vendor"]])}</span></div></div>'
            f'<h2><a class="card-link" href="{escape(target)}"{card_link_attributes(target)}>{escape(model["model"])}'
            f'{card_link_mark(target)}{card_link_hint(target, chinese)}</a></h2>'
            f'<p class="date">{date_markup}</p><p class="model-category">{escape(category_text)}</p></article>')


def hero_heading(text, chinese):
    # Preserve the brand words, with breaks at phrase boundaries instead of inside them.
    separator = '官方报告档案' if chinese else 'behind frontier AI'
    position = text.find(separator)
    lines = [text[:position].strip(), text[position:].strip()] if position > 0 else [text]
    return '\n'.join(f'<span class="headline-line"><span data-motion="headline" data-delay="{index * 90}">{escape(line)}</span></span>'
                   for index, line in enumerate(lines))


def write_robots(output):
    (output / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n', encoding='utf-8')


def write_sitemap(output, readers):
    locations = {f'{SITE_URL}/', f'{SITE_URL}/cn/', f'{SITE_URL}/models.html', f'{SITE_URL}/cn/models.html',
                 f'{SITE_URL}/reports.html', f'{SITE_URL}/cn/reports.html'}
    for summary in readers.values():
        path = quote(reader_path(summary), safe='/')
        locations.update({f'{SITE_URL}/{path}', f'{SITE_URL}/cn/{path}'})
    entries = ''.join(f'  <url><loc>{escape(location)}</loc></url>\n' for location in sorted(locations))
    (output / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                        + entries + '</urlset>\n', encoding='utf-8')


def write_not_found(output):
    (output / '404.html').write_text(NOT_FOUND_PAGE.replace('__SITE__', SITE_URL), encoding='utf-8')


def cadence_plate(timeline, chinese):
    """A real fragment of this archive's own interface: dated models per quarter."""
    quarters = {}
    for model in timeline:
        if not model['release_date']:
            continue
        year, month = int(model['release_date'][:4]), int(model['release_date'][5:7])
        key = year * 4 + (month - 1) // 3
        quarters[key] = quarters.get(key, 0) + 1
    if not quarters:
        return ''
    keys = list(range(min(quarters), max(quarters) + 1))
    top = max(quarters.values())
    width, height, plot = 760, 260, 216
    step = width / len(keys)
    bars, labels = [], []
    for index, key in enumerate(keys):
        count = quarters.get(key, 0)
        bar = plot * count / top
        bars.append(f'<rect x="{index * step + 1.5:.1f}" y="{plot - bar:.1f}" width="{step - 3:.1f}" '
                    f'height="{max(bar, 1.5):.1f}" fill="var(--accent)" opacity="{0.3 + 0.7 * count / top:.2f}"></rect>')
        if key % 4 == 0:
            labels.append(f'<text x="{index * step:.1f}" y="{height - 12}" fill="var(--muted)" font-size="12">{key // 4}</text>')
    busiest = max(quarters, key=quarters.get)
    reading = (f'{busiest // 4} 年第 {busiest % 4 + 1} 季度最多：{quarters[busiest]} 个模型'
               if chinese else
               f'Busiest quarter: Q{busiest % 4 + 1} {busiest // 4}, {quarters[busiest]} models')
    return (f'<div class="ui-row"><b>{"模型发布节奏" if chinese else "Release cadence"}</b>'
            f'<span class="ui-muted">{reading}</span></div>'
            f'<svg class="ui-plot" viewBox="0 0 {width} {height}" role="img" aria-label="{"按季度的模型发布数" if chinese else "models released per quarter"}">'
            + ''.join(bars) + ''.join(labels) + '</svg>')


def showcase_input(report, chinese):
    """A real catalog record, laid out like the cover metadata of the report itself."""
    rows = [
        ('报告' if chinese else 'Report', escape(report['title'])),
        ('发布方' if chinese else 'Publisher', escape(VENDORS[report['vendor']])),
        ('类型' if chinese else 'Type', escape(TYPE_LABELS_CN[report['document_type']] if chinese else DOCUMENT_TYPES[report['document_type']][0])),
        ('日期' if chinese else 'Date', escape(report['published_date'] or '—')),
        ('页数' if chinese else 'Pages', f'{report["pages"]} ' + ('页' if chinese else 'pages')),
        ('版本' if chinese else 'Version', escape(report['version'] or '—')),
    ]
    body = ''.join(f'<div class="ui-row"><span class="ui-muted">{label}</span><b>{value}</b></div>' for label, value in rows)
    return body + f'<div class="ui-row" style="margin-top:10px"><span class="ui-muted">{"官方来源" if chinese else "Official source"}</span><b>{escape(report["source_url"])}</b></div>'


def showcase_output(reader, figure, chinese):
    """A real reading page fragment: opening passage, figure caption, printed page number."""
    passage = ' '.join((reader.get('text') or '').split())
    if len(passage) > 200:
        passage = passage[:200].rsplit(' ', 1)[0] + '…'
    items = [f'<div class="showcase-fig"><small>{"原文概要" if chinese else "Source passage"}</small><b>{escape(passage) or "—"}</b></div>']
    if figure:
        items.append(f'<div class="showcase-fig"><small>{"原图注" if chinese else "Original caption"}</small><b>{escape(figure.get("caption") or "")}</b>'
                     f'<small>p. {figure.get("page")}</small></div>')
    items.append(f'<div class="showcase-fig"><small>{"阅读页" if chinese else "Reading page"}</small>'
                 f'<b>{escape(reader_path(reader))}</b></div>')
    return ''.join(items)


def publisher_tiles(timeline, reports, labels, chinese, prefix):
    """A complete publisher index; every tile is a direct selection, including ALL."""
    tiles = (f'<a class="publisher-tile publisher-tile--all" href="models.html" data-publisher="" data-motion="publisher">'
             f'<span class="tile-name">ALL</span>{lab_count(len(reports), len(timeline), chinese)}</a>')
    tones = ('paper', 'ink', 'accent', 'soft')
    for index, (vendor, label) in enumerate(labels.items()):
        report_count = sum(record['vendor'] == vendor for record in reports)
        model_count = sum(model['vendor'] == vendor for model in timeline)
        tiles += (f'<a class="publisher-tile publisher-tile--{tones[index % len(tones)]}" href="models.html?publisher={vendor}" data-publisher="{vendor}" '
                  f'data-label="{escape(label.split(" / ")[0])}" data-motion="publisher">'
                  f'<span class="tile-brand">{publisher_mark(vendor, prefix, "eager")}'
                  f'<span class="tile-name">{escape(label.split(" / ")[0])}</span></span>'
                  f'{lab_count(report_count, model_count, chinese)}</a>')
    return tiles


def proof_table(reports, models, readers, chinese):
    """Where every document came from: counts, newest document and collection link per publisher."""
    by_vendor = {}
    for row in reports:
        by_vendor.setdefault(row['vendor'], []).append(row)
    model_counts = {}
    for model in models:
        model_counts[model['vendor']] = model_counts.get(model['vendor'], 0) + 1
    rows = []
    for vendor, group in sorted(by_vendor.items(), key=lambda item: -len(item[1]))[:12]:
        newest = max(group, key=lambda row: row['published_date'])
        collection = f'{REPOSITORY}/blob/main/pdfs/{vendor}/README.md'
        rows.append('<tr>'
                    f'<td>{escape(VENDORS[vendor])}</td>'
                    f'<td data-label="{"报告" if chinese else "Reports"}">{len(group)}</td>'
                    f'<td data-label="{"前沿模型" if chinese else "Frontier models"}">{model_counts.get(vendor, 0)}</td>'
                    f'<td data-label="{"最新一份" if chinese else "Newest"}">{escape(newest["published_date"] or "—")}</td>'
                    f'<td data-label="{"档案目录" if chinese else "Collection"}">{link(collection, "目录" if chinese else "index")}</td>'
                    '</tr>')
    return ''.join(rows)


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((ROOT / 'catalog.csv').open(encoding='utf-8', newline='')))
    reports = sorted((r for r in rows if r['status'] == 'archived'),
                     key=lambda r: (r['published_date'], r['title']), reverse=True)
    coverage = json.loads((ROOT / 'model-coverage.json').read_text())
    sources = {(s['vendor'], s['slug']): s for s in json.loads((ROOT / 'sources.json').read_text())}
    summary_file = ROOT / 'abstracts/index.json'
    readers = {r['id']: r for r in json.loads(summary_file.read_text())['reports']} if summary_file.exists() else {}
    summaries = {r['source_pdf']: r for r in readers.values() if r.get('source_pdf')}
    web_readers = {(r['vendor'], name): r for r in readers.values() if r.get('source_kind') == 'html' for name in r['models']}
    history = json.loads((ROOT / 'model-history.json').read_text())
    timeline = timeline_models(coverage, history, list(sources.values()), VENDORS)
    # Public browser data contains reader links and release dates, never extraction diagnostics.
    timeline_data = []
    for model in timeline:
        documents = model_documents(model, reports, sources, summaries)
        timeline_data.append(dict(vendor=model['vendor'], model=model['model'],
                                  release_date=model['release_date'],
                                  aliases=model['search_aliases'],
                                  publisher_en='Z.ai / Zhipu AI' if model['vendor'] == 'zai' else VENDORS[model['vendor']],
                                  publisher_cn=VENDORS[model['vendor']],
                                  logo=f'assets/vendors/{MARKS[model["vendor"]]}.svg'
                                  if (ROOT / f'assets/vendors/{MARKS[model["vendor"]]}.svg').is_file() else '',
                                  href=model_target(model, documents, web_readers)))
    figure_file = ROOT / 'figures/index.json'
    figure_reports = {r['id']: r for r in json.loads(figure_file.read_text())['reports']} if figure_file.exists() else {}
    reader_count, preview_count = build_readers(ROOT, output, readers, figure_reports, reports)
    brand = json.loads((ROOT / '.github/brand.json').read_text())
    models = [m for m in coverage['models'] if m.get('lifecycle', 'active') == 'active'
              and (m.get('latest_categories') or m.get('frontier_categories'))]
    current_keys = current_model_keys(models, history)
    for model, entry in zip(timeline, timeline_data):
        entry['categories'] = model['categories']
        entry['frontier'] = (model['vendor'], model['model'].casefold()) in current_keys
    # Real fragments for the showcase: the newest archived document, and a reader that has a figure.
    showcase_report = reports[0]
    showcase_reader, showcase_figure = None, None
    for report in reports:
        summary = summaries.get(report['local_path'])
        if not summary:
            continue
        figures_for = figure_reports.get(summary['id'], {}).get('figures') or []
        if figures_for:
            showcase_reader, showcase_figure = summary, figures_for[0]
            break
    if showcase_reader is None:
        raise ValueError('No reading page with a figure is available for the showcase section')
    template = (ROOT / 'site/template.html').read_text()
    directory_template = (ROOT / 'site/models.html').read_text()
    reports_template = (ROOT / 'site/reports.html').read_text()
    timeline_template = (ROOT / 'site/timeline.html').read_text()
    for chinese in (False, True):
        labels = dict(VENDORS)
        if not chinese:
            labels['zai'] = 'Z.ai / Zhipu AI'
        prefix = '../' if chinese else ''
        def mark(vendor):
            return publisher_mark(vendor, prefix)
        cards = []
        for r in reports:
            date = r['published_date'] or ('日期待确认' if chinese else 'Date unconfirmed')
            kind = DOCUMENT_TYPES[r['document_type']][0]
            revision = f" · {r['version']}" if r['version'].startswith('arxiv-') else ''
            target = report_target(r, summaries)
            cards.append(f'<article class="card" data-view="reports" data-vendor="{r["vendor"]}" data-type="{r["document_type"]}" data-category="" data-date="{r["published_date"]}" data-title="{escape(r["title"])}" data-search="{escape(r["title"] + " " + labels[r["vendor"]] + " " + date)}"><div class="card-heading"><div class="publisher">{mark(r["vendor"])}<span>{escape(labels[r["vendor"]])}</span></div></div><span class="document-badge" data-kind="{r["document_type"]}">{kind}</span><h3><a class="card-link" href="{escape(target)}"{card_link_attributes(target)}>{escape(r["title"])}{card_link_mark(target)}{card_link_hint(target, chinese)}</a></h3><p class="date">{escape(date + revision)} · {r["pages"]} {"页" if chinese else "pages"}</p></article>')
        model_cards = '\n'.join(model_card(model, entry['href'], labels, current_keys, chinese, prefix)
                                for model, entry in zip(timeline, timeline_data))
        publisher_options = ''.join(f'<option value="{v}">{escape(label)}</option>' for v, label in labels.items())
        type_options = ''.join(f'<option value="{k}">{v[0]}</option>' for k, v in DOCUMENT_TYPES.items())
        category_options = ''.join(f'<option value="{k}">{escape(v[int(chinese)])}</option>' for k, v in MODEL_CATEGORIES.items())
        values = {
            'lang': 'zh-CN' if chinese else 'en', 'prefix': '../' if chinese else '',
            'name': escape(brand['name']), 'tagline': escape(brand.get('hero_line_cn' if chinese else 'hero_line', brand['tagline_cn' if chinese else 'tagline'])),
            'intro': '原始报告，前沿模型。从语言与多模态 AI，到机器人与世界模型。' if chinese else 'Original reports. Frontier models. From language and multimodal AI to robotics and world models.',
            'switch': '../index.html' if chinese else 'cn/index.html', 'switch_label': '切换至 English' if chinese else 'Switch to 中文',
            'switch_compact': '中 → EN' if chinese else 'EN → 中',
            'repository': REPOSITORY, 'star': '给项目点个 Star' if chinese else 'Star on GitHub',
            'date_range': f"{min(r['published_date'][:4] for r in reports if r['published_date'])} — {max(r['published_date'][:4] for r in reports if r['published_date'])}",
            'report_count': str(len(reports)), 'publisher_count': str(len(VENDORS)), 'model_count': str(len(models)),
            'reports': '原始报告' if chinese else 'Original reports', 'publishers': '厂商' if chinese else 'Publishers',
            'models': '前沿模型' if chinese else 'Frontier models', 'updated': ('更新于：' if chinese else 'Updated: ') + coverage.get('updated_at', coverage['checked_at']),
            'search': '搜索报告、模型或厂商' if chinese else 'Search reports, models, or publishers',
            'all_publishers': '全部厂商' if chinese else 'All publishers', 'all_types': '全部文档类型' if chinese else 'All document types',
            'all_categories': '全部模型类别' if chinese else 'All model categories',
            'publisher_options': publisher_options, 'type_options': type_options, 'category_options': category_options,
            'timeline_data': json.dumps(timeline_data, ensure_ascii=False).replace('<', '\\u003c'),
            'timeline_title': '模型时间线' if chinese else 'Model timeline',
            'timeline_search': '搜索时间线中的模型或厂商' if chinese else 'Find a model or publisher on the timeline',
            'timeline_pan': '拖动浏览时间线' if chinese else 'Drag to explore the timeline',
            'timeline_gesture': '拖动平移 · 双指或 Ctrl/⌘ + 滚轮缩放' if chinese else 'Drag to pan · Pinch or Ctrl/⌘ + scroll to zoom',
            'timeline_zoom_in': '放大时间线' if chinese else 'Zoom in',
            'timeline_zoom_out': '缩小时间线' if chinese else 'Zoom out',
            'timeline_fit': '全览' if chinese else 'Fit all',
            'timeline_latest': '最新' if chinese else 'Latest',
            'timeline_undated': '日期待确认' if chinese else 'Date unconfirmed',
            'timeline_empty': '当前范围内没有已确认日期的模型' if chinese else 'No dated models in this view',
            'timeline_count_label': '个模型' if chinese else 'models',
            'timeline_count': str(len(timeline)),
            'undated_scope_option': ('<option value="undated">' + ('日期待确认' if chinese else 'Date unconfirmed') + '</option>') if any(not model['release_date'] for model in timeline) else '',
            'model_list_label': '模型列表' if chinese else 'Model list',
            'all_models_link': f'浏览全部 {len(timeline)} 个模型' if chinese else f'Browse all {len(timeline)} models',
            'cards': '\n'.join(cards), 'empty': '未找到匹配结果，请调整搜索或筛选条件。' if chinese else 'No matches. Try a different search or filter.',
            'footer': '从原始报告走向技术洞察。' if chinese else 'From original reports to technical insight.',
            'results': '条结果' if chinese else 'results',
            'explore': '探索报告' if chinese else 'Explore the archive',
            'browse_labs': '追踪每一家厂商' if chinese else 'Follow every frontier lab',
            'publisher_hint': '选择厂商，浏览它的时间线与模型。' if chinese else 'Choose a lab to explore its timeline and models.',
            'clear': '清除筛选' if chinese else 'Clear filters',
            'sort_label': '排序' if chinese else 'Sort',
            'newest': '日期：由新到旧' if chinese else 'Date: newest first',
            'oldest': '日期：由旧到新' if chinese else 'Date: oldest first',
            'alphabetical': '标题：A–Z' if chinese else 'Title: A–Z',
            'theme_label': '外观' if chinese else 'Appearance',
            'light_theme': '浅色' if chinese else 'Light',
            'dark_theme': '深色' if chinese else 'Dark',
            'system_theme': '跟随系统' if chinese else 'System',
            'top': '回到顶部' if chinese else 'Back to top',
            'skip': '跳到内容' if chinese else 'Skip to content',
            'evidence': '原始文档 · 清晰分类 · 来源可追溯' if chinese else 'Original documents · Clear categories · Traceable sources',
            'page_title': ('AI Frontier — 官方前沿 AI 报告、核心原图与模型发布时间线' if chinese else
                           'AI Frontier — official frontier AI reports, core figures and a model timeline'),
            'description': (f'来自 {len(VENDORS)} 家厂商的 {len(reports)} 份官方技术报告、模型卡与系统卡，附原文概要、核心原图，以及 {len(timeline)} 个模型的发布时间线。'
                            if chinese else
                            f'{len(reports)} official technical reports, model cards and system cards from {len(VENDORS)} publishers, '
                            f'with source summaries, core figures and a release timeline of {len(timeline)} models.'),
            'nav_reports': '报告' if chinese else 'Reports',
            'nav_timeline': '时间线' if chinese else 'Timeline',
            'nav_labs': '厂商' if chinese else 'Publishers',
            'nav_models': '模型' if chinese else 'Models',
            'nav_label': '主导航' if chinese else 'Main navigation',
            'nav_publishers_href': '#publishers', 'nav_timeline_href': 'models.html#timeline', 'nav_reports_href': 'reports.html',
            'nav_home': '首页' if chinese else 'Home', 'skip_href': '#publishers',
            'report_return_hint': '在顶部继续向上滑，返回刚才的首页位置。' if chinese else 'Scroll up past the top to return to where you left the home page.',
            'publisher_tiles': publisher_tiles(timeline, reports, labels, chinese, prefix),
            'dated_models': str(sum(1 for model in timeline if model['release_date'])),
            'dated_label': '个模型已有发布日期' if chinese else 'models with a release date',
            'stat_plate': cadence_plate(timeline, chinese),
            'stat_plate_caption': '按季度的模型发布数，取自档案自己记录的日期' if chinese else
                                  "models per quarter, from the archive's own recorded dates",
            'reader_count': str(len(readers)),
            'reader_label': '篇含原文概要与核心原图的报告' if chinese else 'reports with an original-language summary and core figures',
            'figure_count': str(sum(len(record.get('figures') or []) for record in figure_reports.values())),
            'figure_label': '张核心原图，附印刷版图注与页码' if chinese else 'core figures with their printed captions and page numbers',
            'showcase_label': '收进来什么，读的人拿到什么' if chinese else 'What arrives and what a reader gets',
            'showcase_in_title': '收进来的' if chinese else 'What arrives',
            'showcase_in_lead': '官方文档按发布时的原样登记：标题、发布方、类型、日期、修订版本，以及发布方自己的链接。' if chinese else
                                "Official documents are filed exactly as published: title, publisher, type, date, revision, and the publisher's own link.",
            'showcase_input': showcase_input(showcase_report, chinese),
            'showcase_out_title': '读的人拿到什么' if chinese else 'What a reader gets',
            'showcase_out_lead': '原文段落、带印刷版图注与页码的核心原图，以及并排的官方来源。' if chinese else
                                 'The original passage, the core figures with their printed captions and page numbers, and the official source beside them.',
            'showcase_output': showcase_output(showcase_reader, showcase_figure, chinese),
            'proof_title': '每份文档来自哪里' if chinese else 'Where every document comes from',
            'proof_lead': '官方来源、日期、修订与校验值逐份记录。' if chinese else 'Official sources, dates, revisions and checksums are recorded per document.',
            'proof_publisher': '厂商' if chinese else 'Publisher',
            'proof_reports': '报告' if chinese else 'Reports',
            'proof_models': '前沿模型' if chinese else 'Frontier models',
            'proof_latest': '最新一份' if chinese else 'Newest',
            'proof_source': '档案目录' if chinese else 'Collection',
            'proof_rows': proof_table(reports, models, readers, chinese),
            'proof_note': ('原始 PDF 保留在发布方；本站保留官方链接、记录的日期与修订，以及已校验文件的校验值。' if chinese else
                           'Original PDFs stay with their publishers; this archive keeps the official link, the recorded date and revision, '
                           'and a checksum of the file it verified.'),
            'cta_title': '少了一份报告，或发现了更新的修订？' if chinese else 'A missing report, or a newer revision?',
            'cta_lead': '把发布方的官方链接发来，核实后收录。' if chinese else "Send the publisher's official link and it will be verified and added.",
            'cta_action': '提交 issue' if chinese else 'Open an issue',
        }
        values['hero_heading'] = hero_heading(html.unescape(values['tagline']), chinese)
        page = template
        for key, value in values.items():
            page = page.replace('{{' + key + '}}', value)
        target = output / ('cn/index.html' if chinese else 'index.html')
        target.parent.mkdir(exist_ok=True)
        target.write_text(page, encoding='utf-8')
        directory_values = dict(values, page_title='模型 — AI Frontier' if chinese else 'Models — AI Frontier',
                                description=f'浏览 {len(timeline)} 个历史与当前模型，阅读概要原文与核心图片。' if chinese else
                                            f'Browse {len(timeline)} historical and current models, with original summaries and core figures.',
                                switch='../models.html' if chinese else 'cn/models.html',
                                directory_title='模型' if chinese else 'Models',
                                directory_intro='历史与当前模型，直接阅读原文或访问官方来源。' if chinese else
                                                'Historical and current models. Read the original report or visit the official source.',
                                directory_search='搜索模型或厂商' if chinese else 'Search models or publishers',
                                directory_scope='模型范围' if chinese else 'Model scope',
                                all_models='全部模型' if chinese else 'All models', model_cards=model_cards,
                                nav_publishers_href='index.html#publishers', nav_timeline_href='#timeline',
                                nav_reports_href='reports.html', skip_href='#collection')
        header = template.split('<main>', 1)[0].replace('data-page="home"', 'data-page="models"')
        header = header.replace('src="{{prefix}}app.js"', 'src="{{prefix}}models.js"').replace('<script src="{{prefix}}navigation.js" defer>', '<script src="{{prefix}}timeline.js" defer></script><script src="{{prefix}}navigation.js" defer>')
        footer = template[template.index('<footer>'):]
        directory_page = directory_template.replace('{{page_header}}', header).replace('{{page_footer}}', footer).replace('{{model_timeline}}', timeline_template)
        for key, value in directory_values.items():
            directory_page = directory_page.replace('{{' + key + '}}', value)
        (output / ('cn/models.html' if chinese else 'models.html')).write_text(directory_page, encoding='utf-8')
        report_values = dict(values, page_title='原始报告 — AI Frontier' if chinese else 'Original reports — AI Frontier',
                             description=f'浏览来自 {len(VENDORS)} 家厂商的 {len(reports)} 份官方报告。' if chinese else
                                         f'Browse {len(reports)} official reports from {len(VENDORS)} publishers.',
                             switch='../reports.html' if chinese else 'cn/reports.html',
                             nav_publishers_href='index.html#publishers', nav_timeline_href='models.html#timeline',
                             nav_reports_href='reports.html', skip_href='#collection')
        report_header = template.split('<main>', 1)[0].replace('data-page="home"', 'data-page="reports"')
        report_header = report_header.replace('src="{{prefix}}app.js"', 'src="{{prefix}}reports.js"').replace('<script src="{{prefix}}timeline.js" defer></script>', '')
        report_page = reports_template.replace('{{page_header}}', report_header).replace('{{page_footer}}', footer)
        for key, value in report_values.items():
            report_page = report_page.replace('{{' + key + '}}', value)
        (output / ('cn/reports.html' if chinese else 'reports.html')).write_text(report_page, encoding='utf-8')
    for name in ('style.css', 'app.js', 'models.js', 'reports.js', 'motion.js', 'navigation.js', 'navigation-init.js', 'theme-init.js', 'shared.js', 'reader.js', 'timeline.js'):
        shutil.copyfile(ROOT / 'site' / name, output / name)
    (output / 'assets').mkdir(exist_ok=True)
    banner_source = ROOT / 'assets/branding/ai-frontier-banner.png'
    Image.open(banner_source).save(output / 'assets/banner.webp', quality=90, method=6)
    shutil.copyfile(banner_source, output / 'assets/banner.png')
    shutil.copytree(ROOT / 'assets/vendors', output / 'assets/vendors', dirs_exist_ok=True)
    for icon in ICON_FILES:
        source = ROOT / 'assets/branding' / icon
        if not source.is_file():
            raise FileNotFoundError(f'Missing branding icon: {source}')
        shutil.copyfile(source, output / icon)
    write_robots(output)
    write_sitemap(output, readers)
    write_not_found(output)
    (output / '.nojekyll').touch()
    print(f'Built {reader_count} reading pages and {preview_count} figure previews; {len(reports)} reports and {len(models)} frontier entries in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.cache/pages')
    build(parser.parse_args().output)
