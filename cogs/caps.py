import nextcord
from nextcord.ext import commands
import re
import unidecode
from baseutils import getLoggingChannel
# from nextcord.ext.commands.errors import MemberNotFound


class Caps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.MIN_CHARS_FOR_DETECTION = 3

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        msg_string = message.content

        if len(msg_string) > self.MIN_CHARS_FOR_DETECTION:
            # remove nums and non-alpanumeric
            msg_string = unidecode.unidecode(msg_string)

            new_msg_string = re.sub(r'[^a-zA-Z]', '', msg_string)
            uppercase = sum(1 for char in new_msg_string if char.isupper())

            if len(new_msg_string) != 0:
                percentage = uppercase / len(new_msg_string)

                if percentage > 0.7:
                    print("Caps detected; opinion rejected")
                    # await replace(self, message, message.author, msg_string)
                    await message.delete(delay=None)

                    channel_webhooks = await message.channel.webhooks()
                    for webhook in channel_webhooks:
                        if webhook.name == "caps webhook by sersi":
                            await webhook.send(str(msg_string.lower()), username=message.author.display_name, avatar_url=message.author.display_avatar.url)
                            return

                    webhook = await message.channel.create_webhook(name="caps webhook by sersi")
                    await webhook.send(str(msg_string.lower()), username=message.author.display_name, avatar_url=message.author.display_avatar.url)

                    channel = self.bot.get_channel(getLoggingChannel(message.guild.id))
                    logging_embed = nextcord.Embed(
                        title=f"Caps Lock Message replaced",
                        description="",
                        color=nextcord.Color.from_rgb(237, 91, 6)
                    )
                    logging_embed.add_field(name="User:", value=message.author.mention, inline=False)
                    logging_embed.add_field(name="Original Message:", value=msg_string, inline=False)
                    logging_embed.add_field(name="Replacement Message:", value=str(msg_string.lower()), inline=False)
                    await channel.send(embed=logging_embed)


def setup(bot):
    bot.add_cog(Caps(bot))
