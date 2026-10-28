"""Word lists. Longer words only appear as the level increases."""

import random

_RAW = """
art bit bug cpu css dns git gui ram sql tab web zip
app bash byte cache chip code data disk edit file font grid hash host icon
java link list loop mail menu node path port root sort tree user wifi
array audio batch bytes cloud debug email event fetch frame input logic
macro merge mouse parse patch pixel proxy query queue regex route scope
shell stack style token trace tuple video
binary branch buffer bundle cursor deploy domain driver engine format
header kernel layout module object packet python script server socket
syntax thread vector window
backend browser compile console desktop execute gateway library network
package pointer program runtime session storage variable
boolean compiler database frontend function hardware keyboard platform
protocol resilient software terminal ephemeral pragmatic versatile
algorithm developer interface processor recursion framework generation
diligent eloquent tenacious meticulous ambiguous benevolent
""".split()

WORDS = sorted(set(_RAW))

BOSS_WORDS = [
    "authentication",
    "synchronization",
    "internationalize",
    "multiprocessing",
    "cybersecurity",
    "objectoriented",
    "virtualization",
    "microprocessor",
    "troubleshooting",
]

MAX_WORD_LENGTH = 12


def max_length(level: int) -> int:
    """Longest word allowed on a level (level 1 = 4 letters)."""
    return min(MAX_WORD_LENGTH, 3 + level)


def pick_word(level: int, avoid_initials=()) -> str:
    """Random word for the level, favouring longer ones, avoiding repeated
    first letters so that typing the first key always selects one meteor."""
    limit = max_length(level)
    pool = [w for w in WORDS if len(w) <= limit]
    fresh = [w for w in pool if w[0] not in avoid_initials]
    pool = fresh or pool
    weights = [len(w) ** 1.5 for w in pool]
    return random.choices(pool, weights=weights, k=1)[0]
