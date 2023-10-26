import nextcord
from nextcord.ext import commands

import re

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class Invites(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.invite_regex = re.compile(r"discord.gg/[A-Za-z0-9]+")

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if not self.invite_regex.search(message.content):
            return

        invite: nextcord.Invite = await self.bot.fetch_invite(
            self.invite_regex.search(message.content).group(0)
        )

        await message.guild.get_channel(self.config.channels.alert).send(
            embed=SersiEmbed(
                title="Discord Invite Detected",
                fields={
                    "Guild:": f"Name: {invite.guild.name}\nDescription: {invite.guild.description}\nID: {invite.guild.id}",
                    "Inviter": f"{invite.inviter.mention} ({invite.inviter.id})"
                    if invite.inviter
                    else "Unknown",
                    "Offender": f"{message.author.mention} ({message.author.id})",
                    "Message Link": message.jump_url,
                },
            ).set_thumbnail(invite.guild.icon)
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Invites(bot, kwargs["config"]))
