import discord
import os
import random
from discord import DMChannel
from discord.ext import commands

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="mb!", intents=intents)

offenceList=["Intentional Bigotry","Unintentional Bigotry","Spam","NSFW Content","Channel Misuse"]

"""Thanks to @kisachi#7272 (348142492245426176)
for the checkForMods function as it is much
improved upon my initial version of it"""

def checkForMods(messageData):
	modRoles=["<@&856424878437040168>","<@&963537133589643304>","<@&875805670799179799>","<@&883255791610638366>"]
	modDetected=False
	
	for modmention in modRoles:
		if modmention in messageData:
			modDetected=True

	return modDetected

def isMod(userRoles):
	modRolePresent=False
	for role in userRoles:
		print(str(role.id))
		if "856424878437040168" == str(role.id):
			modRolePresent=True
		elif "883255791610638366" == str(role.id):
			modRolePresent=True
	return (modRolePresent)

@bot.event
async def on_ready():
	print('We have logged in as {0.user}'.format(bot))
	await bot.change_presence(activity=discord.Game('Ban The Tankie'))

@bot.command()
async def offences(ctx):
	if isMod(ctx.author.roles):
		offenceOutput=str("")
		for i in range (len(offenceList)):
			if i == 0:
				offenceOutput=offenceOutput+offenceList[i]
			else:
				offenceOutput=offenceOutput+str("\n")+str(offenceList[i])
		await ctx.send("__**Adam Something Central Offence List**__\n"+str(offenceOutput))
	else:
		await ctx.send ("Only moderators can use this command.")

#cleaning up the message by eliminating special characters and making the entire message lowercase    
def clearString(string):
	special_characters = ['!', '#', '$', '%', '&', '@', '[', ']', ' ', ']', '_', '-']
	
	string = string.lower()
	for char in special_characters:
		string = string.replace(char, '')
	return string

def detectSlur(messageData):
	#known slurs and safe words; both lists can be amended freely
	#WORDS MUST BE LOWERCASE
	slurs = ["spick", "coon", "trann", "fag", "retard", "nigg", "kike", "yid", "chink", "gook", "negro", "shemale", "e621", "killyourself", "kys", "gypsy", "<@!809891646606409779>", "spastic", "spas", "spaz", "darky", "gippo", "paki", "spic", "dyke", "shizo", "mong"]
	goodword = ["skyscraper", "montenegro", "pakistan", "spicy", "among", "mongrel", "schizophrenia", "zelenskys", "tycoon", "suspicious", "racoon", "yiddish"]
	
	messageData = clearString(messageData)
	
	#if a slur is detected, we increase by 1, if a word that cointains a slur but is safe is found, you get a free pass (substracting that increment), any slur that is not exused that way will be reported
	slur_counter = 0 #more like based_counter, amirite?
    
	for slur in slurs:
		slur_counter += messageData.count(slur)
	for word in goodword:
		slur_counter -= messageData.count(word)

	return slur_counter
	
## I sure hope My pakistani friends and myself will be able to enjoy our spicy noodles among the beautiful skyscrapers of Montenegro	--Pando	

@bot.event
async def on_message(message):
	slur_heat = detectSlur(message.content)
	
	if message.author == bot.user: #ignores message if message is by bot
		return

	elif checkForMods(message.content): #checks moderator ping
	
		#reply to user
		embedVar = discord.Embed(
			title="Moderator Ping Acknowledgment", 
			description=(message.author.mention)+" moderators have been notified of your ping and will investigate when able to do so.", 
			color=discord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Ping detection written by Hekkland and Melanie")
		await message.channel.send(embed=embedVar)
		
		#notification for mods
		channel = bot.get_channel(977377171054166037)
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
	
	elif slur_heat > 0: #checks slur heat
		#notification for mods
		channel = bot.get_channel(977377171054166037)
		embedVar = discord.Embed(
			title="Slur(s) Detected", 
			description="A slur has been detected. Moderation action is advised\n\n__Channel:__\n"
				+str(message.channel.mention)
				+"\n\n__User:__\n"
				+str(message.author.mention)
				+"\n\n__Context:__\n"
				+str(message.content)
				+"\n\n__Slur Heat:__\n"
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


bot.run("CODE HIDDEN")
