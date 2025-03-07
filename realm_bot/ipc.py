# stdlib
import json
import os

# 3rd party
from discord.ext.commands import Bot
import redis

# api
from aethersprite import log

bot: Bot
redis_conn = redis.StrictRedis(host=os.environ.get("REDIS_HOST", "localhost"))
pubsub = redis_conn.pubsub(ignore_subscribe_messages=True)


class _IPCHandlers:
    @staticmethod
    def guilds(data: dict):
        guilds = [str(guild.id) for guild in bot.guilds]
        redis_conn.publish(data["uuid"], json.dumps({"guilds": guilds}))


def handler(message: dict):
    data = json.loads(message["data"])
    log.info(f"IPC op: {data['op']}")
    getattr(_IPCHandlers, data["op"])(data)


async def setup(bot_: Bot):
    global bot
    bot = bot_
    pubsub.subscribe(ipc=handler)
    pubsub.run_in_thread(sleep_time=0.01, daemon=True)


async def teardown(*_):
    pubsub.unsubscribe()
    pubsub.close()
