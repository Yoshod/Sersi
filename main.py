import discord
import os
import random
from discord import DMChannel
from keep_alive import keep_alive

client = discord.Client()

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
  
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  modCheckOutput=(checkForMods(message.content))
  if message.author == client.user:
    return

  if modCheckOutput == True:
    embedVar = discord.Embed(title="Moderator Ping Acknowledgment", description=(message.author.mention)+" moderators have been notified of your ping and will investigate when able to do so.", color=discord.Color.from_rgb(237,91,6))
    await message.channel.send(embed=embedVar)
    channel = client.get_channel(897874682198511648)
    embedVar = discord.Embed(title="Moderator Ping", description= "A moderation role has been pinged, please investigate the ping and take action as appropriate.\n\n__Channel:__\n"+str(message.channel.mention)+"\n\n__User:__\n"+str(message.author.mention)+"\n\n__Context:__\n"+str(message.content)+"\n\n__URL:__\n"+str(message.jump_url), color=discord.Color.from_rgb(237,91,6))
    await channel.send(embed=embedVar)
    #await channel.send("Moderators have been pinged in "+str(message.channel)+".\nPlease investigate if you are available to do so.")

keep_alive()
client.run(os.environ['rtoken'])
