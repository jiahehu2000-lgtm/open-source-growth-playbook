"""Validate evidence consistency, local links, Skill metadata and SVG syntax."""
from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as ET

import yaml

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def dated(value: str) -> None:
    require(datetime.fromisoformat(value.replace('Z', '+00:00')).utcoffset() is not None,
            'Evidence timestamp must contain a timezone.')


def main() -> None:
    data = {p.stem: json.loads(p.read_text(encoding='utf-8-sig'))
            for p in (ROOT / 'data').glob('*.json')}
    selected = data['directions']['directions']
    require([item['id'] for item in selected] == list(range(1, 11)), 'Need ten numbered directions.')
    repos = {item['repository']: item for item in data['repository_evidence']['repositories']}
    captured = {}
    for snap in data['trending_snapshot']['snapshots']:
        require(snap['captured_article_count'] == len(snap['repositories']), 'Trending row count mismatch.')
        dated(snap['fetched_at_utc'])
        for item in snap['repositories']:
            for field in ('cumulative_stars', 'period_stars'):
                require(type(item[field]) is int and item[field] >= 0, 'Invalid Trending count.')
            captured[item['repository'], snap['period']] = item
    for item in repos.values():
        require(item['status'] == 'verified', 'Failed repository evidence must be reviewed.')
        require(item['source_url'] == 'https://api.github.com/repos/' + item['repository'], 'Repo source mismatch.')
        dated(item['fetched_at_utc'])
    for item in selected:
        require(item['repository'] in repos, 'Direction lacks official API evidence.')
        require((item['repository'], item['period']) in captured, 'Direction lacks matching Trending period.')
    posts = data['post_evidence']['posts']
    require(len({p['id'] for p in posts}) == len(posts), 'Duplicate post IDs.')
    for post in posts:
        require(post['item_api_url'] == f"https://hacker-news.firebaseio.com/v0/item/{post['id']}.json",
                'HN source mismatch.')
        require(type(post['points']) is int and post['points'] >= 100, 'Post outside declared sample.')
        require(type(post['comments']) is int and post['comments'] >= 0, 'Invalid comment count.')
        dated(post['published_at_utc'])
        dated(post['fetched_at_utc'])

    skill = ROOT / 'skills' / 'github-project-outreach'
    text = (skill / 'SKILL.md').read_text(encoding='utf-8')
    require(text.startswith('---\n'), 'Missing Skill frontmatter.')
    front = yaml.safe_load(text.split('---', 2)[1])
    require(front['name'] == skill.name, 'Skill folder/name mismatch.')
    require(0 < len(front['description']) <= 1024, 'Invalid Skill description length.')
    interface = yaml.safe_load((skill / 'agents' / 'openai.yaml').read_text(encoding='utf-8'))['interface']
    require(25 <= len(interface['short_description']) <= 64, 'Invalid interface description length.')
    require('$github-project-outreach' in interface['default_prompt'], 'Missing Skill invocation in prompt.')

    sources = [ROOT / 'README.md', *(ROOT / 'docs').glob('*.md'), *skill.rglob('*.md')]
    checked = 0
    for source in sources:
        for target in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)\)', source.read_text(encoding='utf-8')):
            if target.startswith(('https://', 'http://', '#', 'mailto:')):
                continue
            local = unquote(target.split('#', 1)[0])
            require((source.parent / local).exists(), f'Broken link: {source.relative_to(ROOT)} -> {target}')
            checked += 1
    ET.parse(ROOT / 'assets' / 'outreach-map.svg')
    require('2026-10-09' in (ROOT / 'README.md').read_text(encoding='utf-8'), 'Missing dated edition.')
    print(f'PASS: 10 directions, {len(repos)} repository sources, {len(posts)} posts, '
          f'{checked} local links, Skill metadata, SVG.')


if __name__ == '__main__':
    main()
