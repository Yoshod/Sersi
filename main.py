#Mod Buddy
#Version 0.1.2
#Written by Hekkland and Melanie

import discord
import os
import random
import discordTokens

from discord import DMChannel
from discord.ext import commands
from discord_components import DiscordComponents, ComponentsBot, Button, SelectOption, Select
from isMod import isMod
from offence import getOffenceList

from slurdetector import *

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="mb!", intents=intents)

#I wish I could move this to slurdetector.py, but the @bot.command() won't work there --Melanie
@bot.command()
async def addslur(ctx, slur):
	if isMod(ctx.author.roles):
		slur = clearString(slur)
		await ctx.send(f"Slur to be added: {slur}")
		with open("slurs.txt", "a") as file:
			file.write(slur)
			file.write("\n")
		await ctx.send("Slur added. Detection will start after the bot has been restarted.")

@bot.command()
async def addgoodword(ctx, word):
	if isMod(ctx.author.roles):
		word = clearString(word)
		await ctx.send(f"Goodword to be added: {word}")
		with open("goodword.txt", "a") as file:
			file.write(word)
			file.write("\n")
		await ctx.send("Goodword added. Detection will start after the bot has been restarted.")


def checkForMods(messageData):
	modRoles=["<@&856424878437040168>","<@&963537133589643304>","<@&875805670799179799>","<@&883255791610638366>"]
	modDetected=False
	
	for modmention in modRoles:
		if modmention in messageData:
			modDetected=True

	return modDetected

@bot.event
async def on_ready():
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	load()

	print('We have logged in as {0.user}'.format(bot))
	await bot.change_presence(activity=discord.Game('OwO observes you~~~'))

@bot.command()
async def offences(ctx):
	offenceList=getOffenceList(ctx)
	await ctx.send(str(offenceList))

@bot.command()
async def punishcheck(ctx):
	embedVar = discord.Embed(
		title="Moderator Ping", 
			description="Please select an offence from the options below:", 
			color=discord.Color.from_rgb(237,91,6))
	embedVar.set_footer(text="Slur detection written by Hekkland and Melanie")
	await ctx.send(embed=embedVar,components=[
		[Button(label="Intentional Bigotry",style=4,custom_id="itentBig")]])
	

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
		embedVar = discord.Embed(
			title="Moderator Ping Acknowledgment", 
			description=(message.author.mention)+" moderators have been notified of your ping and will investigate when able to do so.", 
			color=discord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Ping detection written by Hekkland and Melanie")
		await message.channel.send(embed=embedVar)
		
		#notification for mods
		channel = bot.get_channel(897874682198511648)
		print(channel)
		embedVar = discord.Embed(
			title="Moderator Ping", 
			description="A moderation role has been pinged, please investigate the ping and take action as appropriate.\n\n__Channel:__\n"
				+str(message.channel.mention)
				+"\n\n__User:__\n"
				+str(message.author.mention)
				+"\n\n__Context:__\n"
				+str(message.content)
				+"\n\n__URL:__\n"
				+str(message.jump_url), 
			color=discord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Ping detection written by Hekkland and Melanie")
		await channel.send(embed=embedVar)
	
	elif len(slur_heat) > 0: #checks slur heat
		channel = bot.get_channel(977377171054166037)
		embedVar = discord.Embed(
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
			color=discord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Slur detection written by Hekkland and Melanie")
		await channel.send(embed=embedVar)


	"""if message.content.startswith ("mb!offencecheck"):
    if isMod(message.author.roles):
      offence=("")
      print(message.content)
      for i in range(len(message.content)-16):
        print(offence)
        offence=offence+str(message.content[i+16])
      if offence == offenceMatrix[1][0]:
        await message.channel.send ("What is the offence instance number?")

        while True:
          msg=await bot.wait_for("message")
        if str(msg) == str(1) and msg.author == message.author:
          await message.channel.send ("The appropriate punishment is "+str(offenceMatrix[1][1]))"""

	await bot.process_commands(message)
token=discordTokens.getToken()
bot.run(token)
