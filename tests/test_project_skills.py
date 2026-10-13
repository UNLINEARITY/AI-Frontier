"""Check restoration and handoff safeguards with isolated local fixtures."""
import csv
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


check = module('af_check', ROOT / '.agents/skills/af-validate/scripts/check_project.py')
restore = module('af_restore', ROOT / '.agents/skills/af-collect-reports/scripts/restore_pdfs.py')


class SkillToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'scripts').mkdir()
        (self.root / 'scripts/archive_reports.py').write_text((ROOT / 'scripts/archive_reports.py').read_text())
        for directory in ('abstracts/openai', 'figures/openai/example'):
            (self.root / directory).mkdir(parents=True)
        self.pdf = b'%PDF-fixture-bytes'
        source_sha = hashlib.sha256(self.pdf).hexdigest()
        self.path = self.root / 'pdfs/openai/technical-reports/example.pdf'
        self.row = dict(local_path='pdfs/openai/technical-reports/example.pdf', status='archived', sha256=source_sha,
                        pages='2', size_bytes=str(len(self.pdf)), pdf_url='https://example.org/report.pdf', resolved_url='')
        with (self.root / 'catalog.csv').open('w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=list(self.row));writer.writeheader();writer.writerow(self.row)
        self.report = dict(id='openai:example', vendor='openai', source_pdf=self.row['local_path'], source_sha256=source_sha,
                           text='Original text.', text_sha256=hashlib.sha256(b'Original text.').hexdigest(),
                           pages=[1], status='cross_checked', markdown_path='abstracts/openai/example.md')
        self.model = dict(vendor='openai', model='Example', source_url='https://example.org/report',
                          report_slugs=['example'], latest_categories=['general'])
        self.save('sources.json', [dict(vendor='openai', slug='example', document_type='technical_report', source_url='https://example.org/report')])
        self.save('model-coverage.json', dict(checked_at='2026-10-13', models=[self.model]))
        self.save('abstracts/index.json', dict(reports=[self.report]))
        self.save('figures/index.json', dict(reports=[dict(id=self.report['id'], source_sha256=source_sha, figures=[])]))
        self.save('figures/selections.json', [dict(id=self.report['id'], source_sha256=source_sha, figures=[])])
        (self.root / self.report['markdown_path']).write_text('# Example\n\nOriginal text.\n')

    def save(self, name, value):
        (self.root / name).write_text(json.dumps(value))

    def test_pdf_free_clone_passes_but_local_source_check_fails(self):
        errors, _ = check.validate(self.root)
        self.assertEqual(errors, [])
        errors, _ = check.validate(self.root, local_pdfs=True)
        self.assertTrue(any('local source PDF' in e for e in errors))

    def test_duplicate_latest_slot_and_stale_provenance_fail(self):
        self.save('model-coverage.json', dict(models=[self.model, {**self.model, 'model':'Another'}]))
        self.report['source_sha256'] = '0' * 64
        self.save('abstracts/index.json', dict(reports=[self.report]))
        errors, _ = check.validate(self.root)
        self.assertTrue(any('Duplicate active latest slot' in e for e in errors))
        self.assertTrue(any('Stale summary source' in e for e in errors))

    def test_public_pdf_link_is_rejected(self):
        (self.root / self.report['markdown_path']).write_text('# Example\n\nOriginal text.\n\n[PDF](../../pdfs/openai/technical-reports/example.pdf)\n')
        errors, _ = check.validate(self.root)
        self.assertTrue(any('Public local PDF link' in e for e in errors))

    def test_missing_png_and_visual_review_fail(self):
        figure = dict(page=1, bbox=[0,0,10,10], caption='Caption', png_path='figures/openai/example/figure-01.png',
                      png_sha256='0'*64, pdf_path='figures/openai/example/figure-01.pdf', pdf_sha256='0'*64)
        self.save('figures/index.json', dict(reports=[dict(id=self.report['id'], source_sha256=self.report['source_sha256'], figures=[figure])]))
        self.save('figures/selections.json', [dict(id=self.report['id'], source_sha256=self.report['source_sha256'], figures=[dict(page=1,bbox=[0,0,10,10],visual_review=False)])])
        errors, _ = check.validate(self.root)
        self.assertTrue(any('Missing/changed PNG' in e for e in errors))
        self.assertTrue(any('Missing visual figure review' in e for e in errors))

    def test_restore_dry_run_does_not_download_or_write(self):
        with patch.object(restore.urllib.request, 'urlopen') as request:
            self.assertEqual(restore.restore(self.root), [('openai:example','missing')])
            request.assert_not_called()
        self.assertFalse(self.path.exists())

    def test_restore_exact_bytes_and_metadata_stability(self):
        before = (self.root / 'catalog.csv').read_bytes()
        with patch.object(restore.urllib.request, 'urlopen', return_value=io.BytesIO(self.pdf)):
            self.assertEqual(restore.restore(self.root, 'openai', ['example'], download=True), [('openai:example','restored')])
        self.assertEqual(self.path.read_bytes(), self.pdf)
        self.assertEqual((self.root / 'catalog.csv').read_bytes(), before)
        with patch.object(restore.urllib.request, 'urlopen') as request:
            self.assertEqual(restore.restore(self.root), [('openai:example','present')])
            request.assert_not_called()

    def test_changed_remote_bytes_are_not_published_as_originals(self):
        with patch.object(restore.urllib.request, 'urlopen', return_value=io.BytesIO(b'%PDF-other-bytes')):
            with self.assertRaisesRegex(ValueError, 'Cannot restore'):
                restore.restore(self.root, download=True)
        self.assertFalse(self.path.exists())

    def test_existing_mismatched_source_and_path_escape_are_rejected(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b'changed locally')
        with self.assertRaisesRegex(ValueError, 'not overwritten'):
            restore.restore(self.root, download=True)
        self.assertEqual(self.path.read_bytes(), b'changed locally')
        escaped = '../outside.pdf'
        self.row['local_path'] = self.report['source_pdf'] = escaped
        with (self.root / 'catalog.csv').open('w', newline='') as file:
            writer=csv.DictWriter(file,fieldnames=list(self.row));writer.writeheader();writer.writerow(self.row)
        self.save('abstracts/index.json', dict(reports=[self.report]))
        with self.assertRaisesRegex(ValueError, 'inside the local pdfs'):
            restore.restore(self.root)


class ScopedCollectionTests(unittest.TestCase):
    def test_only_selected_report_is_fetched_and_history_is_retained(self):
        collector = module('af_collect', ROOT / '.agents/skills/af-collect-reports/scripts/collect_reports.py')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sources = [dict(vendor='openai', slug='example', title='Example', pdf_url='https://example.org/new'),
                       dict(vendor='openai', slug='unrelated', title='Unrelated', pdf_url='https://example.org/unrelated')]
            (root / 'sources.json').write_text(json.dumps(sources))
            old = {key:'' for key in collector.archive.FIELDS}
            old.update(vendor='openai', title='Example', published_date='2026-01-01', version='arxiv-v1',
                       local_path='pdfs/openai/technical-reports/example--arxiv-v1.pdf', pdf_url='https://example.org/old', status='archived')
            new = {**old, 'version':'arxiv-v2', 'local_path':'pdfs/openai/technical-reports/example--arxiv-v2.pdf', 'pdf_url':sources[0]['pdf_url']}
            with patch.object(collector.archive, 'ROOT', root), patch.object(collector.archive, 'render'), patch.object(collector.archive, 'fetch_one', return_value=new) as fetch:
                collector.archive.write_catalog([old])
                collector.collect('openai', ['example'])
                self.assertEqual(fetch.call_count, 1)
                self.assertEqual(fetch.call_args.args[0]['slug'], 'example')
                self.assertEqual({r['version'] for r in collector.archive.read_catalog()}, {'arxiv-v1','arxiv-v2'})
                fetch.reset_mock()
                with self.assertRaisesRegex(ValueError, 'Unknown'):
                    collector.collect('openai', ['missing'])
                fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
