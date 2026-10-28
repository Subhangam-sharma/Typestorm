import tempfile
import unittest
from pathlib import Path

from typestorm import storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "stats.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_missing_file_gives_defaults(self):
        self.assertEqual(storage.load(self.path), storage.default_stats())

    def test_round_trip(self):
        stats = storage.default_stats()
        storage.record_game(stats, "Hard", 420, 15)
        storage.save(stats, self.path)
        self.assertEqual(storage.load(self.path), stats)

    def test_corrupt_file_is_ignored(self):
        self.path.write_text("{ not json")
        self.assertEqual(storage.load(self.path), storage.default_stats())

    def test_wrong_shape_is_ignored(self):
        self.path.write_text("[1, 2, 3]")
        self.assertEqual(storage.load(self.path), storage.default_stats())

    def test_record_game_tracks_best_per_difficulty(self):
        stats = storage.default_stats()
        self.assertTrue(storage.record_game(stats, "Normal", 100, 5))
        self.assertFalse(storage.record_game(stats, "Normal", 80, 4))
        self.assertTrue(storage.record_game(stats, "Easy", 10, 1))
        self.assertEqual(stats["best"]["Normal"], 100)
        self.assertEqual(stats["games"], 3)
        self.assertEqual(stats["words"], 10)


if __name__ == "__main__":
    unittest.main()
