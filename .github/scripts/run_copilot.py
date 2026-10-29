#!/usr/bin/env python3
"""Preserve CLI usage output and telemetry for each attempt, including failures."""
import argparse
from datetime import datetime, timezone
import json
import os
import re
from pathlib import Path
import subprocess
import sys


def telemetry_usage(path):
    """Read per-call span attributes; metrics are not added again to span totals."""
    calls = {}

    def visit(value):
        if isinstance(value, list):
            for child in value:
                visit(child)
        elif isinstance(value, dict):
            context = value.get('spanContext', {})
            span_id = value.get('spanId') or context.get('spanId')
            attrs = value.get('attributes', {})
            if isinstance(attrs, list):
                attrs = {a['key']: next(iter(a.get('value', {}).values()), None)
                         for a in attrs if 'key' in a}
            if span_id and isinstance(attrs, dict) and any(k.startswith('gen_ai.usage.') for k in attrs):
                calls[span_id] = attrs
            for child in value.values():
                visit(child)

    if path.exists():
        for line in path.read_text('utf-8').splitlines():
            try:
                visit(json.loads(line))
            except (ValueError, TypeError):
                continue  # Interrupted JSONL may end with an incomplete record.
    result = {'telemetry_call_count': len(calls)}
    models = sorted({a.get('gen_ai.response.model') or a.get('gen_ai.request.model')
                     for a in calls.values()
                     if a.get('gen_ai.response.model') or a.get('gen_ai.request.model')})
    result['actual_models'] = models
    result['actual_model'] = models[0] if len(models) == 1 else None
    for field, attribute in (
        ('input_tokens', 'gen_ai.usage.input_tokens'),
        ('output_tokens', 'gen_ai.usage.output_tokens'),
        ('cache_tokens', 'gen_ai.usage.cache_read.input_tokens'),
    ):
        values = [a.get(attribute) for a in calls.values()]
        # Avoid reporting a partial sum as a complete run total.
        result[field] = sum(int(v) for v in values) if values and all(
            isinstance(v, (int, float)) or (isinstance(v, str) and v.isdigit())
            for v in values) else None
    return result


def run(command, mode, directory=Path('usage')):
    directory.mkdir(parents=True, exist_ok=True)
    metadata = {
        'mode': mode, 'run_id': os.getenv('GITHUB_RUN_ID'),
        'attempt': os.getenv('GITHUB_RUN_ATTEMPT'),
        'requested_model': os.getenv('COPILOT_MODEL'),
        'actual_model': None,
        'started_at': datetime.now(timezone.utc).isoformat(),
        'status': 'running', 'exit_code': None,
        'ai_credits': None, 'input_tokens': None, 'output_tokens': None,
        'cache_tokens': None,
        'note': 'Unavailable values are null. CLI summary and OTel are the usage evidence; do not infer billing from requested model.',
    }
    path = directory / 'run.json'
    path.write_text(json.dumps(metadata, indent=2), 'utf-8')
    env = dict(os.environ, COPILOT_OTEL_FILE_EXPORTER_PATH=str((directory / 'otel.jsonl').resolve()),
               OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT='false', NO_COLOR='1')
    code = 1
    try:
        with (directory / 'copilot-output.txt').open('w', encoding='utf-8') as output:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                       text=True, encoding='utf-8', errors='replace', env=env)
            with process.stdout:
                for line in process.stdout:
                    output.write(line)
                    output.flush()
                    print(line, end='', flush=True)
            code = process.wait()
        metadata['status'] = 'success' if code == 0 else 'failed'
    except Exception as exc:
        metadata.update(status='failed', error=str(exc))
        raise
    finally:
        metadata.update(telemetry_usage(directory / 'otel.jsonl'))
        output_path = directory / 'copilot-output.txt'
        if output_path.exists():
            text = output_path.read_text('utf-8')
            metadata['usage_summary_lines'] = [line for line in text.splitlines()
                if re.search(r'usage|tokens|cached|credits|model', line, re.I)][-80:]
            # Only extract an explicitly labelled CLI total, never estimate price.
            match = re.search(r'^Total usage est:\s*([\d.]+)\s+AI credits\b', text, re.M | re.I)
            if match:
                metadata['ai_credits'] = float(match[1])
        metadata.update(exit_code=code, finished_at=datetime.now(timezone.utc).isoformat())
        path.write_text(json.dumps(metadata, indent=2), 'utf-8')
    return code


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', required=True, choices=['daily', 'weekly', 'monthly', 'dry-run'])
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('A CLI command is required after --')
    sys.exit(run(command, args.mode))
