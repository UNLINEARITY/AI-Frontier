"""Protect the Pages shell: bilingual cards, publisher counts, icons and generated site files."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_pages import (SITE_URL, card_link_attributes, card_link_hint, card_link_mark, lab_count, publisher_tiles,
                         write_not_found, write_robots, write_sitemap)

ROOT = Path(__file__).resolve().parents[1]


class ShellTests(unittest.TestCase):
    def test_external_card_links_are_marked_and_open_separately(self):
        external, internal = 'https://example.org/report', 'abstracts/lab/model.html'
        self.assertEqual(card_link_attributes(external), ' target="_blank" rel="noopener"')
        self.assertEqual(card_link_attributes(internal), '')
        self.assertIn('external-mark', card_link_mark(external))
        self.assertEqual(card_link_mark(internal), '')
        self.assertIn('opens in a new tab', card_link_hint(external, False))
        self.assertIn('新标签页', card_link_hint(external, True))
        self.assertEqual(card_link_hint(internal, False), '')

    def test_publisher_counts_drop_empty_reports_and_pluralize(self):
        self.assertEqual(lab_count(43, 10, False), '<span class="lab-count"><span>43 reports</span><span>10 models</span></span>')
        self.assertEqual(lab_count(1, 1, False), '<span class="lab-count"><span>1 report</span><span>1 model</span></span>')
        self.assertEqual(lab_count(0, 1, False), '<span class="lab-count"><span>1 model</span></span>')
        self.assertNotIn('0 ', lab_count(0, 3, False))
        self.assertNotIn('0 ', lab_count(0, 3, True))
        self.assertEqual(lab_count(43, 10, True), '<span class="lab-count"><span>43 份报告</span><span>10 个模型</span></span>')
        self.assertIn('1 个模型', lab_count(0, 1, True))
        self.assertIn('No records', lab_count(0, 0, False))
        self.assertIn('无记录', lab_count(0, 0, True))

    def test_overview_precedes_timeline_and_models_have_a_direct_page(self):
        from html.parser import HTMLParser
        class Sections(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids, self.links = [], []
            def handle_starttag(self, tag, attrs):
                attributes = dict(attrs)
                if tag == 'section' and attributes.get('id'):
                    self.ids.append(attributes['id'])
                if tag == 'a':
                    self.links.append(attributes.get('href'))
        parser = Sections()
        parser.feed((ROOT / 'site/template.html').read_text())
        self.assertLess(parser.ids.index('publishers'), parser.ids.index('timeline'))
        self.assertNotIn('collection', parser.ids)
        self.assertIn('reports.html', parser.links)
        self.assertIn('id="collection"', (ROOT / 'site/reports.html').read_text())
        self.assertIn('models.html', parser.links)
        self.assertNotIn('timeline-pending', parser.ids)

    def test_publisher_index_is_complete_including_model_only_labs_and_all(self):
        labels = {'openai': 'Lab', 'generalist': 'Robot & Co', 'figure': 'New Lab'}
        models = [{'vendor': 'openai'}, {'vendor': 'openai'}, {'vendor': 'generalist'}]
        reports = [{'vendor': 'openai'}]
        for chinese in (False, True):
            tiles = publisher_tiles(models, reports, labels, chinese, '../')
            self.assertEqual(tiles.count('<button '), len(labels) + 1)
            for vendor in ('', *labels):
                self.assertIn(f'data-publisher="{vendor}"', tiles)
            self.assertIn('Robot &amp; Co', tiles)
            self.assertIn('3 个模型' if chinese else '3 models', tiles)
            self.assertNotIn('0 reports', tiles)

    def test_stylesheet_keeps_the_house_style(self):
        css = (ROOT / 'site/style.css').read_text()
        for banned in ('linear-gradient(', 'radial-gradient(', 'box-shadow:', 'border-radius: 14px'):
            self.assertNotIn(banned, css)
        self.assertNotIn('border-top: 1px', css)
        self.assertNotIn('border-bottom: 1px', css)

    def test_template_declares_the_light_banner_and_icons(self):
        for name in ('site/template.html', 'site/reader.html'):
            page = (ROOT / name).read_text()
            self.assertIn('favicon.svg', page)
            self.assertIn('apple-touch-icon.png', page)
        template = (ROOT / 'site/template.html').read_text()
        self.assertIn('<source type="image/webp" srcset="{{prefix}}assets/banner.webp">', template)
        self.assertIn('width="2172" height="724"', template)
        self.assertNotIn('timeline.json', (ROOT / 'scripts/build_pages.py').read_text())

    def test_generated_site_files_point_at_the_public_site(self):
        self.assertEqual(SITE_URL, 'https://unlinearity.github.io/AI-Frontier')
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp)
            readers = {'pdfs/model.pdf': dict(markdown_path='abstracts/lab/model.md')}
            write_robots(output)
            write_sitemap(output, readers)
            write_not_found(output)
            robots = (output / 'robots.txt').read_text()
            self.assertIn(f'Sitemap: {SITE_URL}/sitemap.xml', robots)
            sitemap = (output / 'sitemap.xml').read_text()
            self.assertEqual(sitemap.count('<loc>'), 8)
            for location in (f'{SITE_URL}/', f'{SITE_URL}/cn/', f'{SITE_URL}/abstracts/lab/model.html',
                             f'{SITE_URL}/cn/abstracts/lab/model.html', f'{SITE_URL}/models.html', f'{SITE_URL}/cn/models.html', f'{SITE_URL}/reports.html', f'{SITE_URL}/cn/reports.html'):
                self.assertIn(f'<loc>{location}</loc>', sitemap)
            page = (output / '404.html').read_text()
            self.assertNotIn('__SITE__', page)
            self.assertIn(f'href="{SITE_URL}/"', page)
            self.assertIn(f'href="{SITE_URL}/cn/"', page)
            self.assertIn('noindex', page)


if __name__ == '__main__':
    unittest.main()
