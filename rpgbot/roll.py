"""Dice rolling extension"""

# stdlib
from dataclasses import dataclass
from random import randint, seed
from re import compile

# 3rd party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext.commands import Bot, check, command, Context

# api
from aethersprite import log
from aethersprite.authz import channel_only
from aethersprite.emotes import THUMBS_DOWN

roll_regex = compile(
    r"^(?P<all>(?P<num>\d*)d(?P<die>\d+)(?P<fun>!\d*|k[hl]\d*)?)"
)
"""Regex pattern for initial roll"""

addl_roll_regex = compile(
    r"(?P<all>(?P<op>[-+])(?P<num>\d*)(d(?P<die>\d+)(?P<fun>!\d*|k[hl]\d*)?)?)"
)
"""Regex pattern for additional modifier rolls/constants"""

explode_regex = compile(r"!(?P<num>\d*)")
"""Regex for exploding die extra"""

keep_hilow_regex = compile(r"(?P<fun>k[hl])(?P<num>\d*)")
"""Regex for keep highest/lowest extras"""


@dataclass
class RollSegment:
    raw: str
    negative: bool = False


@dataclass
class DiceRoll(RollSegment):
    dice: int = 0
    faces: int = 0
    extra: str | None = None


@dataclass
class ConstantModifier(RollSegment):
    number: int = 0


@dataclass
class SegmentResult:
    segment: RollSegment
    rolls: list[int] | None = None
    work: str | None = None
    total: int = 0


def segment_icon(segment: RollSegment):
    """Get emote icon for displaying segment result in an Embed."""

    if isinstance(segment, DiceRoll):
        return ":game_die:"

    if isinstance(segment, ConstantModifier):
        return ":1234:"


def parse_segments(roll: str) -> list[RollSegment]:
    """Parse a roll formula string into a list of RollSegment objects."""

    segments = []

    # strip all whitespace
    roll = roll.replace(" ", "")

    # parse first roll
    match = roll_regex.match(roll)
    assert match
    match = match.groupdict()
    segments.append(
        DiceRoll(
            raw=match["all"],
            dice=int(match["num"] or "1"),
            faces=int(match["die"]),
            extra=match["fun"],
        )
    )

    # parse variable number of mods
    rest = [r.groupdict() for r in addl_roll_regex.finditer(roll)]

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

    return segments


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


@check(channel_only)
@command()
async def roll(ctx: Context, *, dice: str):
    """
    Roll them bones.

    Examples:
        # roll a single d20
        !roll d20

        # 2d20, keep highest
        !roll 2d20kh

        # 4d20, keep lowest 2, plus 1
        !roll 4d20kl2+1

        # 3d6, explode
        !roll 3d6!

        # 4d6, explode up to 3x, minus 1d4
        !roll 4d6!3-1d4
    """

    try:
        segments = parse_segments(dice)
        results = [roll_segment(s) for s in segments]
    except Exception:
        log.exception("Error parsing dice roll")
        await ctx.message.add_reaction(THUMBS_DOWN)
        return

    embed = Embed(
        title=f"Roll: `{dice}`",
        color=Color.purple(),
    )
    embed.set_author(
        name=ctx.author.name,
        icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
    )

    for result in results:
        embed.add_field(
            name=f"{segment_icon(result.segment)} {result.segment.raw}",
            value=result.work if isinstance(result.segment, DiceRoll) else "",
        )

    totals = [s.total for s in results]
    grand_total = sum(totals)
    embed.add_field(
        name=":checkered_flag: Total",
        value=f"{totals} = **{grand_total}**",
        inline=False,
    )
    await ctx.send(embed=embed)
    await ctx.message.delete()


async def setup(bot: Bot):
    seed()
    bot.add_command(roll)
