"""Small data classes for things that move around on screen."""

from dataclasses import dataclass


@dataclass
class Meteor:
    text: str
    x: float
    y: float
    speed: float
    color: str
    kind: str = "normal"   # normal | boss | freeze | bomb | life
    base_x: float = 0.0
    sway: float = 0.0
    phase: float = 0.0


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    color: str


@dataclass
class FloatText:
    text: str
    x: float
    y: float
    life: int
    color: str
