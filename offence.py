#Sersi Offences Commands
#Written by Hekkland

import discord
import isMod

offenceList=["Intentional Bigotry","Unintentional Bigotry","Spam","NSFW Content","Channel Misuse"]

def getOffenceList(ctx):
	if isMod.isMod(ctx.author.roles):
		offenceOutput=str("")
		for i in range (len(offenceList)):
			if i == 0:
				offenceOutput=offenceOutput+offenceList[i]
			else:
				offenceOutput=offenceOutput+str("\n")+str(offenceList[i])
		return(output=("__**Adam Something Central Offence List**__\n"+str(offenceOutput)))
	else:
		return(output=("Only moderators can use this command."))