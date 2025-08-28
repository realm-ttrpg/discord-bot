"""Roll response formats (verbose vs. compact)"""

# 3rd party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext.commands import Context

# api
from realm_schema import ConstantModifier, DiceRoll, RollSegment, SegmentResult


def segment_icon(segment: RollSegment):
    """Get emote icon for displaying segment result in an Embed."""

    if isinstance(segment, DiceRoll):
        return ":game_die:"

    if isinstance(segment, ConstantModifier):
        return ":1234:"


def compact(ctx: Context, dice: str, results: list[SegmentResult]) -> str:
    """
    Compact output for dice roll results.

    Args:
        dice: The original dice roll string
        results: The list of results for the roll segments

    Returns:
        The message to be posted to the channel
    """

    rolls = "* :game_die: *".join([s.work for s in results if s.work])
    totals = [s.total for s in results]

    return "".join(
        (
            f"{ctx.author.mention} ",
            f"`{dice}` ｜ :game_die: *{rolls}* ｜ ",
            f":checkered_flag: {totals} ",
            f"= **{sum(totals)}**",
        )
    )


def verbose(ctx: Context, dice: str, results: list[SegmentResult]) -> Embed:
    """
    Verbose output for dice roll results.

    Args:
        dice: The original dice roll string
        results: The list of results for the roll segments

    Returns:
        The embed to be posted to the channel
    """

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
    embed.add_field(
        name=":checkered_flag: Total",
        value=f"{totals} = **{sum(totals)}**",
        inline=False,
    )

    return embed
