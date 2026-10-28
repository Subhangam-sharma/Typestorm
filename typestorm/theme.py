"""Window size, colour palette and small colour helpers."""

W, H = 800, 600
GROUND = 545                 # y position of the firewall line

BG_TOP = "#070b1f"
BG_BOTTOM = "#101b42"
PANEL = "#111a3b"
PANEL_DARK = "#0b1230"
PANEL_EDGE = "#2b3c80"
CHIP = "#15204a"

TEXT = "#eef1ff"
MUTED = "#8190c4"
ACCENT = "#4cc9f0"
GOOD = "#2ee6a6"
WARN = "#ffd166"
BAD = "#ff5d73"
PINK = "#ff8fd8"
VIOLET = "#a29bfe"

METEOR_COLORS = [ACCENT, GOOD, WARN, PINK, VIOLET, "#ff9f68"]

UI_FONT = "Segoe UI"
MONO_FONT = "Consolas"


def _rgb(colour: str):
    colour = colour.lstrip("#")
    return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    """Blend colour a into colour b. t=0 gives a, t=1 gives b."""
    t = max(0.0, min(1.0, t))
    ra, ga, ba = _rgb(a)
    rb, gb, bb = _rgb(b)
    return "#{:02x}{:02x}{:02x}".format(
        round(ra + (rb - ra) * t), round(ga + (gb - ga) * t), round(ba + (bb - ba) * t))
