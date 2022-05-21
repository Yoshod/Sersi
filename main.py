#Mod Buddy
#Version 0.1.0
#Written by Hekkland and Melanie


import discord
import os
import random
from itertools import product 	#needed for slur obscurity permutations
import unidecode				#needed for cleaning accents and diacritic marks
from discord import DMChannel
from discord.ext import commands
slurs = []

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix="mb!", intents=intents)

offenceList=["Intentional Bigotry","Unintentional Bigotry","Spam","NSFW Content","Channel Misuse"]

def leet(word):
	substitutions = {
		"a": ("a", "@", "*", "4"),
		"i": ("i", "*", "l", "1"),
		"o": ("o", "*", "0", "@"),
		"u": ("u", "*", "v"),
		"v": ("v", "*", "u"),
		"l": ("l", "1"),
		"e": ("e", "*", "3", "€", "ε"),
		"s": ("s", "$", "5"),
		"t": ("t", "7"),
		"y": ("y", "¥"),
		"n": ("n", "и"),
		"r": ("r", "я", "®"),
		"t": ("t", "†"),
	}
	possibles = []
	for char in word.lower():
		options = substitutions.get(char, char)
		possibles.append(options)
		
	#print(possibles)
	return [''.join(permutations) for permutations in product(*possibles)]

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
		if "856424878437040168" == str(role.id):
			modRolePresent=True
		elif "883255791610638366" == str(role.id):
			modRolePresent=True
		elif "977394150494326855" == str(role.id):
			modRolePresent=True
	#print(modRolePresent)
	return (modRolePresent)

@bot.event
async def on_ready():
	files = [f for f in os.listdir('.') if os.path.isfile(f)]
	#for f in files:
		#print (files)
	with open("slurs.txt", "r") as file:
		for line in file:
			line = line.replace('\n', '')
			slurs.extend(leet(line))
	#print(slurs) #will print the very long list, feel free to comment out for performance reasons

	print('We have logged in as {0.user}'.format(bot))
	await bot.change_presence(activity=discord.Game('OwO observes you~~~'))

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

#cleaning up the message by eliminating special characters and making the entire message lowercase    
def clearString(string):
	special_characters = ['!', '#', '%', '&', '[', ']', ' ', ']', '_', '-', '<', '>']

	string = string.lower()
	string = unidecode.unidecode(string)
	
	for char in special_characters:
		string = string.replace(char, '')
	
	return string

def detectSlur(messageData):
	#known slurs and safe words; both lists can be amended freely
	#WORDS MUST BE LOWERCASE
	#slurs = ["spick", "coon", "trann", "fag", "retard", "nigg", "kike", "yid", "chink", "gook", "negro", "shemale", "e621", "killyourself", "kys", "gypsy", "809891646606409779", "spastic", "spas", "spaz", "darky", "gippo", "paki", "spic", "dyke", "shizo", "mong"]
	goodword = ["skyscraper", "montenegro", "pakistan", "spicy", "among", "mongrel", "schizophrenia", "zelenskys", "tycoon", "suspicious", "racoon", "yiddish"]
	
	cleanedMessageData = clearString(messageData)
	messageData = messageData.lower()
	messageData = messageData.replace(' ', '')
	#print("scan:", messageData, cleanedMessageData)
	#if a slur is detected, we increase by 1, if a word that cointains a slur but is safe is found, you get a free pass (substracting that increment), any slur that is not exused that way will be reported
	slur_counter = 0 #more like based_counter, amirite?
	
	for slur in slurs:
		slur_counter += messageData.count(slur)
		slur_counter += cleanedMessageData.count(slur)
	for word in goodword:
		slur_counter -= messageData.count(word)
		slur_counter -= cleanedMessageData.count(word)

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
