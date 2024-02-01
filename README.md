# Realm TTRPG bot for Discord

A [Discord][] bot for use with the associated [API server][] and
[web interface][] to facilitate the play and administration of
[tabletop roleplaying games][]

![realm](https://raw.githubusercontent.com/realm-ttrpg/discord-bot/assets/realm.jpg)

## Installing

First, make a `config.toml` file from the provided `config.example.toml` file,
providing it with your username, API token, and any settings tweaks you wish to
apply.

Then, install the bot package in your Python environment of choice:

```shell
pip install -U 'realm_bot@git+https://github.com/realm-ttrpg/discord-bot.git'
```

## Running

In the same directory as your `config.toml` file:

```shell
python -m aethersprite
```

[api server]: https://github.com/realm-ttrpg/api-server
[discord]: https://discord.com
[tabletop roleplaying games]: https://en.wikipedia.org/wiki/Tabletop_role-playing_game
[web interface]: https://github.com/realm-ttrpg/web-interface
