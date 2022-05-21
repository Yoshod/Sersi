#Sersi Offences Commands
#Written by Hekkland

import discord
import isMod

def getOffenceList(ctx):
	if isMod.isMod(ctx.author.roles):
		offenceOutput=str("")
		for i in range (len(offenceList)):
			if i == 0:
				offenceOutput=offenceOutput+offenceList[i]
			else:
				offenceOutput=offenceOutput+str("\n")+str(offenceList[i])
		await ctx.send("__**Adam Something Central Offence List**__\n"+str(offenceOutput))
	else:
		await ctx.send ("Only moderators can use this command.")