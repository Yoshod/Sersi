import nextcord
from nextcord.ext import commands
import re
import unidecode
#from nextcord.ext.commands.errors import MemberNotFound

class Caps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        msg_string = message.content
        if len(msg_string):
            #remove nums and non-alpanumeric
            msg_string = unidecode.unidecode(msg_string)
            new_msg_string = re.sub(r'[^a-zA-Z]', '', msg_string)
            print("cleaned message:", new_msg_string)

            uppercase = sum(1 for char in new_msg_string if char.isupper())

            percentage = uppercase/len(new_msg_string)
            print("percentage:", percentage)
            if percentage > 0.7:
                print("Caps detected; opinion rejected")
                #await replace(self, message, message.author, msg_string)
                await message.delete(delay=None)
        
                webhook = await message.channel.create_webhook(name=message.author.name)
                await webhook.send(str(msg_string.lower()), username=message.author.display_name, avatar_url=message.author.display_avatar.url)
                await webhook.delete()

def setup(bot):
    bot.add_cog(Caps(bot))