"""
Sersi
Version 1.2.0 Development Build 00051
Hekkland, Melanie, Gombik
"""

import nextcord
import os
import random
import discordTokens
import sys
import asyncio

from nextcord import DMChannel
from nextcord.ext import commands
from baseutils import *
from offence import getOffenceList

from slurdetector import *

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="s!", intents=intents)

### GENERAL COMMANDS ###

@bot.command()
async def ping(ctx):
	await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

### MESSAGE FILTER COMMANDS ###

#I wish I could move this to slurdetector.py, but the @bot.command() won't work there --Melanie
@bot.command()
async def addslur(ctx, slur):
	if isMod(ctx.author.roles):
		slur = clearString(slur)
		await ctx.send(f"Slur to be added: {slur}")
		with open("slurs.txt", "a") as file:
			file.write(slur)
			file.write("\n")
		load_slurs()	#reloads updated list into memory
		
		#logging
		channel = bot.get_channel(getLoggingChannel(ctx.message.guild.id))
		embedVar = nextcord.Embed(
			title="Slur Added",
				description="A new slur has been added to the filter.\n\n__Added By:__\n"
				+str(ctx.message.author.mention)
				+" ("
				+str(ctx.message.author.id)
				+")\n\n__Slur Added:__\n"
				+str(slur),
				color=nextcord.Color.from_rgb(237,91,6))
		await channel.send(embed=embedVar)
		await ctx.send("Slur added. Detection will start now.")

@bot.command()
async def addgoodword(ctx, word):
	if isMod(ctx.author.roles):
		word = clearString(word)
		await ctx.send(f"Goodword to be added: {word}")
		with open("goodword.txt", "a") as file:
			file.write(word)
			file.write("\n")
		load_goodwords()	#reloads updated list into memory

		#logging
		channel = bot.get_channel(getLoggingChannel(ctx.message.guild.id))
		embedVar = nextcord.Embed(
			title="Goodword Added",
				description="A new goodword has been added to the filter.\n\n__Added By:__\n"
				+str(ctx.message.author.mention)
				+" ("
				+str(ctx.message.author.id)
				+")\n\n__Goodword Added:__\n"
				+str(word),
				color=nextcord.Color.from_rgb(237,91,6))
		await channel.send(embed=embedVar)
		await ctx.send("Goodword added. Detection will start now.")

@bot.command()
async def removeslur(ctx, slur):
	if isMod(ctx.author.roles):
		slurList=[]
		slur=clearString(slur)
		await ctx.send(f"Slur to be removed: {slur}")
		with open("slurs.txt", "+") as file:
			for line in file:
				slurList.append(line[0:-1])
			if slur in slurList:
				slurList.remove(slur)
				for line in file:
					file.write(slurList[line])
					file.write("\n")
				load_slurs()
				await ctx.send("Slur removed. The word will no longer be detected.")
			else:
				ctx.send(f"{slur} is not in the list of slurs.")
				

@bot.command()
async def listslurs(ctx):
	wordlist = []
	with open("slurs.txt", "r") as file:
		for line in file:
			wordlist.append(line[0:-1])
	embedVar = nextcord.Embed(
		title="List of currently detected slurs",
			description=str(sorted(wordlist)),
			color=nextcord.Color.from_rgb(237,91,6))
	await ctx.send(embed=embedVar)
	
@bot.command()
async def listgoodwords(ctx):
	wordlist = []
	with open("goodword.txt", "r") as file:
		for line in file:
			wordlist.append(line[0:-1])
	embedVar = nextcord.Embed(
		title="List of words currently whitelisted from slur detection",
			description=str(sorted(wordlist)),
			color=nextcord.Color.from_rgb(237,91,6))
	await ctx.send(embed=embedVar)


@bot.command()
async def reload(ctx):
	if isMod (ctx.author.roles):
		load_goodwords()
		load_slurs()

		#Logging
		channel = bot.get_channel(getLoggingChannel(ctx.message.guild.id))
		embedVar = nextcord.Embed(
			title="Slurs and Goodwords Reloaded",
				description="The list of slurs and goodwords in memory has been reloaded.\n\n__Reloaded By:__\n"
				+str(ctx.message.author.mention)
				+" ("
				+str(ctx.message.author.id),
				color=nextcord.Color.from_rgb(237,91,6))
		await channel.send(embed=embedVar)

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

		elif userId == None and args != None:
			await ctx.send("No user was specified.")

		elif userId != None and args == None:
			await ctx.send("No message was specified.")
		else:
			await ctx.send("How the fuck did this error appear?")
	else:
		await ctx.send("You do not have permission to use this command.")

### BOT EVENTS ###

@bot.event
async def on_ready():
	#files = [f for f in os.listdir('.') if os.path.isfile(f)] #unused
	load_slurdetector()
	print (sys.version)

	print('We have logged in as {0.user}'.format(bot))
	await bot.change_presence(activity=nextcord.Game('OwO observes you~~~'))

@bot.event
async def on_message(message):
	slur_heat = detectSlur(message.content)
    
	if message.author == bot.user: #ignores message if message is by bot
		return
	
	elif message.content == "<@839003324140355585>" or message.content == "<@977376749543387137>":
		channel=message.channel
		await channel.send("Hey there "
			+str(message.author.mention)
			+" I am Serversicherheit, or Sersi for short! My role is to help keep Adam Something Central a safe and enjoyable space.")
	
	#skips subsequent checks if message sent by moderator
	elif isMod(message.author.roles): pass
	
	elif checkForMods(message.content): #checks moderator ping
	
		#reply to user
		embedVar = nextcord.Embed(
			title="Moderator Ping Acknowledgment", 
			description=(message.author.mention)+" moderators have been notified of your ping and will investigate when able to do so.", 
			color=nextcord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Ping detection written by Hekkland and Melanie")
		await message.channel.send(embed=embedVar)
		
		#notification for mods
		channel = bot.get_channel(getAlertChannel(message.guild.id))
		print(channel)
		embedVar = nextcord.Embed(
			title="Moderator Ping", 
			description="A moderation role has been pinged, please investigate the ping and take action as appropriate.\n\n__Channel:__\n"
				+str(message.channel.mention)
				+"\n\n__User:__\n"
				+str(message.author.mention)
				+"\n\n__Context:__\n"
				+str(message.content)
				+"\n\n__URL:__\n"
				+str(message.jump_url), 
			color=nextcord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Ping detection written by Hekkland and Melanie")
		await channel.send(embed=embedVar)
	
	elif len(slur_heat) > 0: #checks slur heat
		channel = bot.get_channel(getAlertChannel(message.guild.id))
		embedVar = nextcord.Embed(
			title="Slur(s) Detected", 
			description="A slur has been detected. Moderation action is advised\n\n__Channel:__\n"
				+str(message.channel.mention)
				+"\n\n__User:__\n"
				+str(message.author.mention)
				+"\n\n__Context:__\n"
				+str(message.content)
				+"\n\n__Slurs Found:__\n"
				+str(slur_heat)
				+"\n\n__URL:__\n"
				+str(message.jump_url), 
			color=nextcord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Slur detection written by Hekkland and Melanie")
		await channel.send(embed=embedVar)
		
	await bot.process_commands(message)
	
token=discordTokens.getToken()
bot.run(token)