"""Keep the independent model directory complete and preserve reader targets."""
import html
import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_pages import current_model_keys, hero_heading, model_card, write_sitemap


class ModelDirectoryTests(unittest.TestCase):
    def test_current_models_resolve_aggregate_and_report_update_aliases(self):
        models = [dict(vendor='openai', model='A / B'), dict(vendor='openai', model='A safety update')]
        history = {'coverage_aliases': [dict(vendor='openai', coverage_model='A / B', models=['A', 'B']),
                                        dict(vendor='openai', coverage_model='A safety update', models=['A'])]}
        self.assertEqual(current_model_keys(models, history), {('openai', 'a'), ('openai', 'b')})

    def test_rows_keep_historical_unknown_dates_and_original_readers(self):
        model = dict(vendor='openai', model='Historical <model>', release_date='', categories=['general'],
                     search_aliases=['Historical alias'])
        row = model_card(model, 'abstracts/openai/example.html', {'openai': 'OpenAI'}, set(), False, '')
        self.assertIn('data-frontier="0"', row)
        self.assertIn('data-date=""', row)
        self.assertIn('Date unconfirmed', row)
        self.assertIn('href="abstracts/openai/example.html"', row)
        self.assertIn('Historical &lt;model&gt;', row)
        self.assertIn('Historical alias', row)
        self.assertNotIn('target="_blank"', row)

    def test_official_sources_and_bilingual_unknown_labels(self):
        model = dict(vendor='openai', model='Model', release_date='', categories=[], search_aliases=[])
        row = model_card(model, 'https://openai.com/model', {'openai': 'OpenAI'}, {('openai', 'model')}, True, '../')
        self.assertIn('data-frontier="1"', row)
        self.assertIn('target="_blank" rel="noopener"', row)
        self.assertIn('日期待确认', row)
        self.assertNotIn('datetime=', row)
        model['release_date'] = '2026-10-01'
        self.assertIn('<time datetime="2026-10-01">2026-10-01</time>',
                      model_card(model, 'https://openai.com/model', {'openai': 'OpenAI'}, set(), False, ''))

    def test_headline_preserves_brand_words_and_phrase_boundaries(self):
        for text, chinese in [('The official reports behind frontier AI', False), ('前沿 AI 的官方报告档案', True)]:
            output = hero_heading(text, chinese)
            visible = html.unescape(re.sub('<[^>]+>', '', output))
            self.assertEqual(re.sub(r'\s+', '', visible), re.sub(r'\s+', '', text))
            self.assertEqual(output.count('class="headline-line"'), 2)
            self.assertNotIn('的官</span>', output)

    def test_model_directory_has_both_sitemap_editions(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            write_sitemap(Path(tmp), {})
            sitemap = (Path(tmp) / 'sitemap.xml').read_text()
        self.assertIn('/models.html</loc>', sitemap)
        self.assertIn('/cn/models.html</loc>', sitemap)


if __name__ == '__main__':
    unittest.main()
