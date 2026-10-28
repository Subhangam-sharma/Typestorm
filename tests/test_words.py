import unittest

from typestorm import words


class WordTests(unittest.TestCase):
    def test_word_list_is_clean(self):
        for word in words.WORDS + words.BOSS_WORDS:
            self.assertTrue(word.isalpha() and word.islower(), word)
        self.assertEqual(len(words.WORDS), len(set(words.WORDS)))

    def test_length_limit_grows_with_level(self):
        self.assertEqual(words.max_length(1), 4)
        self.assertEqual(words.max_length(50), words.MAX_WORD_LENGTH)

    def test_pick_word_respects_level(self):
        for _ in range(200):
            self.assertLessEqual(len(words.pick_word(1)), words.max_length(1))

    def test_pick_word_avoids_used_initials(self):
        used = set("abcdefghijklmnop")
        for _ in range(200):
            self.assertNotIn(words.pick_word(8, used)[0], used)

    def test_pick_word_still_works_when_every_initial_is_used(self):
        every_letter = set("abcdefghijklmnopqrstuvwxyz")
        self.assertIn(words.pick_word(5, every_letter), words.WORDS)

    def test_boss_words_are_long(self):
        self.assertTrue(all(len(w) > words.MAX_WORD_LENGTH for w in words.BOSS_WORDS))


if __name__ == "__main__":
    unittest.main()
