import os
import traceback

from nextcord.ext import commands
from utils.config import Configuration


async def load_all_cogs(bot: commands.Bot, *, config: Configuration, data_folder: str):
    for root, dirs, files in os.walk("./cogs"):
        for filename in files:
            if filename.endswith(".py"):
                cog_category = root[2:].replace(os.sep, ".")

                print(f"Loading {cog_category}.{filename[:-3]}...")

                try:
                    bot.load_extension(
                        f"{cog_category}.{filename[:-3]}",
                        extras={"config": config, "data_folder": data_folder},
                    )
                except commands.errors.ExtensionFailed:
                    print(f"Could not load {cog_category}.{filename[:-3]}.")
                    traceback.print_exc()
    if bot.is_ready():
        await bot.sync_all_application_commands()


async def reload_all_cogs(
    bot: commands.Bot, *, config: Configuration, data_folder: str
):
    for root, dirs, files in os.walk("../cogs"):
        for filename in files:
            if filename.endswith(".py"):
                nroot = root[2:].replace(os.sep, ".")

                print(f"Reloading {nroot}.{filename[:-3]}...")

                bot.unload_extension(f"{nroot}.{filename[:-3]}")
                try:
                    bot.load_extension(
                        f"{nroot}.{filename[:-3]}",
                        extras={"config": config, "data_folder": data_folder},
                    )
                except commands.errors.ExtensionFailed:
                    print(f"Could not load {nroot}.{filename[:-3]}.")
                    traceback.print_exc()
    if bot.is_ready():
        await bot.sync_all_application_commands()
