"""
Sersi, the ASC moderation helper bot

**Version:** `2.0.0 Development Build 00095`

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

intents = nextcord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="s!", intents=intents)
notModFail="Only moderators can use this command."

### COGS ###

@bot.command()
async def load(ctx, extension):
	bot.load_extension(f"cogs.{extension}")
	await ctx.reply(f"Cog {extension} loaded.")

@bot.command()
async def unload(ctx, extension):
	bot.unload_extension(f"cogs.{extension}")
	await ctx.reply(f"Cog {extension} unloaded.")

### GENERAL COMMANDS ###

@bot.command()
async def about(ctx):
	"""shows basic information about the bot"""
	embedVar = nextcord.Embed(
		title="About Sersi", description=__doc__, color=nextcord.Color.from_rgb(237,91,6))
	await ctx.send(embed=embedVar)

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
	new_embed.colour=nextcord.Colour.light_grey()
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
	new_embed.colour=nextcord.Colour.brand_red()
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
	new_embed.colour=nextcord.Colour.brand_red()
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
	#slur_heat = detectSlur(message.content)
    
	if message.author == bot.user: #ignores message if message is by bot
		return
	
	elif message.content == "<@839003324140355585>" or message.content == "<@977376749543387137>":
		channel=message.channel
		await channel.send("Hey there "
			+str(message.author.mention)
			+" I am Serversicherheit, or Sersi for short! My role is to help keep Adam Something Central a safe and enjoyable space.")
	
	"""elif checkForMods(message.content): #checks moderator ping
	
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

		await channel.send(embed=embedVar, view=button_view)"""
		
	await bot.process_commands(message)
	
token=discordTokens.getToken()
bot.run(token)