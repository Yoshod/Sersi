import time
import nextcord
import os
import sys

from nextcord.ext import commands
from nextcord.ext.commands.errors import ExtensionFailed

from configuration.configuration import Configuration
from utilities.cogs import load_cog


config     = Configuration.from_yaml_file("data/config.yml")
bot        = commands.Bot(command_prefix=config.prefix, intents=nextcord.Intents.all())
start_time = time.time()


@bot.event
async def on_ready():
    print(f"Python: {sys.version}\nnextcord: {nextcord.__version__}\n\nLogged in as {bot.user}.\n\nLoading cogs...")

    count = 0
    failed_count = 0
    for filename in os.listdir("cogs"):
        if not filename.endswith(".py"):
            continue

        try:
            load_cog(bot, filename[:-3], config, start_time)
            print(f"-> {filename[:-3]}")
            count += 1
        except ExtensionFailed as ex:
            print(f"-> {filename[:-3]} failed: {ex.original}")
            failed_count += 1

    if failed_count > 0:
        print(f"Successfully loaded {count} cogs, failed to load {failed_count} cogs.")
    else:
        print(f"Successfully loaded {count} cogs.")

    await bot.change_presence(activity=nextcord.Game(config.activity))


@bot.event
async def on_message(message: nextcord.Message):
    if message.author.bot:
        return

    if message.guild is not None and message.content == bot.user.mention:
        await message.channel.send(f"Hey there {message.author.mention}, I am **Serversicherheit**, or **Sersi** for short! My role is to help keep {message.guild.name} a safe and enjoyable space.")
        return

    await bot.process_commands(message)


bot.run(config.token)
