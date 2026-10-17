import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

try:
    import pymupdf
except ImportError:
    raise unittest.SkipTest('Install requirements-figures.txt to test figure exports')

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from extract_figures import validate_selection
import extract_figures


class FigureSelectionTests(unittest.TestCase):
    def setUp(self):
        self.document = pymupdf.open()
        self.document.new_page(width=612, height=792)
        self.report = {'id': 'vendor:report', 'source_sha256': 'source-hash'}
        self.figure = dict(page=1, bbox=[20, 30, 400, 500], role='architecture', visual_review=True)
        self.selection = dict(source_sha256='source-hash', figures=[self.figure])

    def tearDown(self):
        self.document.close()

    def test_bottom_left_or_out_of_page_bounds_are_rejected(self):
        for box in ([20, 500, 400, 30], [-2, 0, 400, 500], [20, 30, 620, 500]):
            with self.subTest(box=box), self.assertRaises(ValueError):
                self.figure['bbox'] = box
                validate_selection(self.selection, self.report, self.document)

    def test_stale_source_selection_is_rejected(self):
        self.selection['source_sha256'] = 'older-revision'
        with self.assertRaisesRegex(ValueError, 'Stale'):
            validate_selection(self.selection, self.report, self.document)

    def test_physical_page_is_one_based(self):
        for page in (0, 2):
            with self.subTest(page=page), self.assertRaises(ValueError):
                self.figure['page'] = page
                validate_selection(self.selection, self.report, self.document)

    def test_unreviewed_region_is_rejected(self):
        self.figure['visual_review'] = False
        with self.assertRaises(ValueError):
            validate_selection(self.selection, self.report, self.document)

    def test_duplicate_crops_are_rejected(self):
        self.selection['figures'].append(dict(self.figure))
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            validate_selection(self.selection, self.report, self.document)

    def test_cut_caption_is_rejected(self):
        self.figure['caption_bbox'] = [20, 490, 400, 530]
        with self.assertRaisesRegex(ValueError, 'full original caption'):
            validate_selection(self.selection, self.report, self.document)

    def test_invented_caption_is_rejected(self):
        self.figure['caption'] = 'Figure 1: An invented architecture.'
        with self.assertRaisesRegex(ValueError, 'Caption does not match'):
            validate_selection(self.selection, self.report, self.document)

    def test_reviewed_line_wrap_restoration_preserves_hyphens_and_numbers(self):
        self.document[0].insert_text((30, 120), 'Figure 1: A con-\nventional model with state-of-the-art results at 90%.')
        self.figure['bbox'] = [20, 30, 590, 500]
        caption = 'Figure 1: A conventional model with state-of-the-art results at 90%.'
        self.figure['caption'] = caption
        validate_selection(self.selection, self.report, self.document)
        for changed in (caption.replace('state-of-the-art', 'stateoftheart'), caption.replace('90%', '91%')):
            with self.subTest(caption=changed), self.assertRaisesRegex(ValueError, 'Caption does not match'):
                self.figure['caption'] = changed
                validate_selection(self.selection, self.report, self.document)

    def test_clipped_axis_label_is_rejected(self):
        self.document[0].insert_text((10, 100), 'axis label')
        with self.assertRaisesRegex(ValueError, 'cuts source text'):
            validate_selection(self.selection, self.report, self.document)

    def test_repeat_export_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source.pdf'
            self.document[0].draw_rect(pymupdf.Rect(30, 40, 150, 100))
            self.document[0].insert_text((30, 130), 'Figure 1: Pipeline')
            self.document.save(source)
            report = dict(id='moonshot:example', vendor='moonshot', title='Example', models=['Example'],
                          document_type='technical_report', source_pdf='source.pdf', source_url='https://example.org',
                          source_sha256=extract_figures.sha(source), source_version='test-v1')
            selection = dict(id=report['id'], source_sha256=report['source_sha256'], inspected_pages=[1],
                             figures=[dict(page=1, figure_number='1', role='architecture',
                                           caption='Figure 1: Pipeline', bbox=[20, 30, 180, 150], visual_review=True)])
            with patch.object(extract_figures, 'ROOT', root):
                first = extract_figures.export(root/'figures', [selection], [report])[0]['figures'][0]
                second = extract_figures.export(root/'figures', [selection], [report])[0]['figures'][0]
            self.assertEqual(first['pdf_sha256'], second['pdf_sha256'])
            self.assertEqual(first['png_sha256'], second['png_sha256'])


if __name__ == '__main__':
    unittest.main()
