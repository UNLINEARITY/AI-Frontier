"""Build a small bilingual Pages site from the archive's curated data."""
import argparse
import csv
import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

from build_readers import build_readers, reader_path
from archive_reports import DOCUMENT_TYPES, MODEL_CATEGORIES, VENDORS
from model_timeline import timeline_models

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/UNLINEARITY/AI-Frontier'
MARKS = {v: {'qwen': 'alibaba', 'amazon': 'aws'}.get(v, v) for v in VENDORS}


def escape(value):
    return html.escape(str(value), quote=True)


def link(url, label):
    return f'<a href="{escape(url)}">{escape(label)}</a>'


def publisher_mark(vendor, prefix=''):
    filename = f'{MARKS[vendor]}.svg'
    if not (ROOT / 'assets/vendors' / filename).is_file():
        return ''
    return f'<img class="publisher-mark" src="{prefix}assets/vendors/{filename}" alt="" loading="lazy">'


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
    (output / 'timeline.json').write_text(json.dumps(timeline_data, ensure_ascii=False) + '\n', encoding='utf-8')
    figure_file = ROOT / 'figures/index.json'
    figure_reports = {r['id']: r for r in json.loads(figure_file.read_text())['reports']} if figure_file.exists() else {}
    reader_count, preview_count = build_readers(ROOT, output, readers, figure_reports, reports)
    brand = json.loads((ROOT / '.github/brand.json').read_text())
    models = [m for m in coverage['models'] if m.get('lifecycle', 'active') == 'active'
              and (m.get('latest_categories') or m.get('frontier_categories'))]
    template = (ROOT / 'site/template.html').read_text()
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
            cards.append(f'<article class="card" data-view="reports" data-vendor="{r["vendor"]}" data-type="{r["document_type"]}" data-category="" data-date="{r["published_date"]}" data-title="{escape(r["title"])}" data-search="{escape(r["title"] + " " + labels[r["vendor"]] + " " + date)}"><div class="card-heading"><div class="publisher">{mark(r["vendor"])}<span>{escape(labels[r["vendor"]])}</span></div><span class="document-badge" data-kind="{r["document_type"]}">{kind}</span></div><h3><a class="card-link" href="{escape(target)}">{escape(r["title"])}</a></h3><p class="date">{escape(date + revision)} · {r["pages"]} {"页" if chinese else "pages"}</p></article>')
        for m in models:
            categories = [c for c in MODEL_CATEGORIES if c in m.get('latest_categories', []) or c in m.get('frontier_categories', [])]
            documents = model_documents(m, reports, sources, summaries)
            target = model_target(m, documents, web_readers)
            additional = '<div class="links">' + ''.join(link(d[2], d[3]) for d in documents[1:]) + '</div>' if len(documents) > 1 else ''
            cards.append(f'<article class="card" data-date="" data-title="{escape(m["model"])}" data-view="models" data-vendor="{m["vendor"]}" data-type="" data-category="{escape(" ".join(categories))}" data-search="{escape(m["model"] + " " + labels[m["vendor"]])}" hidden><div class="card-heading"><div class="publisher">{mark(m["vendor"])}<span>{escape(labels[m["vendor"]])}</span></div><span class="model-indicator" aria-hidden="true"></span></div><h3><a class="card-link" href="{escape(target)}">{escape(m["model"])}</a></h3><p class="date">{escape(" / ".join(MODEL_CATEGORIES[c][int(chinese)] for c in categories))}</p>{additional}</article>')
        publisher_options = ''.join(f'<option value="{v}">{escape(label)}</option>' for v, label in labels.items())
        type_options = ''.join(f'<option value="{k}">{v[0]}</option>' for k, v in DOCUMENT_TYPES.items())
        category_options = ''.join(f'<option value="{k}">{escape(v[int(chinese)])}</option>' for k, v in MODEL_CATEGORIES.items())
        values = {
            'lang': 'zh-CN' if chinese else 'en', 'prefix': '../' if chinese else '',
            'name': escape(brand['name']), 'tagline': escape(brand['tagline_cn' if chinese else 'tagline']),
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
            'cards': '\n'.join(cards), 'empty': '未找到匹配结果，请调整搜索或筛选条件。' if chinese else 'No matches. Try a different search or filter.',
            'footer': '从原始报告走向技术洞察。' if chinese else 'From original reports to technical insight.',
            'results': '条结果' if chinese else 'results',
            'explore': '探索报告' if chinese else 'Explore the archive',
            'browse_labs': '追踪每一家厂商' if chinese else 'Follow every frontier lab',
            'publisher_hint': '选择厂商，浏览报告与前沿模型。' if chinese else 'Choose a publisher. Explore reports and frontier models.',
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
            'publisher_buttons': ''.join(
                f'<button class="lab" data-publisher="{v}" data-reports="{sum(r["vendor"] == v for r in reports)}" aria-pressed="false">{mark(v)}'
                f'<span class="lab-details"><span class="lab-name">{escape(label.split(" / ")[0])}</span>'
                f'<span class="lab-count">{sum(r["vendor"] == v for r in reports)} {"份 PDF 报告" if chinese else "PDF reports"} · '
                f'{sum(m["vendor"] == v for m in models)} {"个模型" if chinese else "models"}</span></span></button>'
                for v, label in labels.items()),
        }
        page = template
        for key, value in values.items():
            page = page.replace('{{' + key + '}}', value)
        target = output / ('cn/index.html' if chinese else 'index.html')
        target.parent.mkdir(exist_ok=True)
        target.write_text(page, encoding='utf-8')
    for name in ('style.css', 'app.js', 'theme-init.js', 'shared.js', 'reader.css', 'reader.js', 'timeline.css', 'timeline.js'):
        shutil.copyfile(ROOT / 'site' / name, output / name)
    (output / 'assets').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'assets/branding/ai-frontier-banner.png', output / 'assets/banner.png')
    shutil.copytree(ROOT / 'assets/vendors', output / 'assets/vendors', dirs_exist_ok=True)
    (output / '.nojekyll').touch()
    print(f'Built {reader_count} reading pages and {preview_count} figure previews; {len(reports)} reports and {len(models)} frontier entries in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.cache/pages')
    build(parser.parse_args().output)
