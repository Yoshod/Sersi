import nextcord
import os
import discordTokens
import sys
import datetime
import time


from nextcord.ext import commands
from baseutils import *
from config import *

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="s!", intents=intents)
start_time = time.time()

### COGS ###


@bot.command()
async def load(ctx, extension):
    """Loads Cog

    Loads cog.
    Permission needed: Sersi contributor"""
    if isSersiContrib(ctx.author.roles):
        try:
            bot.load_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.reply("Cog already loaded.")
    else:
        await ctx.reply("<:sersifail:979070135799279698> Only Sersi contributors are able to load cogs.")


@bot.command()
async def unload(ctx, extension):
    """Unload Cog

    Unloads cog.
    Permission needed: Sersi contributor"""
    if isSersiContrib(ctx.author.roles):
        try:
            bot.unload_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} unloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            await ctx.reply(f"Cog {extension} was not loaded.")
    else:
        await ctx.reply("<:sersifail:979070135799279698> Only Sersi contributors are able to unload cogs.")


@bot.command()
async def reload(ctx, extension):
    """Reload Cog

    Reloads cog. If cog wasn't loaded, loads cog.
    Permission needed: Sersi contributor"""
    if isSersiContrib(ctx.author.roles):
        try:
            bot.unload_extension(f"cogs.{extension}")
            bot.load_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} reloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            await load(extension)
    else:
        await ctx.reply("<:sersifail:979070135799279698> Only Sersi contributors are able to reload cogs.")

### CONFIGURATION COMMANDS ###

@bot.command(aliases=['config', 'conf'])
async def configuration(ctx):
    if not isStaff(ctx.author.roles):
        await ctx.reply("<:sersifail:979070135799279698> Only staff members can view configuration")
        return

    config_embed = nextcord.Embed(
        title="Available Configuration Options:",
        color=nextcord.Color.from_rgb(237, 91, 6))
    for subsection in get_config_sections():
        sub_config_str = ""
        for field in subsection:
            if subsection.name == "CHANNELS":
                channel = ctx.guild.get_channel(int(subsection[field]))
                sub_config_str += f"__**{field}**__\n"

                if channel is None:
                    sub_config_str += f"`{subsection[field]}`\n*channel not found!*\n"
                else:
                    sub_config_str += f"{channel.mention}\n"

            elif subsection.name == "ROLES":
                role = ctx.guild.get_role(int(subsection[field]))
                sub_config_str += f"__**{field}**__\n"

                if role is None:
                    sub_config_str += f"`{subsection[field]}`\n*role not found!*\n"
                else:
                    sub_config_str += f"{role.mention}\n"
            else:
                sub_config_str += f"__**{field}**__\n`{subsection[field]}\n`"
        config_embed.add_field(name=subsection.name, value = sub_config_str)
    await ctx.send(embed=config_embed)


@bot.command(aliases=['reloadconfig', 'reloadconf', 'relconfig', 'relconf'])
async def reloadconfiguration(ctx):
    """Reloads configuration from config.ini"""
    if not isSersiContrib(ctx.author.roles):
        await ctx.reply("<:sersifail:979070135799279698> Only Sersi contributors are able to change configuration.")
        return
        
    load_config()
    await ctx.send(f"<:sersisuccess:979066662856822844> configuration has been reloaded form 'config.ini'")
        

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
    load_config()    # load configuration

    ajustCommandPrefix(bot)  # change prefix to cs! if Sersi(cracked)

    # load all cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Cog {filename[:-3]} loaded.")

    # files = [f for f in os.listdir('.') if os.path.isfile(f)] #unused
    print(sys.version)

    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=nextcord.Game('Sword and Shield of the Server'))


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
