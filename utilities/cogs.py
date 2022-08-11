from nextcord.ext import commands

from configuration.configuration import Configuration
from database.database import Database
from sersi import Sersi


# Loads the cog by the given name.
#
# bot:         The bot instance to load the given cog for.
# name:        The name of the cog to load. It already includes cogs., and doesn't need ".py" at the end.
# config:      The loaded configuration.
# database:    The connected database.
# start_time:  The timestamp of when the bot was launched.
# data_folder: The absolute path to the data folder.
#
# Exceptions are passed down as-is.
def load_cog(bot: Sersi, name: str, config: Configuration, database: Database, start_time: float, data_folder: str):
    if config.cogs.disabled is not None and name in config.cogs.disabled:
        raise commands.ExtensionFailed(name, Exception("Tried loading a disabled cog"))

    bot.load_extension(f"cogs.{name}", extras={"config": config, "database": database, "start_time": start_time, "data_folder": data_folder})


# Unloads the cog by the given name.
#
# bot:  The bot instance to unload the given cog from.
# name: The name of the cog. It already includes cogs., and doesn't need ".py" at the end.
#
# Exceptions are passed down as-is.
def unload_cog(bot: Sersi, name: str):
    bot.unload_extension(f"cogs.{name}")
