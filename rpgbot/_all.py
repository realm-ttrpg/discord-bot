"""Load all command extensions"""

META_EXTENSION = True

_mods = ("roll",)
_package = __name__.replace("._all", "")


async def setup(bot):
    for m in _mods:
        await bot.load_extension(f"{_package}.{m}")


async def teardown(bot):
    for m in _mods:
        await bot.unload_extension(f"{_package}.{m}")
