import nextcord
from nextcord.ext import commands

from baseutils import SersiEmbed
from configutils import Configuration


class Antitamper(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        # fetch the last deleted message
        log: nextcord.AuditLogEntry = (
            await message.guild.audit_logs(
                action=nextcord.AuditLogAction.message_delete, limit=1
            ).flatten()
        )[0]

        # ignore if message was not from logging section
        if message.channel.category.id != self.config.channels.logging_category:
            return

        warning_embed = SersiEmbed(
            title="Logs have been tampered with.",
            description="A message in a logging channel has been deleted. Please investigate at "
            "nearest convenience.",
            footer="Antitamper Alert",
            fields={
                "Perpetrator:": f"{log.user.mention} ({log.user.id})",
                "Target:": f"{log.target.mention} ({log.target.id})",
                "Count": log.extra.count,
                "Channel": log.extra.channel.mention,
            },
        )

        channel = message.guild.get_channel(self.config.channels.tamper_logs)
        mega_admin = message.guild.get_role(self.config.permission_roles.dark_moderator)
        await channel.send(mega_admin.mention, embed=warning_embed)
        if message.embeds:
            await channel.send(
                content="deleted embeds:", embeds=[embed for embed in message.embeds]
            )


def setup(bot, **kwargs):
    bot.add_cog(Antitamper(bot, kwargs["config"]))
