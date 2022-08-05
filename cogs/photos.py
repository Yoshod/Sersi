import nextcord
from nextcord.ext import commands

from nextcord.ext import commands
from configutils import get_config_int, get_config_bool


class Photos(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.emotes = ["👍", "❤", "😲"]

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = message.guild.get_channel(get_config_int('CHANNELS', 'photography'))

        # ignore if message is not in photography channel
        if message.channel.id != channel.id:
            return

        elif message.author == self.bot.user:  # ignores message if message is by bot
            return

        # if there are no attachments whatsoever
        elif not message.attachments:
            await message.delete()
            await message.channel.send(f"{message.author.mention}, please do not send text messages.", delete_after=10.0)

        # if any attachment is not of type image
        elif any('image' not in attachment.content_type for attachment in message.attachments):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, please only send images in this chat.", delete_after=10.0)

        else:
            # add reaction emotes
            for emote in self.emotes:
                await message.add_reaction(emote)

            # create thread if wanted
            if get_config_bool('PHOTOS', 'create_thread'):
                timestr = message.created_at.strftime("%H.%M")
                await message.create_thread(name=f"{message.author.display_name} {timestr}")


def setup(bot):
    bot.add_cog(Photos(bot))
