"""Roll a segment"""

# stdlib
from random import randint
from re import compile

# local
from .dataclasses import ConstantModifier, DiceRoll, RollSegment, SegmentResult

explode_regex = compile(r"!(?P<num>\d*)")
"""Regex for exploding die extra"""

keep_hilow_regex = compile(r"(?P<fun>k[hl])(?P<num>\d*)")
"""Regex for keep highest/lowest extras"""


def roll_segment(segment: RollSegment) -> SegmentResult:
    """Calculate the results of an individual RollSegment instance."""

    if isinstance(segment, ConstantModifier):
        return SegmentResult(
            segment=segment,
            total=segment.number * (-1 if segment.negative else 1),
        )

    if isinstance(segment, DiceRoll):
        limit = 0
        exploding = False
        result = SegmentResult(segment=segment, rolls=[], work="")
        assert result.rolls is not None
        assert result.work is not None

        if segment.extra and segment.extra[0] == "!":
            exploding = True

            # explosion limit
            if len(segment.extra) > 1:
                explode_limit_match = explode_regex.match(segment.extra)
                assert explode_limit_match
                limit = int(explode_limit_match.groupdict()["num"])

        # roll dice
        for _ in range(segment.dice):
            roll = randint(1, segment.faces)
            exploded = 0

            # exploding die
            while (
                exploding
                and roll == segment.faces
                and (limit == 0 or exploded < limit)
            ):
                exploded += 1
                result.rolls.append(roll)
                result.total += roll
                roll = randint(1, segment.faces)

            result.rolls.append(roll)
            result.total += roll

        # keep methods
        if segment.extra and segment.extra.startswith("k"):
            ord_rolls = sorted(result.rolls)
            args_match = keep_hilow_regex.match(segment.extra)
            assert args_match
            args = args_match.groupdict()
            fun = args["fun"]
            keep = int(args["num"]) if args["num"] else 1

            assert keep < segment.dice and keep > 0
            drop = range(segment.dice - keep)

            # keep highest
            if fun == "kh":
                for i in drop:
                    result.total -= ord_rolls[i]

            # keep lowest
            elif fun == "kl":
                for i in drop:
                    result.total -= ord_rolls[-(i + 1)]

        result.work = "".join(
            [
                f"{result.rolls} = ",
                f"**{'-' if segment.negative else ''}{result.total}**",
            ]
        )

        if segment.negative:
            result.total *= -1

        return result

    raise NotImplementedError()
