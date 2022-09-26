import os
import traceback
from nextcord.ext import commands
from configutils import Configuration


async def load_all_cogs(bot, *, config: Configuration, root_folder: str):
    for root, dirs, files in os.walk(f"./cogs"):
        for filename in files:
            if filename.endswith('.py'):

                nroot = root[6:].replace(os.sep, '.')

                print(f"Loading cogs{nroot}.{filename[:-3]}...")

                try:
                    bot.load_extension(f"cogs{nroot}.{filename[:-3]}", extras={"config": config, "data_folder": f"{root_folder}/persistent_data"})
                except commands.errors.ExtensionFailed:
                    print(f"Could not load cogs{nroot}.{filename[:-3]}.")
                    traceback.print_exc()


async def reload_all_cogs(bot, *, config: Configuration, root_folder: str):
    for root, dirs, files in os.walk(f"./cogs"):
        for filename in files:
            if filename.endswith('.py'):

                nroot = root[6:].replace(os.sep, '.')

                print(f"Reloading cogs{nroot}.{filename[:-3]}...")

                bot.unload_extension(f"cogs{nroot}.{filename[:-3]}")
                try:
                    bot.load_extension(f"cogs{nroot}.{filename[:-3]}", extras={"config": config, "data_folder": f"{root_folder}/persistent_data"})
                except commands.errors.ExtensionFailed:
                    print(f"Could not load cogs{nroot}.{filename[:-3]}.")
                    traceback.print_exc()
