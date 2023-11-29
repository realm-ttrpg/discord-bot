"""Dice rolling extension"""

# stdlib
from random import seed

# 3rd party
from discord.colour import Color
from discord.embeds import Embed
from discord.ext.commands import Bot, check, command, Context

# api
from aethersprite import log
from aethersprite.authz import channel_only
from aethersprite.emotes import THUMBS_DOWN

# local
from .dataclasses import ConstantModifier, DiceRoll, RollSegment
from .parse import parse_segments
from .roll import roll_segment


def segment_icon(segment: RollSegment):
    """Get emote icon for displaying segment result in an Embed."""

    if isinstance(segment, DiceRoll):
        return ":game_die:"

    if isinstance(segment, ConstantModifier):
        return ":1234:"


@check(channel_only)
@command(name="roll")
async def roll_(ctx: Context, *, dice: str):
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
    bot.add_command(roll_)
