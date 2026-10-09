"""Read public GitHub metadata and compare dated snapshots; no credentials needed."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_new(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def capture(repository: str) -> dict:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Expected owner/repository, without URL or extra path segments.')
    url = 'https://api.github.com/repos/' + repository
    request = Request(url, headers={'Accept': 'application/vnd.github+json',
                                   'User-Agent': 'github-project-outreach-snapshot'})
    started_at = utc_now()
    try:
        with urlopen(request, timeout=20) as response:
            repo = json.load(response)
        for field in ('id', 'full_name', 'html_url', 'stargazers_count', 'forks_count'):
            if field not in repo:
                raise ValueError('GitHub response missing required field: ' + field)
        for field in ('stargazers_count', 'forks_count'):
            if not isinstance(repo[field], int) or isinstance(repo[field], bool) or repo[field] < 0:
                raise ValueError('Invalid nonnegative GitHub count: ' + field)
        return {'schema_version': 1, 'status': 'ok', 'fetched_at_utc': utc_now(),
                'source_url': url, 'repository_id': repo['id'],
                'repository': repo['full_name'], 'html_url': repo['html_url'],
                'stars': repo['stargazers_count'], 'forks': repo['forks_count'],
                'description': repo.get('description'), 'topics': repo.get('topics', []),
                'created_at': repo.get('created_at'), 'pushed_at': repo.get('pushed_at')}
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        result = {'schema_version': 1, 'status': 'error', 'fetched_at_utc': started_at,
                  'source_url': url, 'repository': repository, 'stars': None,
                  'forks': None, 'error_type': type(exc).__name__}
        if isinstance(exc, HTTPError):
            result['http_status'] = exc.code
            result['retry_after'] = exc.headers.get('Retry-After')
        return result


def parse_time(value: str) -> datetime:
    date = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if date.utcoffset() is None:
        raise ValueError('Snapshot time must include its timezone.')
    return date.astimezone(timezone.utc)


def compare(before: dict, after: dict) -> dict:
    if before.get('status') != 'ok' or after.get('status') != 'ok':
        raise ValueError('Cannot compare a failed or unverified snapshot.')
    if before.get('repository_id') is None or before['repository_id'] != after.get('repository_id'):
        raise ValueError('Snapshots refer to different or unidentified repositories.')
    start = parse_time(before['fetched_at_utc'])
    end = parse_time(after['fetched_at_utc'])
    if end <= start:
        raise ValueError('The later snapshot must have a later timestamp.')
    for item in (before, after):
        for field in ('stars', 'forks'):
            if not isinstance(item.get(field), int) or isinstance(item[field], bool) or item[field] < 0:
                raise ValueError('Invalid snapshot count: ' + field)
    return {'schema_version': 1, 'repository_id': before['repository_id'],
            'before_repository': before['repository'], 'after_repository': after['repository'],
            'start_utc': start.isoformat(), 'end_utc': end.isoformat(),
            'elapsed_hours': (end - start).total_seconds() / 3600,
            'stars_before': before['stars'], 'stars_after': after['stars'],
            'net_stars': after['stars'] - before['stars'],
            'net_forks': after['forks'] - before['forks'],
            'interpretation': 'Observed net change; no attribution or growth guarantee.'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    fetch = sub.add_parser('capture', help='Capture one public repository baseline.')
    fetch.add_argument('repository')
    fetch.add_argument('--output', type=Path, required=True)
    diff = sub.add_parser('compare', help='Compare successful snapshots from the same repository.')
    diff.add_argument('before', type=Path)
    diff.add_argument('after', type=Path)
    diff.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists; use a new filename.')
    try:
        if args.command == 'capture':
            result = capture(args.repository)
        else:
            before = json.loads(args.before.read_text(encoding='utf-8-sig'))
            after = json.loads(args.after.read_text(encoding='utf-8-sig'))
            result = compare(before, after)
        write_new(args.output, result)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps({'status': result.get('status', 'ok'), 'output': str(args.output)},
                     ensure_ascii=False))
    return 1 if result.get('status') == 'error' else 0


if __name__ == '__main__':
    raise SystemExit(main())
