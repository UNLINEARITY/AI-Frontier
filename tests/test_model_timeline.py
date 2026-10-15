"""Model releases must not be inferred from paper revisions or aggregate coverage."""
import sys
import json
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from model_timeline import timeline_models


class TimelineTests(unittest.TestCase):
    def setUp(self):
        self.sources = [dict(vendor='lab', slug='report', published_date='2026-01-01',
                             source_updated_date='2026-09-01')]
        self.model = dict(vendor='lab', model='Model', source_url='https://example.org/model',
                          report_slugs=['report'], note_en='Official named-model announcement.')

    def resolve(self, models=None, history=None):
        return timeline_models({'models': models or [self.model]}, history or {}, self.sources, {'lab': 'Lab'})

    def test_missing_date_never_uses_report_or_review_dates(self):
        self.model.update(reviewed_at='2026-10-14', source_updated_date='2026-09-01')
        self.assertEqual(self.resolve()[0]['release_date'], '')

    def test_history_and_current_coverage_are_one_model_even_when_retired(self):
        self.model.update(lifecycle='discontinued', latest_categories=['general'])
        result = self.resolve(history={'models': [dict(self.model, model='MODEL')]})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['report_slugs'], ['report'])

    def test_aggregate_variants_need_explicit_joint_release_evidence(self):
        self.model.update(model='A / B', release_date='2026-04-01')
        history = {'coverage_aliases': [dict(vendor='lab', coverage_model='A / B', models=['A', 'B'])]}
        result = self.resolve(history=history)
        self.assertEqual([m['release_date'] for m in result], ['', ''])
        self.assertEqual([m['report_slugs'] for m in result], [[], []])
        self.assertEqual([m['search_aliases'] for m in result], [[], []])
        history['coverage_aliases'][0].update(shared_release=True, shared_reports=True)
        result = self.resolve(history=history)
        self.assertEqual([m['release_date'] for m in result], ['2026-04-01', '2026-04-01'])
        self.assertEqual([m['report_slugs'] for m in result], [['report'], ['report']])

    def test_shared_report_does_not_overwrite_individual_variant_launch_days(self):
        self.model.update(model='A / B', release_date='2026-04-01')
        history = {'models': [dict(self.model, model='A', release_date='2026-04-01'),
                              dict(self.model, model='B', release_date='2026-05-02')],
                   'coverage_aliases': [dict(vendor='lab', coverage_model='A / B', models=['A', 'B'], shared_reports=True)]}
        result = self.resolve(history=history)
        self.assertEqual([(m['model'], m['release_date']) for m in result], [('A', '2026-04-01'), ('B', '2026-05-02')])
        self.assertTrue(all(m['report_slugs'] == ['report'] for m in result))

    def test_invalid_partial_conflicting_dates_and_stale_aliases_fail(self):
        for released in ('2026-02-30', '2026-02', '20260201'):
            with self.subTest(released=released), self.assertRaises(ValueError):
                self.resolve(models=[dict(self.model, release_date=released)])
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            self.resolve(models=[dict(self.model, release_date='2026-02-01')],
                         history={'models': [dict(self.model, release_date='2026-02-02')]})
        with self.assertRaisesRegex(ValueError, 'Invalid timeline coverage alias'):
            self.resolve(history={'coverage_aliases': [dict(vendor='lab', coverage_model='Unknown', models=['Model'])]})

    def test_release_order_is_old_to_new_and_undated_last(self):
        result = self.resolve(models=[self.model, dict(self.model, model='New', release_date='2026-02-01'),
                                     dict(self.model, model='Old', release_date='2025-01-01')])
        self.assertEqual([m['model'] for m in result], ['Old', 'New', 'Model'])

    def test_unknown_reports_and_unsafe_sources_fail(self):
        with self.assertRaisesRegex(ValueError, 'Unregistered timeline report'):
            self.resolve(models=[dict(self.model, report_slugs=['unregistered'])])
        with self.assertRaisesRegex(ValueError, 'Unsafe timeline source'):
            self.resolve(models=[dict(self.model, source_url='javascript:alert(1)')])

    def test_repository_timeline_identity_and_release_evidence(self):
        root = Path(__file__).resolve().parents[1]
        from archive_reports import VENDORS
        coverage = json.loads((root / 'model-coverage.json').read_text())
        history = json.loads((root / 'model-history.json').read_text())
        sources = json.loads((root / 'sources.json').read_text())
        result = timeline_models(coverage, history, sources, VENDORS)
        identities = [(m['vendor'], m['model'].casefold()) for m in result]
        self.assertEqual(len(identities), len(set(identities)))
        self.assertIn(('openai', 'sora 2'), identities)
        self.assertNotIn(('openai', 'gpt-5.6 august safety update'), identities)
        self.assertNotIn(('openai', 'gpt-5.6 preview'), identities)
        for model in result:
            if model['release_date']:
                self.assertTrue(model['release_source_url'].startswith('https://'))
                self.assertTrue(model['release_evidence'])


if __name__ == '__main__':
    unittest.main()
