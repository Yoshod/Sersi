#Sersi Offences Commands
#Written by Hekkland

import discord

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