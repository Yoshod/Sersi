import nextcord
import pytz
from datetime import datetime
from nextcord.ext import commands
from configutils import Configuration


class Antitamper(commands.Cog):

    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        # fetch the last deleted message
        async for entry in message.guild.audit_logs(action=nextcord.AuditLogAction.message_delete, limit=1):
            log = entry

        # ignore if message was not from logging section
        if message.channel.category.id != self.config.channels.logging_category:
            return

        if (datetime.now(pytz.UTC) - log.created_at).seconds > 1:
            return

        warning_embed = nextcord.Embed(
            colour=nextcord.Color.from_rgb(237, 91, 6),
            title="Logs have been tampered with.",
            description="A message in a logging channel has been tampered with. An inquiry into the incident seems appropiate."
        )
        warning_embed.add_field(name="Perpetrator:", value=f"{log.user} ({log.user.id})", inline=False)
        warning_embed.add_field(name="Channel:", value=log.extra.channel.mention, inline=False)

        channel = message.guild.get_channel(self.config.channels.tamper_logs)
        mega_admin = message.guild.get_role(self.config.permission_roles.dark_moderator)
        await channel.send(mega_admin.mention, embed=warning_embed)


def setup(bot, **kwargs):
    bot.add_cog(Antitamper(bot, kwargs["config"]))