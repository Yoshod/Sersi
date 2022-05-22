#Sersi Offences Commands
#Written by Hekkland

import nextcord

def isMod(userRoles):
	modRolePresent=False
	for role in userRoles:
		if "856424878437040168" == str(role.id):	#asc role
			modRolePresent=True
		elif "883255791610638366" == str(role.id):	#asc role
			modRolePresent=True
		elif "977394150494326855" == str(role.id):	#proving ground role "certified bot tester"
			modRolePresent=True
	#print(modRolePresent)
	return (modRolePresent)

def getAlertChannel(guild_id):
	if guild_id == 856262303795380224:		#asc
		return 897874682198511648			#information-centre
	elif guild_id == 977377117895536640:	#the proving grounds
		return 977377171054166037			#replies

def getLoggingChannel(guild_id):
	if guild_id == 856262303795380224:		#asc
		return 977609240107700244			#sersi-logs
	elif guild_id == 977377117895536640:	#the proving grounds
		return 977925156330672198			#logging

