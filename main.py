import nextcord
import os
import discordTokens
import sys


from nextcord.ext import commands
from baseutils import *

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="s!", intents=intents)


### COGS ###


@bot.command()
async def load(ctx, extension):
    if isSersiContrib(ctx.author.roles):
        try:
            bot.load_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.reply("Cog already loaded.")


@bot.command()
async def unload(ctx, extension):
    if isSersiContrib(ctx.author.roles):
        try:
            bot.unload_extension(f"cogs.{extension}")
            await ctx.reply(f"Cog {extension} unloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            await ctx.reply(f"Cog {extension} was not loaded.")


@bot.command()
async def reload(ctx, extension):
    if isSersiContrib(ctx.author.roles):
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


### GENERAL COMMANDS ###


@bot.command()
async def ping(ctx):
    """test the response time of the bot"""
    await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

### DEBUG AND MISC COMMANDS ###


@bot.command()
async def dmTest(ctx, userId=None, *, args=None):
    if isMod(ctx.author.roles):
        if userId is not None and args is not None:
            target = userId
            targetId = "Null"
            for i in range(len(target)):
                currentChar = target[i]
                charTest = currentChar.isdigit()
                print(charTest)
                if charTest is True and targetId is not "Null":
                    targetId = str(targetId) + str(target[i])
                    print("Character is number")
                elif charTest is True and targetId is "Null":
                    targetId = str(target[i])
            targetId = int(targetId)
            user = bot.get_user(targetId)
            try:
                await user.send(args)

            except:
                await ctx.send("The message failed to send. Reason: Could not DM user.")

            # Logging
            channel = bot.get_channel(getLoggingChannel(ctx.message.guild.id))
            embedVar = nextcord.Embed(
                title="DM Sent",
                description="A DM has been sent.\n\n__Sender:__\n{ctx.author.mention}\n\n__Recipient:__\n{userId}\n\n__Message Content:__\n{args}",
                color=nextcord.Color.from_rgb(237, 91, 6))
            await channel.send(embed=embedVar)

        elif userId is None and args is not None:
            await ctx.send("No user was specified.")

        elif userId is not None and args is None:
            await ctx.send("No message was specified.")
        else:
            await ctx.send("How the fuck did this error appear?")
    else:
        await ctx.send("Only moderators can use this command.")

### BOT EVENTS ###


@bot.event
async def on_ready():
    # load all cogs
    for filename in os.listdir('./cogs'):
        print("found file", filename)
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')
            print(f"Cog {filename[:-3]} loaded.")

    # files = [f for f in os.listdir('.') if os.path.isfile(f)] #unused
    print(sys.version)

    print('We have logged in as {0.user}'.format(bot))
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
