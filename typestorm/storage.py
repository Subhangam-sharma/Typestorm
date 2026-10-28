"""Saving and loading of best scores and lifetime statistics."""

import json
from pathlib import Path

from .rules import DIFFICULTY

DEFAULT_PATH = Path.home() / ".typestorm_stats.json"


def default_stats() -> dict:
    return {"best": {name: 0 for name in DIFFICULTY}, "games": 0, "words": 0}


def load(path: Path = DEFAULT_PATH) -> dict:
    """Read stats from disk; fall back to defaults if the file is missing
    or damaged."""
    stats = default_stats()
    try:
        data = json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return stats
    if not isinstance(data, dict):
        return stats
    best = data.get("best")
    if isinstance(best, dict):
        for name in DIFFICULTY:
            if isinstance(best.get(name), int):
                stats["best"][name] = best[name]
    for key in ("games", "words"):
        if isinstance(data.get(key), int):
            stats[key] = data[key]
    return stats


def save(stats: dict, path: Path = DEFAULT_PATH) -> None:
    try:
        Path(path).write_text(json.dumps(stats, indent=2))
    except OSError:
        pass  # a read-only disk should never crash the game


def record_game(stats: dict, difficulty: str, score: int, words: int) -> bool:
    """Add a finished game to the stats. Returns True for a new best score."""
    stats["games"] += 1
    stats["words"] += words
    is_best = score > stats["best"].get(difficulty, 0)
    if is_best:
        stats["best"][difficulty] = score
    return is_best
