"""Build a small bilingual Pages site from the archive's curated data."""
import argparse
import csv
import html
import json
import shutil
from pathlib import Path
from urllib.parse import quote

from archive_reports import DOCUMENT_TYPES, MODEL_CATEGORIES, VENDORS

ROOT = Path(__file__).resolve().parents[1]
REPOSITORY = 'https://github.com/UNLINEARITY/AI-Frontier'
MARKS = {v: {'qwen': 'alibaba', 'amazon': 'aws'}.get(v, v) for v in VENDORS}


def escape(value):
    return html.escape(str(value), quote=True)


def link(url, label):
    return f'<a href="{escape(url)}">{escape(label)}</a>'


def build(output):
    output.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((ROOT / 'catalog.csv').open(encoding='utf-8', newline='')))
    reports = sorted((r for r in rows if r['status'] == 'archived'),
                     key=lambda r: (r['published_date'], r['title']), reverse=True)
    coverage = json.loads((ROOT / 'model-coverage.json').read_text())
    sources = {(s['vendor'], s['slug']): s for s in json.loads((ROOT / 'sources.json').read_text())}
    brand = json.loads((ROOT / '.github/brand.json').read_text())
    models = [m for m in coverage['models'] if m.get('lifecycle', 'active') == 'active'
              and (m.get('latest_categories') or m.get('frontier_categories'))]
    template = (ROOT / 'site/template.html').read_text()
    for chinese in (False, True):
        labels = dict(VENDORS)
        if not chinese:
            labels['zai'] = 'Z.ai / Zhipu AI'
        prefix = '../' if chinese else ''
        def publisher_mark(vendor):
            return f'<img class="publisher-mark" src="{prefix}assets/vendors/{MARKS[vendor]}.svg" alt="" loading="lazy">'
        cards = []
        for r in reports:
            date = r['published_date'] or ('日期待确认' if chinese else 'Date unconfirmed')
            kind = DOCUMENT_TYPES[r['document_type']][0]
            revision = f" · {r['version']}" if r['version'].startswith('arxiv-') else ''
            read = link(REPOSITORY + '/blob/main/' + quote(r['local_path']), '阅读 PDF' if chinese else 'Read PDF')
            official = link(r['source_url'], '官方来源' if chinese else 'Official source')
            cards.append(f'<article class="card" data-view="reports" data-vendor="{r["vendor"]}" data-type="{r["document_type"]}" data-category="" data-date="{r["published_date"]}" data-title="{escape(r["title"])}" data-search="{escape(r["title"] + " " + labels[r["vendor"]] + " " + date)}"><div class="card-heading"><div class="publisher">{publisher_mark(r["vendor"])}<span>{escape(labels[r["vendor"]])}</span></div><span class="document-badge" data-kind="{r["document_type"]}">{kind}</span></div><h3>{escape(r["title"])}</h3><p class="date">{escape(date + revision)} · {r["pages"]} {"页" if chinese else "pages"}</p><div class="links">{read}{official}</div></article>')
        for m in models:
            categories = [c for c in MODEL_CATEGORIES if c in m.get('latest_categories', []) or c in m.get('frontier_categories', [])]
            links = []
            for slug in m.get('report_slugs', []):
                source = sources[(m['vendor'], slug)]
                archived = [r for r in reports if r['vendor'] == m['vendor'] and r['title'] == source['title']]
                if archived:
                    row = max(archived, key=lambda r: (r['source_updated_date'], r['retrieved_at']))
                    links.append(link(REPOSITORY + '/blob/main/' + quote(row['local_path']), source['title']))
            links.append(link(m.get('frontier_source_url', m['source_url']), '官方介绍' if chinese else 'Official introduction'))
            cards.append(f'<article class="card" data-date="" data-title="{escape(m["model"])}" data-view="models" data-vendor="{m["vendor"]}" data-type="" data-category="{escape(" ".join(categories))}" data-search="{escape(m["model"] + " " + labels[m["vendor"]])}" hidden><div class="card-heading"><div class="publisher">{publisher_mark(m["vendor"])}<span>{escape(labels[m["vendor"]])}</span></div><span class="model-indicator" aria-hidden="true"></span></div><h3>{escape(m["model"])}</h3><p class="date">{escape(" / ".join(MODEL_CATEGORIES[c][int(chinese)] for c in categories))}</p><div class="links">{"".join(links)}</div></article>')
        publisher_options = ''.join(f'<option value="{v}">{escape(label)}</option>' for v, label in labels.items())
        type_options = ''.join(f'<option value="{k}">{v[0]}</option>' for k, v in DOCUMENT_TYPES.items())
        category_options = ''.join(f'<option value="{k}">{escape(v[int(chinese)])}</option>' for k, v in MODEL_CATEGORIES.items())
        values = {
            'lang': 'zh-CN' if chinese else 'en', 'prefix': '../' if chinese else '',
            'name': escape(brand['name']), 'tagline': escape(brand['tagline_cn' if chinese else 'tagline']),
            'intro': '原始报告，前沿模型，技术洞察。按厂商与类别探索 AI 的演进。' if chinese else 'Original reports. Frontier models. Technical insight. Explore how AI evolves across labs and model families.',
            'switch': '../index.html' if chinese else 'cn/index.html', 'switch_label': 'English' if chinese else '中文',
            'repository': REPOSITORY, 'star': '在 GitHub 上 Star' if chinese else 'Star on GitHub',
            'date_range': f"{min(r['published_date'][:4] for r in reports if r['published_date'])} — {max(r['published_date'][:4] for r in reports if r['published_date'])}",
            'report_count': str(len(reports)), 'publisher_count': str(len(VENDORS)), 'model_count': str(len(models)),
            'reports': '原始报告' if chinese else 'Original reports', 'publishers': '厂商' if chinese else 'Publishers',
            'models': '前沿模型' if chinese else 'Frontier models', 'updated': ('模型核查：' if chinese else 'Models reviewed: ') + coverage['checked_at'],
            'search': '搜索报告、模型或厂商' if chinese else 'Search reports, models, or publishers',
            'all_publishers': '全部厂商' if chinese else 'All publishers', 'all_types': '全部文档类型' if chinese else 'All document types',
            'all_categories': '全部模型类别' if chinese else 'All model categories',
            'publisher_options': publisher_options, 'type_options': type_options, 'category_options': category_options,
            'cards': '\n'.join(cards), 'empty': '未找到匹配结果，请调整搜索或筛选条件。' if chinese else 'No matches. Try a different search or filter.',
            'footer': '保留厂商原始文档。Markdown 与技术分析正在规划中。' if chinese else 'Original publisher documents preserved. Markdown editions and technical analysis are planned.',
            'results': '条结果' if chinese else 'results',
            'explore': '探索报告' if chinese else 'Explore the archive',
            'browse_labs': '追踪每一家厂商' if chinese else 'Follow every frontier lab',
            'publisher_hint': '选择厂商，直达原始报告。' if chinese else 'Choose a publisher. Go straight to the source.',
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
            'publisher_buttons': ''.join(f'<button class="lab" data-publisher="{v}" aria-pressed="false">{publisher_mark(v)}<span>{escape(label.split(" / ")[0])}</span><span class="lab-count">{sum(r["vendor"] == v for r in reports)}</span></button>' for v, label in labels.items()),
        }
        page = template
        for key, value in values.items():
            page = page.replace('{{' + key + '}}', value)
        target = output / ('cn/index.html' if chinese else 'index.html')
        target.parent.mkdir(exist_ok=True)
        target.write_text(page, encoding='utf-8')
    for name in ('style.css', 'app.js', 'theme-init.js'):
        shutil.copyfile(ROOT / 'site' / name, output / name)
    (output / 'assets').mkdir(exist_ok=True)
    shutil.copyfile(ROOT / 'assets/branding/ai-frontier-banner.png', output / 'assets/banner.png')
    shutil.copytree(ROOT / 'assets/vendors', output / 'assets/vendors', dirs_exist_ok=True)
    (output / '.nojekyll').touch()
    print(f'Built {len(reports)} reports and {len(models)} frontier entries in {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / '.cache/pages')
    build(parser.parse_args().output)
