import nextcord
import os
import sys
import datetime
import time
import discordTokens

from nextcord.ext import commands

import configutils
from permutils import permcheck, is_sersi_contrib

bot = commands.Bot(intents=nextcord.Intents.all())
start_time = time.time()
config = configutils.Configuration.from_yaml_file("./persistent_data/config.yaml")
root_folder = os.path.dirname(os.path.realpath(__file__))


### COGS ###


@bot.command()
async def load(ctx, extension):
    """Loads Cog

    Loads cog.
    Permission needed: Sersi contributor"""
    if await permcheck(ctx, is_sersi_contrib):
        try:
            bot.load_extension(f"cogs.{extension}", extras={"config": config, "data_folder": f"{root_folder}/persistent_data"})
            await ctx.reply(f"Cog {extension} loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.reply("Cog already loaded.")
    else:
        await ctx.reply(f"{config.emotes.fail} Only Sersi contributors are able to load cogs.")


@bot.command()
async def unload(ctx, extension):
    """Unload Cog

    Unloads cog.
    Permission needed: Sersi contributor"""
    if await permcheck(ctx, is_sersi_contrib):
        try:
            bot.unload_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} unloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            await ctx.reply(f"Cog {extension} was not loaded.")
    else:
        await ctx.reply(f"{config.emotes.fail} Only Sersi contributors are able to unload cogs.")


@bot.command()
async def reload(ctx, extension):
    """Reload Cog

    Reloads cog. If cog wasn't loaded, loads cog.
    Permission needed: Sersi contributor"""
    if await permcheck(ctx, is_sersi_contrib):
        try:
            bot.unload_extension(f"cogs.{extension}")
            bot.load_extension(f"cogs.{extension}", extras={"config": config, "data_folder": f"{root_folder}/persistent_data"})
            await ctx.reply(f"Cog {extension} reloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            try:
                bot.load_extension(f"cogs.{extension}", extras={"config": config, "data_folder": f"{root_folder}/persistent_data"})
                await ctx.reply(f"Cog {extension} loaded.")
            except commands.errors.ExtensionNotFound:
                await ctx.reply("Cog not found.")
            except commands.errors.ExtensionAlreadyLoaded:
                await ctx.reply("Cog already loaded.")
    else:
        await ctx.reply(f"{config.emotes.fail} Only Sersi contributors are able to reload cogs.")


@bot.command()
async def uptime(ctx):
    """Displays Sersi's uptime"""
    sersi_uptime = str(datetime.timedelta(seconds=int(round(time.time() - start_time))))
    embedVar = nextcord.Embed(
        title="Sersi Uptime",
        description=f"Sersi has been online for:\n`{sersi_uptime}`",
        color=nextcord.Color.from_rgb(237, 91, 6))
    await ctx.send(embed=embedVar)


@bot.command()
async def ping(ctx):
    """test the response time of the bot"""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')


@bot.event
async def on_message_edit(before, after):
    """treats edited messages like new messages when it comes to scanning"""
    bot.dispatch('message', after)


@bot.event
async def on_ready():
    # load all cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f"cogs.{filename[:-3]}", extras={"config": config, "data_folder": f"{root_folder}/persistent_data"})
            print(f"Cog {filename[:-3]} loaded.")

    # files = [f for f in os.listdir('.') if os.path.isfile(f)] #unused
    print(f"System Version:\n{sys.version}")

    print(f"Nextcord Version:\n{nextcord.__version__}")

    print(f"We have logged in as {bot.user}")

    bot.command_prefix = config.prefix
    await bot.change_presence(activity=nextcord.Game(config.status))


@bot.event
async def on_message(message):

    if message.author == bot.user:  # ignores message if message is this bot
        return

    elif bot in message.mentions:
        channel = message.channel
        await channel.send(f"Hey there {message.author.mention} I am Serversicherheit, or Sersi for short! My role is to help keep Adam Something Central a safe and enjoyable space.")

    await bot.process_commands(message)

token = config.token
bot.run(discordTokens.getToken())
