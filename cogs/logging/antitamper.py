import nextcord
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class Antitamper(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        if message.guild is None:
            return

        # ignore if message was not from logging section
        if message.channel.category.id != self.config.channels.logging_category:
            return
    
        # fetch the last deleted message
        log: nextcord.AuditLogEntry = (
            await message.guild.audit_logs(
                action=nextcord.AuditLogAction.message_delete, limit=1
            ).flatten()
        )[0]

        channel = message.guild.get_channel(self.config.channels.tamper_logs)
        await channel.send(
            message.guild.get_role(self.config.permission_roles.dark_moderator).mention,
            embed=SersiEmbed(
                title="Logs have been tampered with.",
                description="A message in a logging channel has been deleted. "
                "Please investigate at nearest convenience.",
                footer="Antitamper Alert",
                fields={
                    "Perpetrator:": f"{log.user.mention} ({log.user.id})",
                    "Target:": f"{log.target.mention} ({log.target.id})",
                    "Channel": log.extra.channel.mention,
                    "Message Content": message.content,
                },
            ),
        )
        if message.embeds:
            await channel.send(
                content="deleted embeds:", embeds=[embed for embed in message.embeds]
            )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Antitamper(bot, kwargs["config"]))
