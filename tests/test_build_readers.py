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
        self.assertIn('href="../../../cn/index.html?publisher=lab#collection"', cn)
        self.assertNotIn('{{', en + cn)
        self.assertNotIn('No core figure selected', en)
        self.assertNotIn('Source summary', en)
        self.assertNotIn('reader-sections', en)
        old = (self.output / 'read/lab/model/index.html').read_text()
        self.assertIn('../../../abstracts/lab/model.html', old)
        self.assertEqual(reader_path(self.summary), 'abstracts/lab/model.html')

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
        self.assertIn('/blob/main/figures/lab/model/figure-01.pdf', en)
        self.assertIn('class="inline-image"', en)
        self.assertNotIn('figure-card', en)
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
