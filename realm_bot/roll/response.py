"""Roll response formats (verbose vs. compact)"""

# 3rd party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext.commands import Context

# api
from realm_schema import RollResults, SegmentResult


def segment_icon(segment: SegmentResult):
    """Get emote icon for displaying segment result in an Embed."""

    if segment.work:
        return ":game_die:"

    return ":1234:"


def _success_text(results: RollResults, grand_total: int) -> str | None:
    if not results.max and not results.min:
        return None

    succeed = True

    if results.max and grand_total > results.max:
        succeed = False

    if results.min and grand_total < results.min:
        succeed = False

    if succeed:
        return ":white_check_mark:"

    return ":x:"


def compact(ctx: Context, dice: str, results: RollResults) -> str:
    """
    Compact output for dice roll results.

    Args:
        dice: The original dice roll string
        results: The list of results for the roll segments

    Returns:
        The message to be posted to the channel
    """

    rolls = "* :game_die: *".join([s.work for s in results.results if s.work])
    totals = [s.total for s in results.results]
    grand_total = sum(totals)
    success = _success_text(results, grand_total)

    return "".join(
        (
            f"{ctx.author.mention} ",
            f"`{dice}` ｜ :game_die: *{rolls}* ｜ ",
            f":checkered_flag: {totals} ",
            f"= **{grand_total}**",
            f" ｜ {success}" if success else "",
        )
    )


def verbose(ctx: Context, dice: str, results: RollResults) -> Embed:
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

    for result in results.results:
        embed.add_field(
            name=f"{segment_icon(result)} {result.segment.raw}",
            value=result.work if result.work else "",
        )

    totals = [s.total for s in results.results]
    grand_total = sum(totals)

    embed.add_field(
        name=":checkered_flag: Total",
        value=f"{totals} = **{grand_total}**",
        inline=False,
    )

    success = _success_text(results, grand_total)

    if success:
        embed.add_field(name=":trophy: Success", value=success)

    return embed
