"""Nine browse groups stay a complete, unambiguous layer over the task tags."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from model_groups import CATEGORY_GROUPS, TAG_TO_GROUP, model_groups


class ModelGroupTests(unittest.TestCase):
    def test_every_task_tag_maps_into_exactly_one_group(self):
        import archive_reports
        tags = set(archive_reports.MODEL_CATEGORIES)
        self.assertEqual(set(TAG_TO_GROUP), tags)
        grouped = [tag for _, _, group_tags in CATEGORY_GROUPS.values() for tag in group_tags]
        self.assertEqual(len(grouped), len(set(grouped)))
        self.assertEqual(sorted(grouped), sorted(tags))

    def test_model_groups_follow_group_order_and_ignore_unknown_tags(self):
        self.assertEqual(
            model_groups(['video', 'general', 'ocr', 'world', 'unknown_tag']),
            ['language', 'vision', 'video', 'world'])
        self.assertEqual(model_groups([]), [])
        self.assertEqual(model_groups(['coding', 'general', 'coding']), ['language'])

    def test_group_labels_are_bilingual(self):
        for en, cn, _ in CATEGORY_GROUPS.values():
            self.assertTrue(en and cn)


class TimelineGroupInheritanceTests(unittest.TestCase):
    def test_history_groups_and_coverage_tags_flow_as_groups(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
        from model_timeline import timeline_models
        coverage = {'models': [dict(vendor='openai', model='Current model', source_url='https://example.org/c',
                                    latest_categories=['general', 'coding'])]}
        history = {'models': [dict(vendor='openai', model='Old model', source_url='https://example.org/o',
                                   report_slugs=[], release_date='2023-01-01',
                                   release_source_url='https://example.org/o', release_evidence='Official page.',
                                   groups=['vision', 'language'])],
                   'coverage_aliases': []}
        sources = [dict(vendor='openai', slug='c', title='C', document_type='technical_report')]
        V = {'openai': 'OpenAI'}
        entries = {m['model']: m for m in timeline_models(coverage, history, sources, V)}
        self.assertEqual(entries['Current model']['categories'], ['language'])
        self.assertEqual(entries['Old model']['categories'], ['vision', 'language'])
        history['models'][0]['groups'] = ['not_a_group']
        with self.assertRaisesRegex(ValueError, 'Unknown timeline model group'):
            timeline_models(coverage, history, sources, V)

    def test_reader_meta_line_assembles_date_then_groups(self):
        import sys
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
        import build_readers
        body = '<h1>Report title</h1>'
        out = build_readers.inject_reader_meta(
            body, {'date': '2024-10-22', 'groups': ['vision', 'language']}, False)
        self.assertIn('<time datetime="2024-10-22">2024-10-22</time>', out)
        self.assertIn('<span>Vision / Language &amp; coding</span>', out)
        self.assertTrue(out.index('<time') < out.index('<span>'))
        self.assertEqual(build_readers.inject_reader_meta(body, {}, True), body)


class LatestIndexGroupCellsTests(unittest.TestCase):
    def setUp(self):
        import archive_reports
        self.archive = archive_reports
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.old_cwd = Path.cwd()
        self.archive.ROOT = self.root
        import os
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.old_cwd)

    def test_latest_table_cells_show_browse_groups(self):
        self.root.joinpath('sources.json').write_text(json.dumps([]))
        model = dict(vendor='openai', model='Example model', source_url='https://example.org/m',
                     latest_categories=['general', 'coding'])
        (self.root / 'model-coverage.json').write_text(json.dumps(
            dict(checked_at='2026-10-15', models=[model])))
        self.archive.render_model_coverage([])
        text = (self.root / 'LATEST_MODELS.md').read_text()
        self.assertIn('| Language & coding | Example model |', text)
        self.assertNotIn('General & reasoning', text)
        cn = (self.root / 'LATEST_MODELS_CN.md').read_text()
        self.assertIn('| 语言与编程 | Example model |', cn)


if __name__ == '__main__':
    unittest.main()
