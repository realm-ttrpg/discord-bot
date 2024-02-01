"""Parse segments from roll command arguments"""

# stdlib
from re import compile

# local
from .dataclasses import ConstantModifier, DiceRoll, RollSegment

roll_regex = compile(
    r"^(?P<all>"
    r"(?P<num>\d*)"
    r"d(?P<die>\d+)"
    r"(?P<fun>!\d*|k[hl]\d*)?"
    r"(x(?P<batch>\d+))?"
    r")"
)
"""Regex pattern for initial roll"""

addl_roll_regex = compile(
    r"(?P<all>"
    r"(?P<op>[-+])"
    r"(?P<num>\d*)"
    r"(d(?P<die>\d+)(?P<fun>!\d*|k[hl]\d*)?)?"
    r"(x(?P<batch>\d+))?"
    r")"
)
"""Regex pattern for additional modifier rolls/constants"""


def parse_segments(roll: str) -> list[list[RollSegment]]:
    """Parse a roll formula string into a list of RollSegment objects."""

    segments = []

    # strip all whitespace
    roll = roll.replace(" ", "")

    # parse first roll
    match = roll_regex.match(roll)
    assert match

    # parse variable number of mods
    rest = [r.groupdict() for r in addl_roll_regex.finditer(roll)]

    batch = int(match["batch"] or 1)
    match = match.groupdict()

    for r in rest:
        if r["batch"]:
            batch = int(r["batch"])

    batches: list[list[RollSegment]] = []

    for _ in range(batch):
        segments: list[RollSegment] = [
            DiceRoll(
                raw=match["all"],
                dice=int(match["num"] or "1"),
                faces=int(match["die"]),
                extra=match["fun"],
            )
        ]

        for match in rest:
            if match["die"]:
                segments.append(
                    DiceRoll(
                        raw=match["all"],
                        negative=match["op"] == "-",
                        dice=int(match["num"] or "1"),
                        faces=int(match["die"]),
                        extra=match["fun"],
                    )
                )
            else:
                segments.append(
                    ConstantModifier(
                        raw=match["all"],
                        negative=match["op"] == "-",
                        number=int(match["num"]),
                    )
                )

        batches.append(segments)

    return batches
