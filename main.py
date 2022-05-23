"""
Sersi, the ASC moderation helper bot

**Version:** `1.2.0  Build 00086`

**Authors:** *Hekkland, Melanie, Gombik*
"""

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

from slurdetector import *

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="s!", intents=intents, help_command=None)
notModFail="Only moderators can use this command."

### GENERAL COMMANDS ###

@bot.command()
async def about(ctx):
	embedVar = nextcord.Embed(
		title="About Sersi", description=__doc__, color=nextcord.Color.from_rgb(237,91,6))
	await ctx.send(embed=embedVar)

@bot.command()
async def help(ctx, command=None):
	await get_help(ctx, command)

@bot.command()
async def ping(ctx):
	await ctx.send(f'Pong! {round(bot.latency * 1000)}ms')

### MESSAGE FILTER COMMANDS ###

#I wish I could move this to slurdetector.py, but the @bot.command() won't work there --Melanie
@bot.command()
async def addslur(ctx, slur):
	if isMod(ctx.author.roles):
		slur = clearString(slur)
		if slur in slurs:
			await ctx.send(f"{slur} is already on the list of slurs")
			return
		
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
	else:
		await ctx.send(notModFail)

@bot.command()
async def addgoodword(ctx, word):
	if isMod(ctx.author.roles):
		word = clearString(word)
		if word in goodword:
			await ctx.send(f"{word} is already on the whitelist")
			return
		
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
	else:
		await ctx.send(notModFail)

@bot.command()
async def removeslur(ctx, slur):
	if isMod(ctx.author.roles):
		rmSlur(ctx, slur)
		
		#logging
		channel = bot.get_channel(getLoggingChannel(ctx.message.guild.id))
		embedVar = nextcord.Embed(
			title="Slur Removed",
			description="A slur has been removed from the filter.\n\n__Removed By:__\n"
				+str(ctx.message.author.mention)
				+" ("
				+str(ctx.message.author.id)
				+")\n\n__Slur Removed:__\n"
				+str(slur),
			color=nextcord.Color.from_rgb(237,91,6))
		await channel.send(embed=embedVar)
		await ctx.send(f"Slur {slur} is no longer in the list")
	else:
		await ctx.send(notModFail)

@bot.command()
async def removegoodword(ctx, word):
	if isMod(ctx.author.roles):
		rmGoodword(ctx, word)
		
		#logging
		channel = bot.get_channel(getLoggingChannel(ctx.message.guild.id))
		embedVar = nextcord.Embed(
			title="Goodword Removed",
			description="A goodword has been removed from the filter.\n\n__Removed By:__\n"
				+str(ctx.message.author.mention)
				+" ("
				+str(ctx.message.author.id)
				+")\n\n__Goodword Removed:__\n"
				+str(word),
			color=nextcord.Color.from_rgb(237,91,6))
		await channel.send(embed=embedVar)
		await ctx.send(f"Goodword {word} is no longer in the list")
	else:
		await ctx.send(notModFail)

@bot.command()
async def listslurs(ctx, page=1):
	if isMod(ctx.author.roles):
		wordlist = []
		pages, index = 1, 0
	
		with open("slurs.txt", "r") as file:
			for line in file:
				wordlist.append(line[0:-1])
		wordlist.sort()
	
		#check if multiple pages are needed, 100 slurs per page will be listed
		if len(wordlist) > 100:
			pages += (len(wordlist) - 1) // 100
		
			#get the index of the current page
			index = int(page) - 1
			if index < 0:
				index = 0
			elif index >= pages:
				index = pages - 1
		
			#update the list to a subsection according to the index
			if index == (pages - 1):
				templist = wordlist[index*100:]
			else:
				templist = wordlist[index*100: index*100 + 100]
			wordlist = templist
	
		#post the list as embed
		embedVar = nextcord.Embed(
			title="List of currently detected slurs",
				description=str(", ".join(wordlist))
					 + "\n\n**page "
					 + str(index + 1)
					 + "/"
					 + str(pages)
					 + "**",
					color=nextcord.Color.from_rgb(237,91,6))
		await ctx.send(embed=embedVar)
	else:
		await ctx.send(notModFail)
	
@bot.command()
async def listgoodwords(ctx, page=1):
	if isMod(ctx.author.roles):
		wordlist = []
		pages, index = 1, 0
	
		with open("goodword.txt", "r") as file:
			for line in file:
				wordlist.append(line[0:-1])
		wordlist.sort()
	
		#check if multiple pages are needed, 100 goodwords per page will be listed
		if len(wordlist) > 100:
			pages += (len(wordlist) - 1) // 100
		
			#get the index of the current page
			index = int(page) - 1
			if index < 0:
				index = 0
			elif index >= pages:
				index = pages - 1
		
			#update the list to a subsection according to the index
			if index == (pages - 1):
				templist = wordlist[index*100:]
			else:
				templist = wordlist[index*100: index*100 + 100]
			wordlist = templist
	
		embedVar = nextcord.Embed(
			title="List of words currently whitelisted from slur detection",
				description=str(", ".join(wordlist))
					 + "\n\n**page "
					 + str(index + 1)
					 + "/"
					 + str(pages)
					 + "**",
					 color=nextcord.Color.from_rgb(237,91,6))
		await ctx.send(embed=embedVar)
	else:
		await ctx.send(notModFail)

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
				+str(ctx.message.author.id)
				+")",
				color=nextcord.Color.from_rgb(237,91,6))
		await channel.send(embed=embedVar)
	else:
		await ctx.send(notModFail)

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
	#files = [f for f in os.listdir('.') if os.path.isfile(f)] #unused
	load_slurdetector()
	print (sys.version)

	print('We have logged in as {0.user}'.format(bot))
	await bot.change_presence(activity=nextcord.Game('OwO observes you~~~'))

async def cb_action_taken(interaction):
	new_embed = interaction.message.embeds[0]
	new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=True)
	new_embed.colour=nextcord.Colour.brand_green()
	await interaction.message.edit(embed=new_embed, view=None)
	#Logging
	channel = bot.get_channel(getLoggingChannel(interaction.guild.id))
	embedLogVar = nextcord.Embed(
		title="Action Taken Pressed", 
		description="Action has been taken by a moderator in response to a report.\n\n__Report:__\n"
		+str(interaction.message.jump_url)
		+"\n\n__Moderator:__\n"
		+f"{interaction.user.mention} ({interaction.user.id})",
		color=nextcord.Color.from_rgb(237,91,6))
	await channel.send(embed=embedLogVar)

async def cb_acceptable_use(interaction):
	new_embed = interaction.message.embeds[0]
	new_embed.add_field(name="Usage Deemed Acceptable By", value=interaction.user.mention, inline=True)
	await interaction.message.edit(embed=new_embed, view=None)
	#Logging
	channel = bot.get_channel(getLoggingChannel(interaction.guild.id))
	embedLogVar = nextcord.Embed(
		title="Acceptable Use Pressed", 
		description="Usage of a slur has been deemed acceptable by a moderator in response to a report.\n\n__Report:__\n"
		+str(interaction.message.jump_url)
		+"\n\n__Moderator:__\n"
		+f"{interaction.user.mention} ({interaction.user.id})",
		color=nextcord.Color.from_rgb(237,91,6))
	await channel.send(embed=embedLogVar)

async def cb_false_positive(interaction):
	new_embed = interaction.message.embeds[0]
	new_embed.add_field(name="Deemed As False Positive By", value=interaction.user.mention, inline=True)
	await interaction.message.edit(embed=new_embed, view=None)
	channel = bot.get_channel(getFalsePositivesChannel(interaction.guild_id))
	await channel.send((interaction.message.embeds[0].description.split('\n'))[9])
	#Logging
	channel = bot.get_channel(getLoggingChannel(interaction.guild.id))
	embedLogVar = nextcord.Embed(
		title="False Positive Pressed", 
		description="Detected slur has been deemed a false positive by a moderator in response to a report.\n\n__Report:__\n"
		+str(interaction.message.jump_url)
		+"\n\n__Moderator:__\n"
		+f"{interaction.user.mention} ({interaction.user.id})", 
		color=nextcord.Color.from_rgb(237,91,6))
	await channel.send(embed=embedLogVar)

async def cb_action_not_neccesary(interaction):
	new_embed = interaction.message.embeds[0]
	new_embed.add_field(name="Action Not Neccesary", value=interaction.user.mention, inline=True)
	new_embed.colour=nextcord.Colour.light_grey()
	await interaction.message.edit(embed=new_embed, view=None)
	#Logging
	channel = bot.get_channel(getLoggingChannel(interaction.guild.id))
	embedLogVar = nextcord.Embed(
		title="Action Not Necessary Pressed", 
		description="A Moderator has deemed that no action is needed in response to a report.\n\n__Report:__\n"
		+str(interaction.message.jump_url)
		+"\n\n__Moderator:__\n"
		+f"{interaction.user.mention} ({interaction.user.id})",
		color=nextcord.Color.from_rgb(237,91,6))
	await channel.send(embed=embedLogVar)

async def cb_bad_faith_ping(interaction):
	new_embed = interaction.message.embeds[0]
	new_embed.add_field(name="Bad Faith Ping", value=interaction.user.mention, inline=True)
	new_embed.colour=nextcord.Colour.brand_green()
	await interaction.message.edit(embed=new_embed, view=None)
	#Logging
	channel = bot.get_channel(getLoggingChannel(interaction.guild.id))
	embedLogVar = nextcord.Embed(
		title="Bad Faith Ping Pressed", 
		description="A moderation ping has been deemed bad faith by a moderator in response to a report.\n\n__Report:__\n"
		+str(interaction.message.jump_url)
		+"\n\n__Moderator:__\n"
		+f"{interaction.user.mention} ({interaction.user.id})",
		color=nextcord.Color.from_rgb(237,91,6))
	await channel.send(embed=embedLogVar)

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
		
		action_taken = Button(label="Action Taken")
		action_taken.callback = cb_action_taken
		
		action_not_neccesary = Button(label="Action Not Neccesary")
		action_not_neccesary.callback = cb_action_not_neccesary

		bad_faith_ping = Button(label="Bad Faith Ping")
		bad_faith_ping.callback = cb_bad_faith_ping

		button_view = View()
		button_view.add_item(action_taken)
		button_view.add_item(action_not_neccesary)
		button_view.add_item(bad_faith_ping)

		await channel.send(embed=embedVar, view=button_view)
	
	elif len(slur_heat) > 0: #checks slur heat
		channel = bot.get_channel(getAlertChannel(message.guild.id))
		embedVar = nextcord.Embed(
			title="Slur(s) Detected", 
			description="A slur has been detected. Moderation action is advised.\n\n__Channel:__\n"
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

		action_taken = Button(label="Action Taken")
		action_taken.callback = cb_action_taken
		
		acceptable_use = Button(label="Acceptable Use")
		acceptable_use.callback = cb_acceptable_use

		false_positive = Button(label="False Positive")
		false_positive.callback = cb_false_positive

		button_view = View()
		button_view.add_item(action_taken)
		button_view.add_item(acceptable_use)
		button_view.add_item(false_positive)

		await channel.send(embed=embedVar, view=button_view)
		
	await bot.process_commands(message)
	
token=discordTokens.getToken()
bot.run(token)