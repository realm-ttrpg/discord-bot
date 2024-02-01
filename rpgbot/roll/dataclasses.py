"""Data classes for dice roller"""

# stdlib
from dataclasses import dataclass


@dataclass
class RollSegment:
    raw: str
    negative: bool = False


@dataclass
class ConstantModifier(RollSegment):
    number: int = 0


@dataclass
class DiceRoll(RollSegment):
    dice: int = 0
    faces: int = 0
    extra: str | None = None


@dataclass
class SegmentResult:
    segment: RollSegment
    rolls: list[int] | None = None
    work: str | None = None
    total: int = 0


class BatchRoll(list[DiceRoll]):
    pass
