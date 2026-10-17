"""Guard source section boundaries and prevent false verification claims."""
import hashlib
import csv
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

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
    def test_reader_alt_labels_preserve_table_and_figure_kinds(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(extract, 'ROOT', Path(directory)):
            root = Path(directory)
            (root / 'figures').mkdir()
            figures = [dict(figure_number=number, source_kind=kind, caption='',
                            png_path=f'figures/example-{i}.png', page=1)
                       for i, (number, kind) in enumerate([('1', 'table'), (None, 'table'),
                                                          ('2', 'figure'), ('Table 3', 'table')])]
            (root / 'figures/index.json').write_text(json.dumps({'reports': [
                dict(id='openai:example', source_sha256='source', figures=figures)]}))
            report = dict(id='openai:example', vendor='openai', title='Example',
                          source_url='https://example.com', source_sha256='source',
                          source_heading=None, text='Original passage.')
            extract.write_outputs(root / 'abstracts', [report], [])
            body = (root / 'abstracts/openai/example.md').read_text()
            for label in ('Table 1', 'Table', 'Figure 2', 'Table 3'):
                self.assertIn(f'![{label}](', body)
            self.assertNotIn('![Figure 1]', body)

    def test_native_cache_preserves_unpaired_surrogates(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory)
            native = 'Original parser text with an unmapped glyph: \ud835'
            reader = Mock(pages=[Mock(extract_text=Mock(return_value=native))])
            with patch.object(extract, 'PdfReader', return_value=reader) as read, \
                    patch.object(extract, 'extract_pages', return_value=[]):
                first = extract.extract_cached('source.pdf', 'source-hash', cache, 12)
                second = extract.extract_cached('source.pdf', 'source-hash', cache, 12)
            self.assertEqual(first['pypdf_pages'], [native])
            self.assertEqual(second, first)
            self.assertEqual(read.call_count, 1)

    def test_reviewed_page_break_reflows_without_merging_real_paragraphs(self):
        text = 'First real paragraph.\n\nA sentence ends the page with In\n\nmulti-turn testing, it continues.\n\nAnother real paragraph.'
        report = dict(id='lab:report', source_pdf='source.pdf', source_sha256='source', text=text)
        layout = dict(source_sha256='source', text_sha256=hashlib.sha256(text.encode()).hexdigest(),
                      join_after=[1], review_method='visual_source_page')
        rendered = extract.markdown_passage(report, layout)
        self.assertEqual(rendered, 'First real paragraph.\n\nA sentence ends the page with In multi-turn testing, it continues.\n\nAnother real paragraph.')
        self.assertEqual(report['text'], text)
        self.assertEqual(extract.markdown_passage(report), text)
        for changed in [{**report, 'source_sha256': 'new-source'}, {**report, 'text': text+' changed'},
                        {**report, 'source_pdf': None}]:
            with self.assertRaisesRegex(ValueError, 'Stale paragraph'):
                extract.markdown_passage(changed, layout)
        for joins in [[-1], [3], [1, 1], [True]]:
            with self.assertRaisesRegex(ValueError, 'Invalid paragraph'):
                extract.markdown_passage(report, {**layout, 'join_after': joins})

    def test_source_bound_passage_repair_is_exact_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            old_root = extract.ROOT
            extract.ROOT = root
            try:
                original = 'Autoregressive\n\nas Transformer-based policies.'
                fixed = 'Autoregressive sequence models, such as Transformer-based policies.'
                repair = dict(
                    id='lab:fast', source_sha256='source',
                    input_text_sha256=hashlib.sha256(original.encode()).hexdigest(),
                    output_text_sha256=hashlib.sha256(fixed.encode()).hexdigest(),
                    source_regions=[dict(page=1, source_fragment_index=0,
                                        raw_text_sha256=hashlib.sha256('Autoregressive'.encode()).hexdigest())],
                    edits=[dict(match='Autoregressive\n\nas Transformer-based',
                                replacement='Autoregressive sequence models, such as Transformer-based',
                                match_sha256=hashlib.sha256('Autoregressive\n\nas Transformer-based'.encode()).hexdigest())])
                (root/'abstracts').mkdir()
                (root/'abstracts/reviews.json').write_text(json.dumps(dict(passage_repairs=[repair])))
                report = dict(id='lab:fast', source_sha256='source', text=original,
                              source_fragments=[dict(page=1, text='Autoregressive')])
                extract.apply_passage_repairs(report)
                self.assertEqual(report['text'], fixed)
                self.assertEqual(report['status'], 'source_reviewed')
                extract.apply_passage_repairs(report)
                self.assertEqual(report['text'], fixed)
                changed = {**report, 'text': fixed + ' stale'}
                with self.assertRaisesRegex(ValueError, 'Stale passage repair input'):
                    extract.apply_passage_repairs(changed)
            finally:
                extract.ROOT = old_root

    def test_unlabelled_embodied_overview_precedes_introduction(self):
        text = 'Building capable embodied agents requires physical understanding. ' * 4
        section = extract.choose_section([page(block('Paper title', 20), block(text, 11),
                                              block('1 Introduction', 13), block('Longer background discussion. ' * 5, 11))])
        self.assertEqual(section['section_type'], 'opening_summary')
        self.assertIsNone(section['source_heading'])
        self.assertEqual(section['raw_text'], text.strip())

    def test_numbered_descriptive_overview_retains_actual_heading(self):
        text = 'The model generates video and synchronized audio from user instructions. ' * 4
        section = extract.choose_section([page(block('System card', 20)),
            page(block('1 Overview of Example 2', 14), block(text, 11),
                 block('2 Model data', 14), block('Unrelated training details. ' * 5, 11))])
        self.assertEqual(section['section_type'], 'overview')
        self.assertEqual(section['source_heading'], '1 Overview of Example 2')
        self.assertEqual(section['raw_text'], text.strip())
        self.assertEqual(section['fragments'][0]['page'], 2)

    def test_model_summary_stops_before_model_details(self):
        text = 'The next iteration in our speech synthesis family generates natural speech. ' * 4
        section = extract.choose_section([page(block('Model card', 20),
            block('Model summary', 16), block(text, 11), block('About this model', 16),
            block('Voice prompting and distribution details. ' * 4, 11))])
        self.assertEqual(section['section_type'], 'summary')
        self.assertEqual(section['source_heading'], 'Model summary')
        self.assertEqual(section['raw_text'], text.strip())
        self.assertTrue(section['boundary_found'])

    def test_named_title_page_opening_is_fallback_without_invented_heading(self):
        for name in ('Codex', 'GPT-5-Codex'):
            with self.subTest(name=name):
                text = f'{name} is a coding agent that executes tasks in an isolated environment. ' * 4
                section = extract.choose_section([page(block('System card', 20), block(text, 11),
                                                       block('1 Safety evaluations', 14))])
                self.assertEqual(section['section_type'], 'opening_summary')
                self.assertIsNone(section['source_heading'])
                self.assertEqual(section['raw_text'], text.strip())
                labelled = extract.choose_section([page(block(text, 11)),
                    page(block('Overview', 14), block('Existing labelled overview. ' * 6, 11))])
                self.assertEqual(labelled['section_type'], 'overview')
                self.assertEqual(labelled['source_heading'], 'Overview')
        self.assertIsNone(extract.choose_section([page(block('Figure 1 is a benchmark comparison. ' * 10, 11))]))

    def test_introduction_continues_below_an_interleaved_figure(self):
        first = 'This report describes an embodied model and evaluates the model’s'
        second = 'proficiency in the physical tasks and its measured safety outcomes.'
        section = extract.choose_section([page(block('1 Introduction', 12), block(first, 10)),
                                          page(block('Figure 1 | Benchmark setup.', 9), block(second, 10),
                                               block('2 Evaluation', 12))])
        self.assertEqual(section['raw_text'], first+'\n\n'+second)
        self.assertTrue(section['boundary_found'])
        self.assertNotIn('Benchmark setup', section['raw_text'])

    def test_abbreviated_figure_caption_is_not_an_abstract_continuation(self):
        opening = 'We present a generalist policy with a complete original abstract. ' * 3
        ending = 'The original abstract ends with measured task results.'
        section = extract.choose_section([page(block('Abstract—' + opening, 9)),
                                          page(block(ending, 9), block('Fig. 2: This is an image caption.', 10),
                                               block('I. INTRODUCTION', 10))])
        self.assertEqual(section['raw_text'], opening.strip()+'\n\n'+ending)
        self.assertTrue(section['boundary_found'])
        self.assertNotIn('image caption', section['raw_text'])

    def test_roman_ieee_heading_ends_abstract_before_main_text(self):
        text = 'We present the policy and its measured robot control results. ' * 3
        section = extract.choose_section([page(block('Abstract—' + text, 9),
                                              block('I. INTRODUCTION & RELATED WORK', 10),
                                              block('This is not the abstract.', 10))])
        self.assertTrue(section['boundary_found'])
        self.assertEqual(section['raw_text'], text.strip())

    def test_line_positioned_abstract_keeps_smaller_body_font(self):
        lines = ['The model learns robotic manipulation from diverse tasks and embodiments.',
                 'Its original evaluation reports generalization across these source tasks.']
        section = extract.choose_section([page(block('Abstract', 12),
                                              *(block(line, 10) for line in lines),
                                              block('1 Introduction', 12))])
        self.assertEqual(section['raw_text'], '\n\n'.join(lines))
        self.assertTrue(section['boundary_found'])

    def test_explicit_archive_reader_does_not_require_a_current_model(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = dict(vendor='google', slug='rt-1', title='RT-1', reading_models=['RT-1'])
            (root/'sources.json').write_text(json.dumps([source]))
            (root/'model-coverage.json').write_text(json.dumps(dict(models=[])))
            rows = [dict(vendor='google', title='RT-1', local_path='pdfs/old.pdf', sha256='1'*64,
                         status='archived', source_updated_date='2022-12-13', retrieved_at='2026-10-14'),
                    dict(vendor='google', title='RT-1', local_path='pdfs/revised.pdf', sha256='2'*64,
                         status='archived', source_updated_date='2023-08-03', retrieved_at='2026-10-14')]
            with (root/'catalog.csv').open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
            with patch.object(extract, 'ROOT', root):
                reports, missing = extract.current_reports()
                self.assertEqual(missing, [])
                self.assertEqual(len(reports), 1)
                self.assertEqual(reports[0]['reader_scope'], 'archive')
                self.assertEqual(reports[0]['models'], ['RT-1'])
                self.assertEqual(reports[0]['row']['local_path'], 'pdfs/revised.pdf')
                source['reading_models'] = []
                (root/'sources.json').write_text(json.dumps([source]))
                with self.assertRaisesRegex(ValueError, 'Invalid archive reading'):
                    extract.current_reports()

    def test_superseded_pdf_reader_is_retained_with_exact_historical_binding(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'abstracts').mkdir()
            (root/'sources.json').write_text('[]')
            (root/'model-coverage.json').write_text(json.dumps(dict(models=[])))
            row = dict(vendor='openai', local_path='pdfs/openai/old.pdf', sha256='1'*64, status='archived')
            with (root/'catalog.csv').open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=list(row)); writer.writeheader(); writer.writerow(row)
            old = dict(id='openai:old', source_pdf=row['local_path'], source_sha256=row['sha256'], models=['Old'])
            (root/'abstracts/index.json').write_text(json.dumps(dict(reports=[old])))
            with patch.object(extract, 'ROOT', root):
                reports, missing = extract.current_reports()
                self.assertEqual(missing, [])
                self.assertEqual(reports[0]['reader_scope'], 'historical')
                self.assertEqual(reports[0]['row']['sha256'], row['sha256'])
                old['source_sha256'] = '2'*64
                (root/'abstracts/index.json').write_text(json.dumps(dict(reports=[old])))
                with self.assertRaisesRegex(ValueError, 'Stale historical'):
                    extract.current_reports()

    def test_word_positioned_pdf_preserves_genuine_hyphens_and_numbers(self):
        self.assertTrue(extract.source_agrees('good-faith model', 'good-\nfaith\n model'))
        self.assertTrue(extract.source_agrees('two-thirds', 'two-\nthirds'))
        self.assertFalse(extract.source_agrees('0.98 success', '0.89 success'))
        self.assertFalse(extract.source_agrees('-3 result', '3 result'))

    def test_multi_page_review_checks_each_range_and_character_inventory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'abstracts').mkdir()
            native = ['first page original', 'second page original']
            ranges = [dict(page=i+1, start_offset=0, end_offset=len(t),
                           raw_text_sha256=hashlib.sha256(t.encode()).hexdigest()) for i, t in enumerate(native)]
            review = dict(id='lab:example', source_sha256='source', ranges=ranges)
            path = root / 'abstracts/reviews.json'
            path.write_text(json.dumps(dict(reviews=[review])))
            report = dict(id='lab:example', source_sha256='source', source_pdf='example.pdf',
                          raw_text='\n'.join(native), cross_check={'matched_fragments': 1, 'total_fragments': 2})
            with patch.object(extract, 'ROOT', root), patch.object(extract, 'extract_cached', return_value=dict(pypdf_pages=native)):
                result = extract.apply_source_review(dict(report), root, 12)
                self.assertEqual(result['pages'], [1, 2])
                self.assertEqual(result['status'], 'source_reviewed')
                self.assertEqual(result['initial_cross_check'], report['cross_check'])
                changed = {**report, 'raw_text': report['raw_text'] + ' invented'}
                with self.assertRaisesRegex(ValueError, 'changes source characters'):
                    extract.apply_source_review(changed, root, 12)
                ranges[1]['raw_text_sha256'] = '0' * 64
                path.write_text(json.dumps(dict(reviews=[review])))
                with self.assertRaisesRegex(ValueError, 'source text changed'):
                    extract.apply_source_review(dict(report), root, 12)

    def test_inline_abstract_keeps_original_heading(self):
        self.assertEqual(extract.heading('Abstract. We describe a model.'), ('abstract', 0, 'Abstract.', 'We describe a model.\n'))

    def test_ieee_dash_abstract_continues_until_roman_introduction(self):
        opening = 'We present a robot model with original experiments and preserve the complete abstract. ' * 3
        continuation = 'The abstract continues on the next page with its final evaluation results.'
        section = extract.choose_section([page(block('Abstract—' + opening)),
                                          page(block(continuation), block('I. INTRODUCTION', 8.4), block('Not the abstract.'))])
        self.assertEqual(section['source_heading'], 'Abstract—')
        self.assertEqual([f['page'] for f in section['fragments']], [1, 2])
        self.assertNotIn('Not the abstract', section['raw_text'])
        self.assertTrue(section['boundary_found'])

    def test_link_widgets_are_not_part_of_abstract(self):
        text = 'We introduce a world model and report its original results. ' * 3
        section = extract.choose_section([page(block('Abstract', 10), block(text, 10),
                                              block('Open-Source Code', 10), block('Code and dataset links.', 10))])
        self.assertEqual(section['raw_text'], text.strip())
        self.assertTrue(section['boundary_found'])

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

    def test_model_architecture_table_is_source_passage_not_abstract(self):
        label = block('Model architecture', bottom=600)
        label['bbox'] = [50, 600, 180, 620]
        text = 'The model uses a mixture of experts with sparse attention and reports the original architecture details. ' * 3
        value = block(text, bottom=600)
        value['bbox'] = [220, 400, 550, 620]
        section = extract.choose_section([page(label, value)])
        self.assertEqual(section['section_type'], 'model_architecture')
        self.assertEqual(section['source_heading'], 'Model architecture')
        self.assertEqual(section['raw_text'], text.strip())
        self.assertTrue(section['boundary_found'])

    def test_merged_architecture_label_stops_before_next_table_row(self):
        text = 'The model uses sparse attention and describes its original training architecture in this table.'
        section = extract.choose_section([page(block('Model architecture  ' + text),
                                              block('Modalities'), block('Text and image inputs.'))])
        self.assertEqual(section['source_heading'], 'Model architecture')
        self.assertEqual(section['raw_text'], text)
        self.assertNotIn('Modalities', section['raw_text'])

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
