"""Render source-bound reading pages and shared lightweight figure previews."""
import hashlib
import html
from pathlib import Path
from urllib.parse import quote

from PIL import Image

REPOSITORY = 'https://github.com/UNLINEARITY/AI-Frontier'


def escape(value):
    return html.escape(str(value), quote=True)


def reader_path(summary):
    vendor, slug = summary['id'].split(':', 1)
    return f'read/{vendor}/{slug}/index.html'


def link(url, label):
    return f'<a href="{escape(url)}">{escape(label)}</a>'


def build_readers(root, output, summaries, figure_reports, catalog, vendors, types):
    template = (root / 'site/reader.html').read_text()
    by_pdf = {r['local_path']: r for r in catalog}
    previews = {}
    roles = {'architecture': ('Architecture', '模型架构'), 'results': ('Results', '实验结果'),
             'overview': ('Overview', '概览'), 'safety_evaluation': ('Safety evaluation', '安全评测')}
    for report in summaries.values():
        row = by_pdf.get(report['source_pdf'])
        if not row or row['sha256'] != report['source_sha256']:
            raise ValueError(f"Stale summary: {report['id']}")
        figure_report = figure_reports.get(report['id'])
        if figure_report and figure_report['source_sha256'] != report['source_sha256']:
            raise ValueError(f"Stale figure selection: {report['id']}")
        figures = figure_report['figures'] if figure_report else []
        for figure in figures:
            source = root / figure['png_path']
            if hashlib.sha256(source.read_bytes()).hexdigest() != figure['png_sha256']:
                raise ValueError(f'Figure checksum mismatch: {source}')
            relative = Path('assets') / Path(figure['png_path']).with_suffix('.webp')
            target = output / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(source) as image:
                image.thumbnail((1800, 1800), Image.Resampling.LANCZOS)
                image.convert('RGB').save(target, 'WEBP', quality=92, method=6)
                previews[figure['png_path']] = (relative.as_posix(), image.size)
        for chinese in (False, True):
            t = lambda en, cn: cn if chinese else en
            path = Path(('cn/' if chinese else '') + reader_path(report))
            prefix = '../' * (len(path.parts) - 1)
            home = prefix + ('cn/index.html' if chinese else 'index.html')
            switch = prefix + ('' if chinese else 'cn/') + reader_path(report)
            source_pdf = REPOSITORY + '/blob/main/' + quote(report['source_pdf'])
            paragraphs = ''.join(f'<p>{escape(p)}</p>' for p in report.get('text', '').split('\n\n') if p.strip())
            pages = ', '.join(str(p) for p in report.get('pages', []))
            heading = report.get('source_heading') or t('Opening passage', '开篇原文')
            summary = (f'<p class="source-heading">{escape(heading)} · {t("Page", "页码")} {escape(pages)}</p>'
                       f'<div class="source-copy">{paragraphs}</div>') if paragraphs else (
                       '<p class="source-empty">' + t('No standalone summary passage identified in this report. Read the original PDF for the full source.',
                       '此报告未识别出独立概要段落，请阅读原始 PDF。') + '</p>')
            gallery = []
            for i, figure in enumerate(figures, 1):
                preview, size = previews[figure['png_path']]
                number = figure.get('figure_number')
                label = t('Figure', '图') + ' ' + str(number if number else i)
                role = roles[figure['role']][int(chinese)]
                caption = figure.get('caption', '')
                downloads = link(REPOSITORY + '/raw/refs/heads/main/' + quote(figure['png_path']), f"PNG · {figure['png_dpi']} DPI")
                downloads += link(REPOSITORY + '/raw/refs/heads/main/' + quote(figure['pdf_path']), t('Cropped PDF', '裁剪 PDF'))
                downloads += link(source_pdf + f"#page={figure['page']}", t('Source page', '原始页码') + ' ' + str(figure['page']))
                alt = label + ' · ' + role
                gallery.append(f'<figure class="figure-card" id="figure-{i}"><div class="figure-meta"><span>{escape(alt)}</span><span>{t("Page", "页码")} {figure["page"]}</span></div><button class="figure-preview" data-preview="{prefix}{preview}" data-title="{escape(alt)}" aria-label="{escape(t("Enlarge", "放大查看") + " " + alt)}"><img src="{prefix}{preview}" width="{size[0]}" height="{size[1]}" alt="{escape(alt)}" loading="lazy" decoding="async"></button><figcaption>{escape(caption)}</figcaption><div class="figure-downloads">{downloads}</div></figure>')
            if not gallery:
                gallery.append('<p class="source-empty">' + t('No core figure selected for this report. The original PDF remains available.', '此报告暂无选取的核心配图，可直接阅读原始 PDF。') + '</p>')
            values = {
                'lang': t('en', 'zh-CN'), 'prefix': prefix, 'home': home, 'switch': switch,
                'switch_label': t('中文', 'English'), 'name': 'AI Frontier', 'repository': REPOSITORY,
                'title': escape(report['title']), 'description': escape(t('Original source summary and core figures from ', '概要原文与核心图片：') + report['title']),
                'publisher': escape(vendors[report['vendor']]), 'vendor': report['vendor'],
                'kind': escape(types[report['document_type']][0]), 'models': escape(' / '.join(report['models'])),
                'date': escape(row['published_date'] or t('Date unconfirmed', '日期待确认')),
                'source_links': link(source_pdf, t('Read original PDF', '阅读原始 PDF')) + link(report['source_url'], t('Official source', '官方来源')) + link(REPOSITORY + '/blob/main/' + quote(report['markdown_path']), 'Markdown'),
                'summary': summary, 'figures': '\n'.join(gallery), 'figure_count': str(len(figures)),
                'summary_label': t('Source summary', '概要原文'), 'figures_label': t('Core figures', '核心图片'),
                'source_note': t('Original wording · Original language', '保留原文 · 保留原始语言'),
                'figure_hint': t('Enlarge to explore. Download the original for full detail.', '点击放大查看，下载原图获取完整细节。'),
                'back': t('Browse this publisher', '浏览此厂商的报告'), 'contents': t('On this page', '本页内容'),
                'zoom': t('Figure preview', '图片预览'), 'close': t('Close preview', '关闭预览'),
                'viewer_hint': t('Click the image to zoom. Press Esc to close. Full-resolution files are available below each figure.', '点击图片切换缩放，按 Esc 关闭。每张图下方可下载高清文件。'),
                'theme_label': t('Appearance', '外观'), 'light_theme': t('Light', '浅色'), 'dark_theme': t('Dark', '深色'), 'system_theme': t('System', '跟随系统'),
                'star': t('Star on GitHub', '在 GitHub 上 Star'), 'skip': t('Skip to content', '跳到内容'), 'top': t('Back to top', '回到顶部'),
                'footer': t('Read the source. Explore the frontier.', '阅读原文，探索前沿。'),
            }
            page = template
            for key, value in values.items():
                page = page.replace('{{' + key + '}}', value)
            target = output / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(page, encoding='utf-8')
    return len(summaries) * 2, len(previews)
