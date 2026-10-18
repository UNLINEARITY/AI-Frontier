"""Source-bound, static TextFold package regressions.

These tests use tiny local OCR/PDF fixtures; they never call a model, network API, or browser.
"""
import gzip
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from textfold_sources import load_textfold_index, prepare_document  # noqa: E402
from textfold_static import write_static_reader  # noqa: E402


class TextFoldSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.pdf_rel = 'pdfs/lab/technical-reports/model.pdf'
        self.pdf = self.root / self.pdf_rel
        self.pdf.parent.mkdir(parents=True)
        self.pdf.write_bytes(b'test PDF bytes')
        self.row = {
            'vendor': 'lab', 'title': 'Model report', 'document_type': 'technical_report',
            'local_path': self.pdf_rel,
            'sha256': hashlib.sha256(self.pdf.read_bytes()).hexdigest(),
            'source_url': 'https://example.org/model', 'published_date': '2026-01-02',
            'version': 'v1',
        }
        self.summary = {
            'id': 'lab:model', 'title': self.row['title'], 'source_pdf': self.pdf_rel,
            'source_sha256': self.row['sha256'], 'source_url': self.row['source_url'],
        }
        self.workspace = self.root / 'ocr/lab/technical-reports/model'
        (self.workspace / 'images').mkdir(parents=True)
        self.ocr = self.workspace / 'model.md'
        self.ocr.write_text(
            '# Model report\n\n'
            '## Abstract\n\n'
            'We present a model for grounded reasoning. The model uses a compact visual encoder.\n\n'
            '## 1 Introduction\n\n'
            'The method improves the measured score. It also keeps inference cost low.\n\n'
            '| Setting | Score |\n| --- | ---: |\n| Base | 42 |\n\n'
            'The scaling law is $E=mc^2$.\n\n'
            '![Figure](images/chart.jpg)\n\n'
            '<script>alert(1)</script><p onclick="x()">Safe text.</p>\n',
            encoding='utf-8',
        )
        self.image = self.workspace / 'images/chart.jpg'
        Image.new('RGB', (24, 12), 'navy').save(self.image, 'JPEG')

    def prepare(self):
        return prepare_document(self.root, self.row, self.summary)

    def write_index(self, record):
        index = self.root / 'reader-content/index.json'
        index.parent.mkdir(parents=True, exist_ok=True)
        index.write_text(json.dumps({'schema_version': 1, 'reports': [record]}), encoding='utf-8')
        return index

    def install_static_reader(self):
        (self.root / 'site').mkdir(exist_ok=True)
        shutil.copy2(ROOT / 'site/reader.html', self.root / 'site/reader.html')
        shutil.copytree(ROOT / 'site/vendor/textfold', self.root / 'site/vendor/textfold')

    def write_table_ocr(self, image_path='images/missing.jpg'):
        self.ocr.write_text(
            '# Model report\n\n## 1 Results\n\n'
            '<table><tbody><tr><td>Measured result '
            f'<img src="{image_path}" alt="table child"></td></tr></tbody></table>\n',
            encoding='utf-8',
        )
        self.workspace.joinpath('content_list_v2.json').write_text(json.dumps([
            {'type': 'table', 'table_body': f'<table><img src="{image_path}"></table>',
             'img_path': 'images/whole-table-missing.jpg', 'bbox': [100, 100, 900, 900], 'page_idx': 0},
        ]), encoding='utf-8')

    def replace_pdf_with_one_page_fixture(self):
        import pymupdf

        document = pymupdf.open()
        page = document.new_page(width=300, height=300)
        page.draw_rect(pymupdf.Rect(35, 35, 265, 265), color=(0, 0, 0), width=1)
        page.insert_text((55, 70), 'Table cell value 42', fontsize=16)
        document.save(self.pdf)
        document.close()
        self.row['sha256'] = hashlib.sha256(self.pdf.read_bytes()).hexdigest()
        self.summary['source_sha256'] = self.row['sha256']

    def test_preparation_binds_real_pdf_and_ocr_and_uses_local_ladder(self):
        record = self.prepare()
        self.assertEqual(record['source_pdf'], self.pdf_rel)
        self.assertEqual(record['source_sha256'], self.row['sha256'])
        self.assertEqual(record['ocr_markdown'], 'ocr/lab/technical-reports/model/model.md')
        self.assertEqual(record['ocr_sha256'], hashlib.sha256(self.ocr.read_bytes()).hexdigest())
        path = self.root / record['document_path']
        self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record['document_sha256'])
        document = json.loads(gzip.decompress(path.read_bytes()))
        self.assertEqual(document['meta']['id'], record['id'])
        self.assertEqual(document['meta']['source_sha256'], self.row['sha256'])
        self.assertEqual(document['provenance']['method'], 'local-first-sentence')
        self.assertFalse(document['provenance']['ai_generated'])
        self.assertTrue(document['units'])
        self.assertTrue(all(unit['lad']['model'] == 'local' for unit in document['units'].values()))

    def test_obsidian_embed_math_table_and_safe_html_survive_preparation(self):
        self.ocr.write_text(
            '# Model report\n\n## 1 Introduction\n\n'
            'The result is $E=mc^2$.\n\n'
            '| Method | Score |\n| --- | ---: |\n| Local | 42 |\n\n'
            '![[images/chart.jpg|Chart]]\n\n'
            '<script>alert(1)</script><p onclick="x()">Visible text.</p>\n',
            encoding='utf-8',
        )
        record = self.prepare()
        self.assertEqual(len(record['images']), 1)
        image = record['images'][0]
        self.assertEqual(image['source_path'], 'ocr/lab/technical-reports/model/images/chart.jpg')
        self.assertTrue(image['site_path'].startswith('assets/textfold-images/lab/model/'))
        self.assertTrue((self.root / image['path']).is_file())

        document = json.loads(gzip.decompress((self.root / record['document_path']).read_bytes()))
        serialized = json.dumps(document).lower()
        self.assertIn('<table', serialized)
        self.assertIn('local', serialized)
        self.assertIn('42', serialized)
        self.assertIn('e=mc^2', serialized)
        self.assertIn(image['site_path'], serialized)
        self.assertNotIn('<script', serialized)
        self.assertNotIn('onclick=', serialized)

    def test_preparation_rejects_stale_pdf_and_summary_bindings(self):
        self.row['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'source checksum'):
            self.prepare()

        self.row['sha256'] = hashlib.sha256(self.pdf.read_bytes()).hexdigest()
        self.summary['source_sha256'] = '1' * 64
        with self.assertRaisesRegex(ValueError, 'Summary source'):
            self.prepare()

    def test_obsidian_embeds_cannot_escape_the_report_images_directory(self):
        self.ocr.write_text('# Model\n\n## 1 Test\n\n![[../outside.jpg]]\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'OCR image'):
            self.prepare()

    def test_index_checks_exported_hashes_without_reading_ocr_or_pdf(self):
        record = self.prepare()
        self.write_index(record)
        self.pdf.unlink()
        self.ocr.unlink()

        # The loader validates only committed package files and the catalog's recorded PDF digest.
        with patch('textfold_sources.checksum', wraps=__import__('textfold_sources').checksum) as checksum:
            loaded = load_textfold_index(self.root, [self.row])
        self.assertEqual(loaded, {record['id']: record})
        checked = [call.args[0] for call in checksum.call_args_list]
        self.assertNotIn(self.pdf, checked)
        self.assertNotIn(self.ocr, checked)

    def test_index_rejects_stale_catalog_and_corrupt_package(self):
        record = self.prepare()
        self.write_index(record)
        stale_row = dict(self.row, sha256='f' * 64)
        with self.assertRaisesRegex(ValueError, 'Stale TextFold source checksum'):
            load_textfold_index(self.root, [stale_row])

        package = self.root / record['document_path']
        package.write_bytes(package.read_bytes() + b'corrupt')
        with self.assertRaisesRegex(ValueError, 'TextFold asset checksum mismatch'):
            load_textfold_index(self.root, [self.row])

    def test_reader_opens_full_text_with_metadata_without_repeating_summary(self):
        from build_readers import build_readers

        record = self.prepare()
        self.write_index(record)
        (self.root / 'site').mkdir()
        shutil.copy2(ROOT / 'site/reader.html', self.root / 'site/reader.html')
        shutil.copytree(ROOT / 'site/vendor/textfold', self.root / 'site/vendor/textfold')

        summary = dict(self.summary, markdown_path='abstracts/lab/model.md')
        markdown = self.root / summary['markdown_path']
        markdown.parent.mkdir(parents=True)
        original_summary = '# Model report\n\nOriginal summary paragraph.\n'
        markdown.write_text(original_summary, encoding='utf-8')
        output = self.root / 'pages'
        metadata = {'model': {'date': '2026-01-02', 'groups': ['language', 'vision']}}
        self.assertEqual(build_readers(self.root, output, {summary['id']: summary}, {}, [self.row], metadata), (2, 0))
        self.assertEqual(markdown.read_text(encoding='utf-8'), original_summary)

        for language, page_rel, expected in (
            ('en', 'abstracts/lab/model.html', '../../fold/lab/model.tfd'),
            ('zh', 'cn/abstracts/lab/model.html', '../../../fold/lab/model.tfd'),
        ):
            with self.subTest(language=language):
                page = output / page_rel
                html_text = page.read_text(encoding='utf-8')
                self.assertIn('<h1>Model report</h1>', html_text)
                self.assertIn('<time datetime="2026-01-02">2026-01-02</time>', html_text)
                self.assertIn('语言与编程 / 视觉理解' if language == 'zh' else 'Language &amp; coding / Vision', html_text)
                self.assertNotIn('id="summary"', html_text)
                self.assertNotIn('Original summary paragraph.', html_text)
                self.assertNotIn('href="#summary"', html_text)
                self.assertIn('<details class="reader-toc" id="contents">', html_text)
                self.assertLess(html_text.index('id="document-header"'), html_text.index('id="contents"'))
                self.assertLess(html_text.index('id="contents"'), html_text.index('id="fulltext"'))
                self.assertNotIn('<iframe', html_text)
                self.assertNotIn('reader-open', html_text)
                self.assertIn('data-textfold-inline', html_text)
                self.assertIn(f'data-ui="{language}"', html_text)
                self.assertIn(f'data-document="{expected}"', html_text)
                self.assertIn('href="#sec-1-introduction"', html_text)
                self.assertTrue((page.parent / expected).resolve().is_file(), expected)
                self.assertTrue((output / 'assets/textfold/inline.js').is_file())
                self.assertTrue((output / 'assets/textfold/inline.css').is_file())
                self.assertTrue((output / 'assets/textfold/inline.html').is_file())

        native_data = output / 'fold/lab/model.tfd'
        self.assertTrue(native_data.is_file())
        data = json.loads(gzip.decompress(native_data.read_bytes()))
        self.assertTrue(data['meta']['static'])
        self.assertFalse(data['meta']['ai_generated'])
        self.assertTrue(any(c.get('title') == 'Abstract' for c in data['chunks']))
        source_image = record['images'][0]
        expected_image = '../../' + source_image['site_path']
        self.assertIn(expected_image, json.dumps(data))
        built_image = output / source_image['site_path']
        self.assertTrue(built_image.is_file())

    def test_static_writer_escapes_payload_json_and_rebases_reader_assets(self):
        site = self.root / 'site'
        shutil.copytree(ROOT / 'site/vendor/textfold', site / 'vendor/textfold')
        output = self.root / 'pages'
        attack = '</script><script>alert(1)</script>'
        record = {
            'id': 'lab:model', 'title': attack, 'source_url': 'https://example.org/report',
        }
        document = {
            'meta': {'id': 'lab:model', 'title': attack, 'source': {'kind': 'markdown'}},
            'atoms': {'a0': {'html': attack, 'src': 'assets/textfold-images/lab/model/chart.webp'}},
            'units': {}, 'chunks': [], 'blocks': [],
        }
        relative = write_static_reader(self.root, output, record, document)
        page = output / relative
        html_text = page.read_text(encoding='utf-8')
        self.assertNotIn(attack, html_text)
        self.assertNotIn('</script><script', html_text.lower())
        self.assertIn('href="https://example.org/report"', html_text)
        self.assertIn("fetch('model.tfd')", html_text)

        payload_text = gzip.decompress(page.with_name('model.tfd').read_bytes()).decode('utf-8')
        self.assertNotIn(attack, payload_text)
        self.assertIn('\\u003c/script>', payload_text)
        data = json.loads(payload_text)
        self.assertEqual(data['katex'], '../../assets/textfold/katex/')
        self.assertEqual(data['atoms']['a0']['src'], '../../assets/textfold-images/lab/model/chart.webp')

    def test_missing_nested_table_image_recovers_exact_pdf_region_and_requires_review(self):
        self.replace_pdf_with_one_page_fixture()
        self.write_table_ocr()

        record = self.prepare()
        self.assertEqual(len(record['images']), 1)
        recovered = record['images'][0]
        self.assertEqual(recovered['source_path'], self.pdf_rel)
        self.assertEqual(recovered['source_sha256'], self.row['sha256'])
        self.assertEqual(recovered['physical_page'], 1)
        for got, expected in zip(recovered['bbox_pdf_points'], (30, 30, 270, 270)):
            self.assertAlmostEqual(got, expected, places=3)
        self.assertEqual(recovered['recovery'], 'recorded-table-region')
        self.assertIs(recovered['visual_review'], False)
        self.assertEqual(record['table_image_fallbacks'][0]['method'], 'recorded-whole-table-image')

        document = json.loads(gzip.decompress((self.root / record['document_path']).read_bytes()))
        payload = json.dumps(document)
        self.assertIn(recovered['site_path'], payload)
        self.assertNotIn('images/missing.jpg', payload)
        self.assertTrue((self.root / recovered['path']).is_file())

        self.write_index(record)
        self.install_static_reader()
        with self.assertRaisesRegex(ValueError, 'Unreviewed TextFold recovered table'):
            from build_readers import build_readers
            build_readers(self.root, self.root / 'pages', {}, {}, [self.row])

    def test_existing_recorded_whole_table_screenshot_needs_no_pdf_fallback(self):
        screenshot = self.workspace / 'images/whole-table-missing.jpg'
        Image.new('RGB', (40, 20), 'white').save(screenshot, 'JPEG')
        self.write_table_ocr()

        record = self.prepare()
        self.assertEqual(len(record['images']), 1)
        image = record['images'][0]
        self.assertEqual(image['source_path'], 'ocr/lab/technical-reports/model/images/whole-table-missing.jpg')
        self.assertNotIn('recovery', image)
        self.assertNotIn('visual_review', image)
        self.assertNotIn('physical_page', image)
        self.assertEqual(record['table_image_fallbacks'][0]['img_path'], 'images/whole-table-missing.jpg')

        self.write_index(record)
        self.install_static_reader()
        from build_readers import build_readers
        self.assertEqual(build_readers(self.root, self.root / 'pages', {}, {}, [self.row]), (0, 0))
        self.assertTrue((self.root / 'pages' / image['site_path']).is_file())


if __name__ == '__main__':
    unittest.main()
