"""Protect the shared Markdown body, bilingual links, and original figures."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_readers import build_readers, reader_path

ROOT = Path(__file__).resolve().parents[1]


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'site').mkdir()
        (self.root / 'site/reader.html').write_text((ROOT / 'site/reader.html').read_text())
        self.output = self.root / 'output'
        self.summary = dict(id='lab:model', vendor='lab', title='Model <test>', models=['Model'],
                            document_type='technical_report', source_pdf='pdfs/model.pdf', source_sha256='source',
                            source_url='https://example.org/model', markdown_path='abstracts/lab/model.md',
                            text='This JSON field is not the rendered body.', pages=[2], source_heading='Abstract')
        self.catalog = [dict(local_path='pdfs/model.pdf', sha256='source', published_date='2026-01-01')]
        self.markdown = self.root / self.summary['markdown_path']
        self.markdown.parent.mkdir(parents=True)
        self.markdown.write_text('# Model <test>\n\n[PDF](../../pdfs/model.pdf#page=2)\n\n## Abstract\n\nSource <script>alert(1)</script> & original.\n\n**Markdown emphasis**.\n')

    def build(self, figures=None):
        return build_readers(self.root, self.output, {'pdfs/model.pdf': self.summary}, figures or {}, self.catalog)

    def test_shared_markdown_and_language_links(self):
        self.assertEqual(self.build(), (2, 0))
        en = (self.output / 'abstracts/lab/model.html').read_text()
        cn = (self.output / 'cn/abstracts/lab/model.html').read_text()
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', en)
        self.assertNotIn('<script>alert(1)', en)
        self.assertIn('<strong>Markdown emphasis</strong>', en)
        self.assertNotIn(self.summary['text'], en)
        self.assertIn('href="../../cn/abstracts/lab/model.html"', en)
        self.assertIn('href="../../../abstracts/lab/model.html"', cn)
        self.assertIn('href="../../../cn/reports.html?publisher=lab"', cn)
        self.assertNotIn('{{', en + cn)
        self.assertNotIn('No core figure selected', en)
        self.assertNotIn('Source summary', en)
        self.assertNotIn('reader-sections', en)
        old = (self.output / 'read/lab/model/index.html').read_text()
        self.assertIn('../../../abstracts/lab/model.html', old)
        self.assertEqual(reader_path(self.summary), 'abstracts/lab/model.html')

    def test_cards_use_official_sources_without_a_summary(self):
        from build_pages import report_target
        row = dict(local_path='pdfs/model.pdf', sha256='source', source_url='https://example.org/report')
        self.assertEqual(report_target(row, {}), row['source_url'])
        self.assertEqual(report_target(row, {'pdfs/model.pdf': self.summary}), 'abstracts/lab/model.html')
        self.summary['source_sha256'] = 'stale'
        self.assertEqual(report_target(row, {'pdfs/model.pdf': self.summary}), row['source_url'])

    def test_publisher_without_a_logo_does_not_emit_a_broken_image(self):
        from build_pages import publisher_mark
        from unittest.mock import patch
        import build_pages
        with patch.object(build_pages, 'ROOT', self.root):
            self.assertEqual(publisher_mark('agibot'), '')
            asset = self.root / 'assets/vendors/agibot.svg'
            asset.parent.mkdir(parents=True)
            asset.write_text('<svg/>')
            self.assertIn('src="../assets/vendors/agibot.svg"', publisher_mark('agibot', '../'))

    def test_model_alias_opens_available_web_reader_before_external_report(self):
        from build_pages import model_target
        model = dict(vendor='lab', model='Variant', source_url='https://example.org/model',
                     reading_aliases=['Model family'])
        documents = [(True, 0, 'https://example.org/report', 'Report')]
        readers = {('lab', 'Model family'): self.summary}
        self.assertEqual(model_target(model, documents, readers), reader_path(self.summary))
        documents[0] = (False, 0, 'abstracts/lab/other.html', 'Report')
        self.assertEqual(model_target(model, documents, readers), 'abstracts/lab/other.html')

    def test_reader_navigation_links_both_languages(self):
        from build_readers import reader_navigation
        entry = lambda path, model, date='': dict(path=path, model=model, date=date,
                                                  publisher_en='Lab', publisher_cn='实验室')
        nav = {'prev': entry('abstracts/lab/older.html', 'Older <model>', '2025-01-02'),
               'next': entry('abstracts/lab/newer.html', 'Newer', '')}
        en = reader_navigation(nav, '../../', False)
        cn = reader_navigation(nav, '../../../', True)
        self.assertIn('class="reader-pager"', en)
        self.assertIn('href="../../abstracts/lab/older.html" rel="prev"', en)
        self.assertIn('href="../../abstracts/lab/newer.html" rel="next"', en)
        self.assertIn('aria-keyshortcuts="ArrowLeft"', en)
        self.assertIn('aria-keyshortcuts="ArrowRight"', en)
        self.assertIn('Older &lt;model&gt;', en)
        self.assertIn('Previous', en)
        self.assertIn('Next', en)
        self.assertNotIn('<span class="reader-pager-meta"></span>', en)
        self.assertIn('href="../../../cn/abstracts/lab/older.html"', cn)
        self.assertIn('href="../../../cn/abstracts/lab/newer.html"', cn)
        self.assertIn('上一份', cn)
        self.assertIn('实验室', cn)
        self.assertEqual(reader_navigation(None, '../../', False), '')

    def test_reader_pages_carry_the_timeline_neighbours(self):
        entry = lambda path, model: dict(path=path, model=model, date='2026-02-03',
                                         publisher_en='Lab', publisher_cn='实验室')
        nav = {'lab:model': {'prev': entry('abstracts/lab/older.html', 'Older'),
                             'next': entry('abstracts/lab/newer.html', 'Newer')}}
        build_readers(self.root, self.output, {'pdfs/model.pdf': self.summary}, {}, self.catalog, None, nav)
        en = (self.output / 'abstracts/lab/model.html').read_text()
        cn = (self.output / 'cn/abstracts/lab/model.html').read_text()
        self.assertIn('href="../../abstracts/lab/newer.html"', en)
        self.assertIn('href="../../../cn/abstracts/lab/newer.html"', cn)
        self.assertNotIn('{{', en + cn)
        without = build_readers(self.root, self.output, {'pdfs/model.pdf': self.summary}, {}, self.catalog, None, {})
        self.assertEqual(without, (2, 0))
        self.assertNotIn('reader-pager', (self.output / 'abstracts/lab/model.html').read_text())

    def test_stale_source_and_figure_selection_rejected(self):
        self.summary['source_sha256'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'Stale summary'):
            self.build()
        self.summary['source_sha256'] = 'source'
        with self.assertRaisesRegex(ValueError, 'Stale figure'):
            self.build({'lab:model': dict(source_sha256='changed', figures=[])})

    def test_shared_inline_preview_and_original_download(self):
        source = self.root / 'figures/lab/model/figure-01.png'
        source.parent.mkdir(parents=True)
        Image.new('RGB', (2000, 1000), 'white').save(source)
        figure = dict(png_path='figures/lab/model/figure-01.png', pdf_path='figures/lab/model/figure-01.pdf',
                      png_sha256=hashlib.sha256(source.read_bytes()).hexdigest(), figure_number='7',
                      role='architecture', caption='Original caption <&>', page=3, png_dpi=600)
        self.markdown.write_text(self.markdown.read_text() + '\n![Figure 7](../../figures/lab/model/figure-01.png)\n\nOriginal caption <&>\n\n[p. 3](../../pdfs/model.pdf#page=3) · [PDF](../../figures/lab/model/figure-01.pdf)\n')
        figures = {'lab:model': dict(source_sha256='source', figures=[figure])}
        self.assertEqual(self.build(figures), (2, 1))
        with Image.open(self.output / 'assets/figures/lab/model/figure-01.webp') as preview:
            self.assertEqual(preview.size, (1800, 900))
        en = (self.output / 'abstracts/lab/model.html').read_text()
        self.assertIn('Figure 7', en)
        self.assertIn('Original caption &lt;&amp;&gt;', en)
        self.assertIn('/raw/refs/heads/main/figures/lab/model/figure-01.png', en)
        self.assertNotIn('/blob/main/figures/lab/model/figure-01.pdf', en)
        self.assertNotIn('/blob/main/pdfs/model.pdf', en)
        self.assertIn('class="inline-image"', en)
        self.assertNotIn('figure-card', en)
        for language, prefix in (('', '../../'), ('cn/', '../../../')):
            with self.subTest(language=language):
                page_path = self.output / language / 'abstracts/lab/model.html'
                page = page_path.read_text()
                preview_url = prefix + 'assets/figures/lab/model/figure-01.webp'
                self.assertIn(f'src="{preview_url}"', page)
                self.assertIn(f'data-preview="{preview_url}"', page)
                self.assertNotIn('{{', page)
                self.assertTrue((page_path.parent / preview_url).is_file())
        self.assertFalse(list(self.output.rglob('*.pdf')))
        figure['png_sha256'] = 'changed'
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            self.build(figures)

    def test_unsafe_link_and_unregistered_image_are_rejected(self):
        self.markdown.write_text('# Test\n\n[Unsafe](javascript:alert%281%29)\n')
        self.build()
        self.assertNotIn('href="javascript:', (self.output / 'abstracts/lab/model.html').read_text())
        self.markdown.write_text('# Test\n\n![Unknown](../../outside.png)\n')
        import subprocess
        with self.assertRaises(subprocess.CalledProcessError):
            self.build()


if __name__ == '__main__':
    unittest.main()
