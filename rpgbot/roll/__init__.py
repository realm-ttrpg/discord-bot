"""Dice rolling extension"""

# stdlib
from random import seed

# 3rd party
from discord.ext.commands import Bot, check, command, Context

# api
from aethersprite import log
from aethersprite.authz import channel_only
from aethersprite.emotes import THUMBS_DOWN
from aethersprite.filters import BooleanFilter
from aethersprite.settings import register, settings

# local
from .response import compact, verbose
from .parse import parse_segments
from .roll import roll_segment

compact_filter = BooleanFilter("realm.roll.compact")


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

    is_compact = settings["realm.roll.compact"].get(ctx)

    if is_compact:
        await ctx.send(compact(ctx, dice, results))
    else:
        await ctx.send(embed=verbose(ctx, dice, results))

    await ctx.message.delete()


async def setup(bot: Bot):
    register(
        "realm.roll.compact",
        False,
        lambda _: True,
        False,
        "Whether to use compact display for roll results.",
        filter=compact_filter,
    )
    seed()
    bot.add_command(roll_)


async def teardown(bot: Bot):
    global settings

    del settings["realm.roll.compact"]
