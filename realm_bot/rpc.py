# stdlib
import asyncio as aio
import json
import os
from uuid import uuid4

# 3rd party
from discord.ext.commands import Bot
import redis

# api
from aethersprite import log

bot: Bot
redis_conn = redis.StrictRedis(host=os.environ.get("REDIS_HOST", "localhost"))
pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)


class RPCHandlers:
    """
    Incoming RPC operation handler functions

    Since there are going to be a small number of operations supported by the
    bot, the handlers can be collected here as static methods instead of
    breaking each out into its own module.
    """

    @staticmethod
    def guilds(data: dict):
        """Get list of guilds the bot is joined to."""

        return [str(guild.id) for guild in bot.guilds]


def handler(message: dict):
    """Handle an incoming RPC operation and publish the result."""

    data = json.loads(message["data"])
    log.info(f"RPC op: {data['op']}")
    result = getattr(RPCHandlers, data["op"])(data)
    redis_conn.publish(data["uuid"], json.dumps(result))


async def rpc_api(op: str, *args, timeout=3, **kwargs):
    """Perform an outgoing API RPC operation and await the response."""

    q = aio.Queue()

    def handler(message: dict):
        data = json.loads(message["data"])
        aio.new_event_loop().run_until_complete(q.put(data))

    uuid = str(uuid4())
    pubsub.subscribe(**{uuid: handler})

    try:
        redis_conn.publish(
            "rpc.api",
            json.dumps(
                {
                    "uuid": uuid,
                    "op": op,
                    "args": args,
                    "kwargs": kwargs,
                }
            ),
        )

        return await aio.wait_for(q.get(), timeout)

    finally:
        pubsub.unsubscribe(uuid)


async def setup(bot_: Bot):
    global bot
    bot = bot_
    pubsub.subscribe(**{"rpc.bot": handler})
    pubsub.run_in_thread(daemon=True, sleep_time=0.01)


async def teardown(*_):
    pubsub.unsubscribe()
    pubsub.close()
