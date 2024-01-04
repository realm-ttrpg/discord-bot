# Realm TTRPG bot for Discord

An extension pack for the [Aethersprite][] [Discord][] bot to facilitate the
play and administration of [tabletop roleplaying games][]

![realm](https://raw.githubusercontent.com/realm-ttrpg/discord-bot/assets/realm.jpg)

## Installing

First, make a `config.toml` file from the provided `config.example.toml` file,
providing it with your username, API token, and any settings tweaks you wish to
apply.

Then, install the bot package in your Python environment of choice:

```shell
pip install -U 'rpgbot@git+https://github.com/realm-ttrpg/discord-bot.git'
```

## Running

Commands must be run in the same directory as your `config.toml` file.

To start the Discord bot:

```shell
python -m aethersprite
```

To start the web application:

```shell
python -m aethersprite.webapp
```

[aethersprite]: https://github.com/haliphax/aethersprite
[discord]: https://discord.com
[tabletop roleplaying games]: https://en.wikipedia.org/wiki/Tabletop_role-playing_game
