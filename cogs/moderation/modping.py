import nextcord
from nextcord.ext import commands

from utils.alerts import create_alert_log, AlertType, AlertView
from utils.sersi_embed import SersiEmbed
from utils.base import (
    modmention_check,
    ignored_message,
)
from utils.config import Configuration


class ModPing(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
            return

        if modmention_check(self.config, message.content):
            # Reply to user
            response_embed: nextcord.Embed = SersiEmbed(
                title="Moderator Ping Acknowledgment",
                description=f"{message.author.mention} moderators have been notified of your ping and will investigate when able to do so.",
                footer="Sersi Moderator Ping Detection",
            )
            await message.channel.send(embed=response_embed)
            await message.channel.send(
                message.guild.get_role(
                    self.config.permission_roles.trial_moderator
                ).mention,
                delete_after=1,
            )

            # notification for mods
            channel = self.bot.get_channel(self.config.channels.alert)
            alert_embed: nextcord.Embed = SersiEmbed(
                title="Moderator Ping",
                description="A moderation role has been pinged, please investigate the ping and take action as appropriate.",
                fields={
                    "Channel:": message.channel.mention,
                    "User:": message.author.mention,
                    "Context:": message.content,
                    "URL:": message.jump_url,
                },
                footer="Sersi Moderator Ping Detection",
            )

            alert = await channel.send(embed=alert_embed, view=AlertView(AlertType.Ping, message.author))
            create_alert_log(message=alert, alert_type=AlertType.Ping)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(ModPing(bot, kwargs["config"]))
