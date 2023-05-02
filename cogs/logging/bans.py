import nextcord
from nextcord.ext import commands

from utils.base import SersiEmbed
from utils.config import Configuration


class BanUnban(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_member_ban(self, guild: nextcord.Guild, user: nextcord.User):
        log: nextcord.AuditLogEntry = (
            await guild.audit_logs(
                limit=1, action=nextcord.AuditLogAction.ban
            ).flatten()
        )[0]

        await guild.get_channel(self.config.channels.ban_unban).send(
            embed=SersiEmbed(
                description=f"{user} was banned",
                fields={
                    "User Information": f"{user} `{user.id}` {user.mention}",
                    "Reason": {log.reason},
                },
                footer="Sersi Ban/Unban Logging",
                colour=nextcord.Colour.brand_red(),
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )

    @commands.Cog.listener()
    async def on_member_unban(self, guild: nextcord.Guild, user: nextcord.User):
        """kedyfab#1979 was unbanned
        User Information
        kedyfab#1979 (452101373409099777) @kedyfab
        Reason
        Appealed, accepted by JUNIPER#3250"""
        log: nextcord.AuditLogEntry = (
            await guild.audit_logs(
                limit=1, action=nextcord.AuditLogAction.unban
            ).flatten()
        )[0]

        await guild.get_channel(self.config.channels.ban_unban).send(
            embed=SersiEmbed(
                description=f"{user} was unbanned",
                fields={
                    "User Information": f"{user} `{user.id}` {user.mention}",
                    "Reason": {log.reason},
                },
                footer="Sersi Ban/Unban Logging",
                colour=nextcord.Colour.brand_green(),
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )


def setup(bot, **kwargs):
    bot.add_cog(BanUnban(bot, kwargs["config"]))
