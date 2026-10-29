#!/usr/bin/env python3
"""Collect every registered primary source; retain changed evidence for review."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / '.agents/skills/ai-coding-agent-updates'
JST = timezone(timedelta(hours=9))
sys.path.insert(0, str(SKILL / 'scripts'))
from update_log import canonicalize_url, load_log


def sources(text):
    tool = None
    primary = False
    ids = dict(zip(('GitHub Copilot', 'GitHub Copilot CLI', 'GitHub Copilot app',
                    'OpenAI Codex', 'Claude Code', 'Cursor', 'Google Antigravity CLI'),
                   ('github-copilot', 'github-copilot-cli', 'github-copilot-app',
                    'openai-codex', 'claude-code', 'cursor', 'antigravity-cli')))
    for line in text.splitlines():
        if line.startswith('## '):
            primary = False
            tool = ids.get(line[3:])
        if line.startswith('### '):
            primary = line == '### primary'
        if tool and primary and (match := re.search(r'https://\S+', line)):
            yield tool, match[0]


def fetch(url):
    # Raw Markdown avoids the GitHub page's navigation and dynamic chrome.
    url = re.sub(r'https://github.com/([^/]+/[^/]+)/blob/',
                 r'https://raw.githubusercontent.com/\1/', url)
    headers = {'User-Agent': 'ai-dlc-update-collector', 'Accept': '*/*'}
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=45) as response:
        data = response.read(8_000_001)
        if len(data) > 8_000_000:
            raise ValueError('Source exceeds 8 MB; manual verification required')
        return data.decode('utf-8')


def plain(value):
    value = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', value, flags=re.S | re.I)
    return re.sub(r'\s+', ' ', html.unescape(re.sub('<[^>]+>', ' ', value))).strip()


def entries(body, url):
    if not (url.endswith('.atom') or url.endswith('.xml') or '/feed/' in url):
        content = plain(body)
        if len(content) < 100 or any(marker in content.casefold() for marker in
                ('just a moment...', 'verify you are human', 'access denied')):
            raise ValueError('Empty page or access challenge; manual verification required')
        return [{'url': url, 'title': 'Changed primary page: verify dates and changes',
                 'published': None, 'body': content}]
    root = ET.fromstring(body)
    result = []
    for item in root.iter():
        if item.tag.split('}')[-1] not in ('entry', 'item'):
            continue
        fields = {}
        link = None
        for child in item:
            key = child.tag.split('}')[-1]
            value = ''.join(child.itertext())
            fields[key] = value
            if key == 'link' and child.attrib.get('rel', 'alternate') == 'alternate':
                link = child.attrib.get('href') or value
        published = fields.get('published') or fields.get('pubDate') or fields.get('updated')
        if not link or not published:
            raise ValueError('Feed entry missing URL or date')
        try:
            dt = datetime.fromisoformat(published.replace('Z', '+00:00'))
        except ValueError:
            dt = parsedate_to_datetime(published)
        if dt.tzinfo is None:
            raise ValueError('Feed date has no timezone')
        result.append({'url': link.strip(), 'title': plain(fields.get('title', '')),
                       'published': dt.astimezone(JST).date().isoformat(),
                       'body': plain(fields.get('content') or fields.get('description') or fields.get('summary', ''))})
    if not result:
        raise ValueError('Empty or unrecognized feed; manual verification required')
    return result


def collect(registry, previous, target, fetcher=fetch, known_urls=frozenset()):
    state = dict(previous)
    candidates, coverage = [], []
    registered = list(sources(registry))

    def safe_fetch(url):
        try:
            return fetcher(url)
        except Exception as exc:
            return exc

    urls = list(dict.fromkeys(url for _, url in registered))
    with ThreadPoolExecutor(max_workers=6) as executor:
        fetched = dict(zip(urls, executor.map(safe_fetch, urls)))
    for tool, url in registered:
        key = tool + ':' + url
        old = previous.get(key, {})
        try:
            if isinstance(fetched[url], Exception):
                raise fetched[url]
            items = entries(fetched[url], url)
            seen = dict(old)
            count = 0
            for item in items:
                digest = hashlib.sha256(json.dumps(item, sort_keys=True).encode()).hexdigest()
                prior = old.get(item['url'])
                changed = prior != digest
                # Warm cache catches late publications and revisions of old entries.
                eligible = bool(old) or item['published'] is None or item['published'] == target
                future = item['published'] and item['published'] > target
                logged = (tool, canonicalize_url(item['url'])) in known_urls
                if changed and eligible and not future and (prior or not logged):
                    candidates.append(dict(item, tool=tool, source=url,
                                           reason='revision' if prior else 'new-or-unseen'))
                    count += 1
                # Do not acknowledge future entries before their target day.
                if not future:
                    seen[item['url']] = digest
            state[key] = seen
            coverage.append(dict(tool=tool, url=url, status='ok', candidates=count,
                                 baseline=not bool(old)))
        except Exception as exc:
            coverage.append(dict(tool=tool, url=url, status='failed', error=str(exc)))
    return {'target_date': target, 'coverage': coverage, 'candidates': candidates}, state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--date', required=True)
    parser.add_argument('--state', type=Path, default=ROOT / 'updates/collection-state.json')
    parser.add_argument('--output', type=Path, default=ROOT / 'collection/candidates.json')
    args = parser.parse_args()
    date.fromisoformat(args.date)
    previous = json.loads(args.state.read_text('utf-8')) if args.state.exists() else {}
    known = {(item['tool'], canonicalize_url(item['url']))
             for item in load_log(ROOT / 'updates/update-log.jsonl')}
    result, state = collect((SKILL / 'references/official-sources.md').read_text('utf-8'),
                            previous, args.date, known_urls=known)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), 'utf-8')
    # Pending state is committed only after a successful report and validation.
    args.output.with_name('pending-state.json').write_text(json.dumps(state, ensure_ascii=False), 'utf-8')
    print(f"Candidates: {len(result['candidates'])}; failed sources: "
          f"{sum(s['status'] == 'failed' for s in result['coverage'])}")


if __name__ == '__main__':
    main()
