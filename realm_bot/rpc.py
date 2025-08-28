"""RPC functionality and Aethersprite extension"""

# stdlib
import asyncio as aio
import json
import os
from uuid import uuid4

# 3rd party
from discord.ext.commands import Bot
from pydantic import BaseModel
from redis.asyncio import StrictRedis

# api
from aethersprite import log
from realm_schema import BotGuildsResponse

bot: Bot
task: aio.Task
redis_conn = StrictRedis(host=os.environ.get("REDIS_HOST", "localhost"))
pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)


class RPCHandlers:
    """
    Incoming RPC operation handler functions

    Since there are going to be a small number of operations supported by the
    bot, the handlers can be collected here as static methods instead of
    breaking each out into its own module.
    """

    @staticmethod
    async def guilds(*_, **__):
        """Get list of guilds the bot is joined to."""

        return BotGuildsResponse(
            guild_ids=set([str(guild.id) for guild in bot.guilds]),
        )


async def handler(message: dict):
    """Handle an incoming RPC operation and publish the result."""

    data: dict = json.loads(message["data"])
    log.info(f"RPC op: {data['op']}")
    result: BaseModel = await getattr(RPCHandlers, data["op"])(
        *data.get("args", []),
        **data.get("kwargs", dict()),
    )
    response = result.model_dump_json()
    await redis_conn.publish(data["uuid"], response if result else "")


async def rpc_api(op: str, *args, timeout=3, **kwargs):
    """Perform an outgoing API RPC operation and await the response."""

    q = aio.Queue()

    async def handler(message: dict):
        data = message["data"]
        await q.put(data)

    uuid = str(uuid4())
    await pubsub.subscribe(**{uuid: handler})
    message = {
        "uuid": uuid,
        "op": op,
        "args": args,
        "kwargs": kwargs,
    }

    try:
        await redis_conn.publish("rpc.api", json.dumps(message))
        return await aio.wait_for(q.get(), timeout)

    finally:
        await pubsub.unsubscribe(uuid)


async def setup(bot_: Bot):
    global bot, task
    bot = bot_
    await pubsub.subscribe(**{"rpc.bot": handler})
    task = aio.create_task(pubsub.run())


async def teardown(*_):
    await pubsub.unsubscribe()
    await pubsub.close()
    task.cancel()
