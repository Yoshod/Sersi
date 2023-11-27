import nextcord
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class BanUnban(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
    
    @commands.Cog.listener()
    async def on_guild_audit_log_entry_create(self, entry: nextcord.AuditLogEntry):
        if entry.action == nextcord.AuditLogAction.ban:
            target: nextcord.User = await self.bot.fetch_user(entry._target_id)
            await entry.guild.get_channel(self.config.channels.ban_unban).send(
                embed=SersiEmbed(
                    description=f"{target} was banned",
                    fields={
                        "User Information": f"{target} `{target.id}` {target.mention}",
                        "Reason": entry.reason,
                    },
                    footer="Sersi Ban/Unban Logging",
                    thumbnail_url=target.display_avatar.url,
                    colour=nextcord.Colour.brand_red(),
                ).set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
            )
        elif entry.action == nextcord.AuditLogAction.unban:
            target: nextcord.User = await self.bot.fetch_user(entry._target_id)
            await entry.guild.get_channel(self.config.channels.ban_unban).send(
                embed=SersiEmbed(
                    description=f"{target} was unbanned",
                    fields={
                        "User Information": f"{target} `{target.id}` {target.mention}",
                        "Reason": entry.reason,
                    },
                    footer="Sersi Ban/Unban Logging",
                    thumbnail_url=target.display_avatar.url,
                    colour=nextcord.Colour.brand_green(),
                ).set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
            )
        elif entry.action == nextcord.AuditLogAction.kick:
            target: nextcord.User = await self.bot.fetch_user(entry._target_id)
            await entry.guild.get_channel(self.config.channels.ban_unban).send(
                embed=SersiEmbed(
                    description=f"{target} was kicked",
                    fields={
                        "User Information": f"{target} `{target.id}` {target.mention}",
                        "Reason": entry.reason,
                    },
                    thumbnail_url=target.display_avatar.url,
                    footer="Sersi Ban/Unban Logging",
                ).set_author(name=entry.user, icon_url=entry.user.display_avatar.url)
            )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(BanUnban(bot, kwargs["config"]))
