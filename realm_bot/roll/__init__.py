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
from ..rpc import rpc_api
from .response import compact, verbose
from .parse import parse_segments
from .roll import roll_segment

ROLL_COMPACT_SETTING = "realm.roll.compact"
"""Setting name for compact roll results toggle"""

compact_filter = BooleanFilter(ROLL_COMPACT_SETTING)
"""Boolean setting filter for compact roll results toggle"""


@check(channel_only)
@command(name="roll")
async def roll_command(ctx: Context, *, dice: str):
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

        # 4 batches of 2d6+1d4
        !roll 2d6+1d4x4
    """

    is_compact = settings[ROLL_COMPACT_SETTING].get(ctx)

    try:
        batches = parse_segments(dice)

        for segments in batches:
            results = [roll_segment(s) for s in segments]

            if is_compact:
                await ctx.send(compact(ctx, dice, results))
            else:
                await ctx.send(embed=verbose(ctx, dice, results))
    except Exception:
        log.exception("Error parsing dice roll")
        await ctx.message.add_reaction(THUMBS_DOWN)
        return

    await ctx.message.delete()
    await rpc_api("roll")


async def setup(bot: Bot):
    register(
        ROLL_COMPACT_SETTING,
        False,
        lambda _: True,
        False,
        "Whether to use compact display for roll results.",
        filter=compact_filter,
    )
    seed()
    bot.add_command(roll_command)


async def teardown(bot: Bot):
    global settings

    del settings[ROLL_COMPACT_SETTING]
