"""Protect native web quotations, asset identity, and PDF-free reader builds."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from web_sources import digest, export_figures, load_sources, summary, validate_summary, validate_figures, verify_snapshot
from build_readers import build_readers


class WebSourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'abstracts').mkdir()
        (self.root / '.cache').mkdir()
        self.snapshot = self.root / '.cache/article.html'
        self.snapshot.write_text('<p>Original <a href="https://example.org">model</a> overview.</p>'
                                 '<p>Second paragraph.<span class="sr-only">Hidden helper</span></p>'
                                 '<script>Invented text</script><img src="https://example.org/asset.png">'
                                 '<figcaption>Original caption.</figcaption>')
        self.asset = self.root / '.cache/asset.png'
        Image.new('RGBA', (20, 10), (255, 255, 255, 0)).save(self.asset)
        self.source = dict(id='openai:web-example', vendor='openai', title='Example', models=['Example'],
            source_url='https://example.org/article', retrieved_at='2026-10-14', source_heading=None,
            snapshot=dict(path='.cache/article.html', bytes=self.snapshot.stat().st_size,
                          sha256=digest(self.snapshot.read_bytes())),
            paragraphs=[dict(text='Original model overview.', locator='First p'),
                        dict(text='Second paragraph.', locator='Second p')],
            review=dict(reviewed_at='2026-10-14', paragraph_boundaries_verified=True),
            assets=[dict(local_path='.cache/asset.png', asset_url='https://example.org/asset.png',
                         asset_sha256=digest(self.asset.read_bytes()), dimensions=[20, 10],
                         role='results', caption='Original caption.', alt='Native alt', visual_review=True)])
        self.save()

    def save(self):
        (self.root / 'abstracts/web-sources.json').write_text(json.dumps(dict(sources=[self.source])))

    def test_visible_text_excludes_scripts_and_accessibility_helpers(self):
        verify_snapshot(self.root, self.source)
        for text in ('Invented text', 'Hidden helper'):
            self.source['paragraphs'] = [dict(text=text)]
            with self.assertRaisesRegex(ValueError, 'visible HTML'):
                verify_snapshot(self.root, self.source)

    def test_changed_html_and_invented_caption_are_rejected(self):
        self.snapshot.write_text('changed')
        with self.assertRaisesRegex(ValueError, 'Changed HTML'):
            verify_snapshot(self.root, self.source)
        self.source['snapshot'].update(bytes=7, sha256=digest(b'changed'))
        self.source['paragraphs'] = [dict(text='changed')]
        with self.assertRaisesRegex(ValueError, 'Caption/lead-in'):
            verify_snapshot(self.root, self.source)

    def test_stale_web_passage_and_snapshot_binding_are_rejected(self):
        report = summary(self.source)
        validate_summary(self.root, report)
        report['text'] = 'Another model.'
        with self.assertRaisesRegex(ValueError, 'Stale web summary'):
            validate_summary(self.root, report)

    def test_relative_native_image_url_resolves_against_official_page(self):
        self.snapshot.write_text(self.snapshot.read_text().replace('https://example.org/asset.png', '/asset.png'))
        self.source['snapshot'].update(bytes=self.snapshot.stat().st_size, sha256=digest(self.snapshot.read_bytes()))
        verify_snapshot(self.root, self.source)
        self.source['assets'][0]['asset_url'] = 'https://example.org/another-version.png'
        with self.assertRaisesRegex(ValueError, 'Asset URL'):
            verify_snapshot(self.root, self.source)

    def test_empty_native_html_attributes_do_not_hide_visible_prose(self):
        self.snapshot.write_text(self.snapshot.read_text().replace('<p>', '<p class>') + '<img srcset>')
        self.source['snapshot'].update(bytes=self.snapshot.stat().st_size, sha256=digest(self.snapshot.read_bytes()))
        verify_snapshot(self.root, self.source)

    def test_unreviewed_asset_and_path_escape_are_rejected(self):
        self.source['assets'][0]['visual_review'] = False
        self.save()
        with self.assertRaisesRegex(ValueError, 'unreviewed'):
            load_sources(self.root)
        self.source['assets'][0]['visual_review'] = True
        self.source['snapshot']['path'] = '../outside.html'
        with self.assertRaisesRegex(ValueError, 'escapes project'):
            verify_snapshot(self.root, self.source)

    def export(self):
        report = summary(self.source)
        selected = dict(source_sha256=report['source_sha256'], figures=self.source['assets'])
        return export_figures(self.root, self.root/'figures', report, selected)[1]

    def test_original_png_bytes_are_preserved_without_a_synthetic_pdf(self):
        figure = self.export()['figures'][0]
        self.assertEqual((self.root / figure['png_path']).read_bytes(), self.asset.read_bytes())
        self.assertEqual(figure['transform'], 'original_bytes')
        self.assertIsNone(figure['page'])
        self.assertNotIn('pdf_path', figure)
        self.asset.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'Changed/unreviewed'):
            self.export()

    def test_alpha_composition_changes_only_display_background(self):
        self.source['assets'][0]['display_background'] = '#111111'
        self.save()
        figure = self.export()['figures'][0]
        with Image.open(self.root / figure['png_path']) as image:
            self.assertEqual(image.getpixel((0, 0)), (17, 17, 17))
        self.assertEqual(figure['asset_sha256'], digest(self.asset.read_bytes()))
        self.assertEqual(figure['transform'], 'alpha_composite:#111111')

    def test_reader_build_needs_no_html_capture_or_pdf(self):
        self.source['assets'] = []
        self.save()
        report = summary(self.source)
        report['markdown_path'] = 'abstracts/openai/web-example.md'
        markdown = self.root / report['markdown_path']
        markdown.parent.mkdir()
        markdown.write_text('# Example\n\n' + report['text'])
        (self.root / 'site').mkdir()
        (self.root / 'site/reader.html').write_text((ROOT/'site/reader.html').read_text())
        self.snapshot.unlink()
        self.asset.unlink()
        output = self.root / 'output'
        self.assertEqual(build_readers(self.root, output, {report['id']: report}, {}, []), (2, 0))
        self.assertIn('Original model overview.', (output/'abstracts/openai/web-example.html').read_text())
        self.assertFalse(list(output.rglob('*.pdf')))

    def test_missing_assets_and_invented_captions_fail_without_captures(self):
        report = summary(self.source)
        exported = self.export()
        self.snapshot.unlink()
        self.asset.unlink()
        validate_figures(self.root, report, exported)
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            validate_figures(self.root, report, None)
        exported['figures'][0]['caption'] = 'Invented results.'
        with self.assertRaisesRegex(ValueError, 'Stale native'):
            validate_figures(self.root, report, exported)


if __name__ == '__main__':
    unittest.main()
