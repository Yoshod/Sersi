import discord
import os
import random
from discord import DMChannel
from discord.ext import commands
from keep_alive import keep_alive

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

  return (modDetected)

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
async def offencecheck(ctx,offence):
  if isMod(ctx.author.roles):
    
    else:
      ctx.send ("Only moderators can use this command.")
  

@bot.event
async def on_message(message):
  modCheckOutput=(checkForMods(message.content))
  if message.author == bot.user:
    return

  if modCheckOutput == True:
    embedVar = discord.Embed(title="Moderator Ping Acknowledgment", description=(message.author.mention)+" moderators have been notified of your ping and will investigate when able to do so.", color=discord.Color.from_rgb(237,91,6))
    await message.channel.send(embed=embedVar)
    channel = bot.get_channel(897874682198511648)
    embedVar = discord.Embed(title="Moderator Ping", description= "A moderation role has been pinged, please investigate the ping and take action as appropriate.\n\n__Channel:__\n"+str(message.channel.mention)+"\n\n__User:__\n"+str(message.author.mention)+"\n\n__Context:__\n"+str(message.content)+"\n\n__URL:__\n"+str(message.jump_url), color=discord.Color.from_rgb(237,91,6))
    await channel.send(embed=embedVar)
    #await channel.send("Moderators have been pinged in "+str(message.channel)+".\nPlease investigate if you are available to do so.")

  """"if message.content.startswith ("mb!offences"):
    modRolePresent=(isMod(user.roles))
    if modRolePresent==True:
      channel.message.send("The test was successful!")
    else:
      channel.message.send("Only moderators can use this command.")"""

  await bot.process_commands(message)

    
keep_alive()
bot.run(os.environ['rtoken'])
