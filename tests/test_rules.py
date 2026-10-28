import unittest

from typestorm import rules


class SpeedCurveTests(unittest.TestCase):
    def test_every_level_is_faster(self):
        speeds = [rules.fall_speed(level) for level in range(1, 12)]
        self.assertEqual(speeds, sorted(speeds))
        self.assertLess(speeds[0], speeds[1])

    def test_each_level_is_at_least_twenty_percent_faster(self):
        self.assertAlmostEqual(rules.fall_speed(2) / rules.fall_speed(1), rules.SPEED_GROWTH)

    def test_speed_is_capped(self):
        self.assertEqual(rules.fall_speed(100), rules.MAX_SPEED)

    def test_difficulty_factor_scales_speed(self):
        self.assertGreater(rules.fall_speed(3, 1.25), rules.fall_speed(3, 1.0))
        self.assertLess(rules.fall_speed(3, 0.8), rules.fall_speed(3, 1.0))


class SpawnTests(unittest.TestCase):
    def test_spawn_gap_shrinks_but_has_a_floor(self):
        gaps = [rules.spawn_interval(level) for level in range(1, 30)]
        self.assertEqual(gaps, sorted(gaps, reverse=True))
        self.assertEqual(gaps[-1], rules.MIN_SPAWN_FRAMES)


class LevelTests(unittest.TestCase):
    def test_level_thresholds(self):
        self.assertEqual(rules.level_for(0), 1)
        self.assertEqual(rules.level_for(rules.WORDS_PER_LEVEL - 1), 1)
        self.assertEqual(rules.level_for(rules.WORDS_PER_LEVEL), 2)


class ScoreTests(unittest.TestCase):
    def test_basic_score(self):
        self.assertEqual(rules.score_for_word(5, 0), 50)

    def test_combo_multiplier(self):
        self.assertEqual(rules.combo_multiplier(4), 1.0)
        self.assertEqual(rules.combo_multiplier(5), 1.5)
        self.assertEqual(rules.combo_multiplier(10), 2.0)
        self.assertEqual(rules.score_for_word(4, 5), 60)

    def test_boss_pays_triple(self):
        self.assertEqual(rules.score_for_word(10, 0, boss=True), 300)


class StatTests(unittest.TestCase):
    def test_accuracy(self):
        self.assertEqual(rules.accuracy(0, 0), 100.0)
        self.assertEqual(rules.accuracy(9, 10), 90.0)

    def test_wpm(self):
        self.assertEqual(rules.wpm(100, 0), 0.0)
        # 300 characters in one minute is 60 words per minute
        self.assertAlmostEqual(rules.wpm(300, rules.FPS * 60), 60.0)


if __name__ == "__main__":
    unittest.main()
