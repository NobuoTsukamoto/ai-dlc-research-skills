import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / '.github/scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


collector = load('collect_updates')
runner = load('run_copilot')
REGISTRY = '## Cursor\n### primary\n- RSS: https://cursor.com/changelog/rss.xml\n'


def feed(body='First', published='Wed, 28 Oct 2026 16:00:00 GMT', extra=''):
    return f'<rss><channel><item><title>Update</title><link>https://cursor.com/changelog/test</link><pubDate>{published}</pubDate><description>{body}</description></item>{extra}</channel></rss>'


class CollectionTests(unittest.TestCase):
    def collect(self, body, old=None):
        return collector.collect(REGISTRY, old or {}, '2026-10-29', lambda _: body)

    def test_jst_dates_and_duplicate_suppression(self):
        result, state = self.collect(feed())
        self.assertEqual(len(result['candidates']), 1)
        self.assertEqual(result['candidates'][0]['published'], '2026-10-29')
        result, _ = self.collect(feed(), state)
        self.assertEqual(result['candidates'], [])

    def test_revision_and_late_entry_survive_date_filter(self):
        _, state = self.collect(feed())
        result, _ = self.collect(feed('Corrected'), state)
        self.assertEqual(result['candidates'][0]['reason'], 'revision')
        late = '<item><title>Late</title><link>https://cursor.com/late</link><pubDate>Mon, 26 Oct 2026 00:00:00 GMT</pubDate><description>Late</description></item>'
        result, _ = self.collect(feed(extra=late), state)
        self.assertEqual(result['candidates'][0]['title'], 'Late')

    def test_future_entry_not_acknowledged(self):
        result, state = self.collect(feed(published='Fri, 30 Oct 2026 00:00:00 GMT'))
        self.assertEqual(result['candidates'], [])
        self.assertFalse(any(state.values()))

    def test_logged_url_is_filtered_but_revision_is_not(self):
        known = {('cursor', 'https://cursor.com/changelog/test')}
        result, state = collector.collect(REGISTRY, {}, '2026-10-29',
                                          lambda _: feed(), known)
        self.assertEqual(result['candidates'], [])
        result, _ = collector.collect(REGISTRY, state, '2026-10-29',
                                      lambda _: feed('Revised'), known)
        self.assertEqual(result['candidates'][0]['reason'], 'revision')

    def test_failure_keeps_previous_state(self):
        _, state = self.collect(feed())
        result, new = self.collect('invalid xml', state)
        self.assertEqual(result['coverage'][0]['status'], 'failed')
        self.assertEqual(new, state)

    def test_registry_covers_every_primary(self):
        registry = (ROOT / '.agents/skills/ai-coding-agent-updates/references/official-sources.md').read_text('utf-8')
        sources = list(collector.sources(registry))
        self.assertEqual(len(sources), 18)
        self.assertEqual(len({tool for tool, _ in sources}), 7)

    def test_runner_preserves_failure_and_usage_output(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            code = runner.run([sys.executable, '-c', 'print("usage evidence"); raise SystemExit(7)'], 'weekly', path)
            self.assertEqual(code, 7)
            data = json.loads((path / 'run.json').read_text('utf-8'))
            self.assertEqual(data['status'], 'failed')
            self.assertEqual(data['exit_code'], 7)
            self.assertIn('usage evidence', (path / 'copilot-output.txt').read_text('utf-8'))

    def test_telemetry_totals_deduplicate_spans_and_keep_unknown_null(self):
        import json
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'otel.jsonl'
            span = {'spanContext': {'spanId': 'one'}, 'attributes': {
                'gen_ai.response.model': 'gpt-6-luna',
                'gen_ai.usage.input_tokens': 25,
                'gen_ai.usage.output_tokens': 10}}
            path.write_text(json.dumps(span) + '\n' + json.dumps(span) + '\n{', 'utf-8')
            result = runner.telemetry_usage(path)
            self.assertEqual(result['input_tokens'], 25)
            self.assertEqual(result['output_tokens'], 10)
            self.assertEqual(result['actual_model'], 'gpt-6-luna')
            self.assertIsNone(result['cache_tokens'])


if __name__ == '__main__':
    unittest.main()
