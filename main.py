import nextcord
import os
import discordTokens
import sys
import datetime
import time

from nextcord.ext import commands
from baseutils import *

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix=get_config("BOT", "command prefix", "s!"), intents=intents)
start_time = time.time()

### COGS ###


@bot.command()
async def load(ctx, extension):
    """Loads Cog

    Loads cog.
    Permission needed: Sersi contributor"""
    if is_sersi_contrib(ctx.author):
        try:
            bot.load_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.reply("Cog already loaded.")
    else:
        await ctx.reply(f"{get_config('EMOTES', 'fail')} Only Sersi contributors are able to load cogs.")


@bot.command()
async def unload(ctx, extension):
    """Unload Cog

    Unloads cog.
    Permission needed: Sersi contributor"""
    if is_sersi_contrib(ctx.author):
        try:
            bot.unload_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} unloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            await ctx.reply(f"Cog {extension} was not loaded.")
    else:
        await ctx.reply(f"{get_config('EMOTES', 'fail')} Only Sersi contributors are able to unload cogs.")


@bot.command()
async def reload(ctx, extension):
    """Reload Cog

    Reloads cog. If cog wasn't loaded, loads cog.
    Permission needed: Sersi contributor"""
    if is_sersi_contrib(ctx.author):
        try:
            bot.unload_extension(f"cogs.{extension}")
            bot.load_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} reloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            try:
                bot.load_extension(f"cogs.{extension}")
                await ctx.reply(f"Cog {extension} loaded.")
            except commands.errors.ExtensionNotFound:
                await ctx.reply("Cog not found.")
            except commands.errors.ExtensionAlreadyLoaded:
                await ctx.reply("Cog already loaded.")
    else:
        await ctx.reply(f"{get_config('EMOTES', 'fail')} Only Sersi contributors are able to reload cogs.")


### GENERAL COMMANDS ###


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


### BOT EVENTS ###


@bot.event
async def on_message_edit(before, after):
    """treats edited messages like new messages when it comes to scanning"""
    bot.dispatch('message', after)


@bot.event
async def on_command_error(ctx, error):
    """brings command errors to the frontend"""
    await ctx.send(f"Error while executing command: `{error}`")


@bot.event
async def on_ready():
    # load all cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Cog {filename[:-3]} loaded.")

    # files = [f for f in os.listdir('.') if os.path.isfile(f)] #unused
    print(sys.version)

    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=nextcord.Game(get_config("BOT", "status")))


@bot.event
async def on_message(message):

    if message.author == bot.user:  # ignores message if message is by bot
        return

    elif message.content == "<@839003324140355585>" or message.content == "<@977376749543387137>":
        channel = message.channel
        await channel.send(f"Hey there {message.author.mention} I am Serversicherheit, or Sersi for short! My role is to help keep Adam Something Central a safe and enjoyable space.")

    await bot.process_commands(message)

token = discordTokens.getToken()
bot.run(token)
