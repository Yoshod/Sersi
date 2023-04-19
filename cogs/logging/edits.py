import nextcord
from nextcord.ext import commands

from baseutils import SersiEmbed
from configutils import Configuration


class Edits(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        if before.guild is None:
            return
        elif before.content == "" or after.content == "":
            return

        edited_messages: nextcord.TextChannel = before.guild.get_channel(
            self.config.channels.edited_messages
        )
        logging_embed: nextcord.Embed = SersiEmbed(
            description="A message has been edited",
            fields={
                "Channel": f"{before.channel.mention} ({before.channel.id})",
                "Before": before.content,
                "After": after.content,
                "Link": after.jump_url,
                "IDs": f"```ini\nMessage = {after.id}```",
            },
            footer="Sersi Deletion Logging",
        )
        logging_embed.set_author(
            name=before.author, icon_url=before.author.display_avatar.url
        )

        await edited_messages.send(embed=logging_embed)


def setup(bot, **kwargs):
    bot.add_cog(Edits(bot, kwargs["config"]))
