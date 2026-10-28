import re
import unittest

from typestorm import theme


class ColourTests(unittest.TestCase):
    def test_mix_endpoints(self):
        self.assertEqual(theme.mix("#000000", "#ffffff", 0), "#000000")
        self.assertEqual(theme.mix("#000000", "#ffffff", 1), "#ffffff")

    def test_mix_midpoint(self):
        self.assertEqual(theme.mix("#000000", "#ffffff", 0.5), "#808080")

    def test_mix_is_clamped(self):
        self.assertEqual(theme.mix("#102030", "#ffffff", 5), "#ffffff")
        self.assertEqual(theme.mix("#102030", "#ffffff", -5), "#102030")

    def test_palette_values_are_valid_hex(self):
        for name in ("BG_TOP", "BG_BOTTOM", "PANEL", "ACCENT", "GOOD", "WARN", "BAD", "TEXT"):
            self.assertRegex(getattr(theme, name), re.compile(r"^#[0-9a-f]{6}$"))


if __name__ == "__main__":
    unittest.main()
