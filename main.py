import nextcord
from nextcord.ui import Button, View
import os
import random
import discordTokens
import sys
import asyncio

from nextcord import DMChannel
from nextcord.ext import commands
from baseutils import *
from offence import getOffenceList
from bothelp import get_help

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="s!", intents=intents)
notModFail="Only moderators can use this command."

### COGS ###

@bot.command()
async def load(ctx, extension):
	if isSersiContrib(ctx.author.roles):
		bot.load_extension(f"cogs.{extension}")
		await ctx.reply(f"Cog {extension} loaded.")

@bot.command()
async def unload(ctx, extension):
	if isSersiContrib(ctx.author.roles):
		bot.unload_extension(f"cogs.{extension}")
		await ctx.reply(f"Cog {extension} unloaded.")

@bot.command()
async def reload(ctx, extension):
	if isSersiContrib(ctx.author.roles):
		bot.unload_extension(f"cogs.{extension}")
		bot.load_extension(f"cogs.{extension}")
		await ctx.reply(f"Cog {extension} reloaded.")

### GENERAL COMMANDS ###

@bot.command()
async def hilfe(ctx, command=None):
	await get_help(ctx, command)

@bot.command()
async def ping(ctx):
	"""test the response time of the bot"""
	await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

### PUNISHMENT GUIDELINES COMMANDS ###
# not yet implemented fully

@bot.command()
async def offences(ctx):
	offenceList=getOffenceList(ctx)
	await ctx.send(str(offenceList))

@bot.command()
async def punishcheck(ctx):
	embedVar = nextcord.Embed(
		title="Moderator Ping", 
			description="Please select an offence from the options below:", 
			color=nextcord.Color.from_rgb(237,91,6))
	embedVar.set_footer(text="Slur detection written by Hekkland and Melanie")
	await ctx.send(embed=embedVar,components=[
		[Button(label="Intentional Bigotry",style=4,custom_id="itentBig")]])

### DEBUG AND MISC COMMANDS ###

@bot.command()
async def dmTest(ctx,userId=None,*,args=None):
	if isMod (ctx.author.roles):
		if userId != None and args != None:
			target=userId
			targetId="Null"
			for i in range(len(target)):
				currentChar=target[i]
				charTest=currentChar.isdigit()
				print(charTest)
				if charTest==True and targetId!="Null":
					targetId=str(targetId)+str(target[i])
					print("Character is number")
				elif charTest==True and targetId=="Null":
					targetId=str(target[i])
			targetId=int(targetId)
			user=bot.get_user(targetId)
			try:
				await user.send(args)

			except:
				await ctx.send("The message failed to send. Reason: Could not DM user.")

			#Logging
			channel = bot.get_channel(getLoggingChannel(ctx.message.guild.id))
			embedVar = nextcord.Embed(
				title="DM Sent", 
				description="A DM has been sent.\n\n__Sender:__\n"
					+str(ctx.author.mention)
					+"\n\n__Recipient:__\n"
					+str(userId)
					+"\n\n__Message Content:__\n"
					+str(args), 
				color=nextcord.Color.from_rgb(237,91,6))
			await channel.send(embed=embedVar)

		elif userId == None and args != None:
			await ctx.send("No user was specified.")

		elif userId != None and args == None:
			await ctx.send("No message was specified.")
		else:
			await ctx.send("How the fuck did this error appear?")
	else:
		await ctx.send(notModFail)

### BOT EVENTS ###

@bot.event
async def on_ready():
	# load all cogs
	for filename in os.listdir('./cogs'):
		print("found file", filename)
		if filename.endswith('.py'):
			bot.load_extension(f'cogs.{filename[:-3]}')
			print(f"Cog {filename[:-3]} loaded.")

	#files = [f for f in os.listdir('.') if os.path.isfile(f)] #unused
	print (sys.version)

	print('We have logged in as {0.user}'.format(bot))
	await bot.change_presence(activity=nextcord.Game('OwO observes you~~~'))

@bot.event
async def on_message(message):
	#slur_heat = detectSlur(message.content)
    
	if message.author == bot.user: #ignores message if message is by bot
		return
	
	elif message.content == "<@839003324140355585>" or message.content == "<@977376749543387137>":
		channel=message.channel
		await channel.send("Hey there "
			+str(message.author.mention)
			+" I am Serversicherheit, or Sersi for short! My role is to help keep Adam Something Central a safe and enjoyable space.")
		
	await bot.process_commands(message)
	
token=discordTokens.getToken()
bot.run(token)