"""Behavioral invariants for repository comparisons and failed collection."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/github-project-outreach/scripts/github_snapshot.py'
SPEC = importlib.util.spec_from_file_location('snapshot', SCRIPT)
snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(snapshot)


def sample(at, stars=10, repo_id=7):
    return {'status': 'ok', 'repository_id': repo_id, 'repository': 'demo/project',
            'fetched_at_utc': at, 'stars': stars, 'forks': 2}


class SnapshotTests(unittest.TestCase):
    def test_counts_can_decline(self):
        result = snapshot.compare(sample('2026-10-01T12:00:00Z'),
                                  sample('2026-10-02T12:00:00Z', stars=8))
        self.assertEqual(result['net_stars'], -2)
        self.assertEqual(result['elapsed_hours'], 24)

    def test_different_repositories_are_rejected(self):
        with self.assertRaises(ValueError):
            snapshot.compare(sample('2026-10-01T12:00:00Z'),
                             sample('2026-10-02T12:00:00Z', repo_id=8))

    def test_timezone_equivalence_is_not_a_later_snapshot(self):
        with self.assertRaises(ValueError):
            snapshot.compare(sample('2026-10-01T12:00:00Z'),
                             sample('2026-10-01T20:00:00+08:00'))

    def test_missing_timezone_is_rejected(self):
        with self.assertRaises(ValueError):
            snapshot.compare(sample('2026-10-01T12:00:00'),
                             sample('2026-10-02T12:00:00Z'))

    def test_failed_capture_does_not_invent_zero(self):
        with patch.object(snapshot, 'urlopen', side_effect=URLError('network unavailable')):
            result = snapshot.capture('demo/project')
        self.assertEqual(result['status'], 'error')
        self.assertIsNone(result['stars'])
        with self.assertRaises(ValueError):
            snapshot.compare(result, sample('2026-10-02T12:00:00Z'))

    def test_extra_repository_path_is_rejected(self):
        with self.assertRaises(ValueError):
            snapshot.capture('demo/project/issues')

    def test_existing_artifact_is_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'baseline.json'
            path.write_text('original', encoding='utf-8')
            with self.assertRaises(FileExistsError):
                snapshot.write_new(path, {'other': 1})
            self.assertEqual(path.read_text(encoding='utf-8'), 'original')

    def test_boolean_is_not_a_count(self):
        with self.assertRaises(ValueError):
            snapshot.compare(sample('2026-10-01T12:00:00Z', stars=True),
                             sample('2026-10-02T12:00:00Z'))


if __name__ == '__main__':
    unittest.main()
