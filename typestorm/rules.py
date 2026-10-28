"""Pure game rules: speed curve, spawn rate, scoring and statistics.

Nothing in this module touches the GUI, which keeps it easy to unit test and
to tune the difficulty in one place.
"""

FPS = 60

START_LIVES = 5
MAX_LIVES = 7
WORDS_PER_LEVEL = 7

BASE_SPEED = 0.6        # pixels per frame on level 1
SPEED_GROWTH = 1.2      # every level is 20% faster than the one before
MAX_SPEED = 6.5         # hard cap so late levels stay (barely) playable

BASE_SPAWN_FRAMES = 100  # frames between meteors on level 1
SPAWN_DECAY = 0.88       # spawn gap shrinks by 12% per level
MIN_SPAWN_FRAMES = 20

DIFFICULTY = {"Easy": 0.8, "Normal": 1.0, "Hard": 1.25}


def level_for(words_destroyed: int) -> int:
    """Level reached after destroying the given number of words."""
    return 1 + words_destroyed // WORDS_PER_LEVEL


def fall_speed(level: int, factor: float = 1.0) -> float:
    """Pixels per frame a meteor falls at the given level."""
    base = min(MAX_SPEED, BASE_SPEED * SPEED_GROWTH ** (level - 1))
    return base * factor


def spawn_interval(level: int, factor: float = 1.0) -> int:
    """Frames between two meteors at the given level."""
    frames = BASE_SPAWN_FRAMES * SPAWN_DECAY ** (level - 1) / factor
    return max(MIN_SPAWN_FRAMES, int(frames))


def combo_multiplier(combo: int) -> float:
    """+0.5x for every five words destroyed in a row."""
    return 1 + (combo // 5) * 0.5


def score_for_word(length: int, combo: int, boss: bool = False) -> int:
    points = int(length * 10 * combo_multiplier(combo))
    return points * 3 if boss else points


def accuracy(correct_keys: int, total_keys: int) -> float:
    """Percentage of key presses that hit the current word."""
    if total_keys <= 0:
        return 100.0
    return 100.0 * correct_keys / total_keys


def wpm(correct_chars: int, frames_played: int) -> float:
    """Typing speed in words per minute (one word = five characters)."""
    minutes = frames_played / (FPS * 60)
    if minutes <= 0:
        return 0.0
    return (correct_chars / 5) / minutes
