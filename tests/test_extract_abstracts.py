"""Guard source section boundaries and prevent false verification claims."""
import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    import pdfminer
except ModuleNotFoundError:
    raise unittest.SkipTest('Install requirements-abstracts.txt for source summary tests.')

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

spec = importlib.util.spec_from_file_location('extract_abstracts', Path(__file__).resolve().parents[1] / 'scripts/extract_abstracts.py')
extract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extract)


def block(text, font=11, bottom=200):
    return dict(text=text, font_size=font, bbox=[50, bottom, 500, bottom + 20])


def page(*blocks):
    return dict(width=600, height=800, blocks=list(blocks))


class AbstractTests(unittest.TestCase):
    def test_inline_abstract_keeps_original_heading(self):
        self.assertEqual(extract.heading('Abstract. We describe a model.'), ('abstract', 0, 'Abstract.', 'We describe a model.\n'))

    def test_wrapped_summary_heading(self):
        self.assertEqual(extract.heading('Executive\nSummary\nOriginal words.'), ('executive_summary', 1, 'Executive Summary', 'Original words.'))

    def test_contents_is_not_executive_summary(self):
        text = 'This is the actual source paragraph. ' * 6
        pages = [page(block('Contents'), block('Executive Summary\n2')),
                 page(block('Executive Summary', 16), block(text), block('1 Introduction', 16))]
        section = extract.choose_section(pages)
        self.assertEqual(section['raw_text'], text.strip())
        self.assertEqual([f['page'] for f in section['fragments']], [2])

    def test_description_stops_before_model_dependencies(self):
        text = 'The model supports text and image inputs. ' * 4
        section = extract.choose_section([page(block('Description', 16), block(text), block('Model dependencies', 16), block('Earlier model.'))])
        self.assertNotIn('Earlier model', section['raw_text'])
        self.assertTrue(section['boundary_found'])

    def test_unlabelled_opening_is_not_invented_abstract(self):
        text = 'We introduce a model that supports new research tasks. ' * 5
        section = extract.choose_section([page(block('Report title', 20), block(text), block('1. Introduction', 15))])
        self.assertEqual(section['section_type'], 'opening_summary')
        self.assertIsNone(section['source_heading'])

    def test_independent_number_disagreement_requires_review(self):
        text = 'We introduce a model trained with 100 examples and report its measured performance. ' * 3
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'source.pdf').write_bytes(b'fixture')
            row = dict(vendor='openai', title='Example', local_path='source.pdf', sha256=hashlib.sha256(b'fixture').hexdigest(), version='v1', document_type='technical_report', source_url='https://example.org')
            cache = dict(pypdf_pages=[text.replace('100', '10')], pdfminer_pages=[page(block('Abstract', 15), block(text), block('1 Introduction', 15))], page_count=1)
            with patch.object(extract, 'ROOT', root), patch.object(extract, 'extract_cached', return_value=cache):
                report = extract.extract_report(dict(row=row, slug='example', models=['Example']), root, 12)
            self.assertEqual(report['status'], 'needs_review')
            self.assertFalse(report['manual_review'])
            self.assertIn('100', report['text'])

    def test_short_model_description_is_preserved(self):
        text = 'Description: The model generates high-quality audio from a text prompt.'
        section = extract.choose_section([page(block(text), block('Inputs: Text'))])
        self.assertEqual(section['source_heading'], 'Description:')
        self.assertTrue(section['boundary_found'])

    def test_split_introduction_and_caption_end_abstract(self):
        text = 'We introduce a model and report original experimental results. ' * 4
        section = extract.choose_section([page(block('Abstract', 12), block(text), block('Figure 1: Benchmark comparison.', 9), block('1', 12), block('Introduction', 12), block('This is not the abstract.'))])
        self.assertEqual(section['raw_text'], text.strip())
        self.assertNotIn('Benchmark', section['raw_text'])

    def test_margin_arxiv_stamp_does_not_make_a_contents_page(self):
        stamp = block('1\n2\n3\n4\n5\n6\n7\n8\n9')
        stamp['bbox'] = [16, 200, 36, 500]
        source = page(stamp, block('Abstract'), block('1 Introduction\n1.1 First\n1.2 Second\n1.3 Third'))
        self.assertFalse(extract.contents_page(source))

    def test_normalization_does_not_ignore_number_changes(self):
        self.assertNotEqual(extract.compact('100 tokens'), extract.compact('10 tokens'))
        self.assertEqual(extract.compact('ofﬁcial\nsource'), extract.compact('official source'))


if __name__ == '__main__':
    unittest.main()
