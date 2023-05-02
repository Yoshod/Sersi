import nextcord
from nextcord.ext import commands

from utils.base import SersiEmbed, get_discord_timestamp
from utils.config import Configuration


class UserLogging(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_user_update(self, before: nextcord.User, after: nextcord.User):
        """Called when a User updates their profile.
        This is called when one or more of the following things change:
            avatar
            username
            discriminator"""

        if before.avatar != after.avatar:
            await self.bot.get_channel(self.config.channels.user_chanes).send(
                embed=SersiEmbed(
                    description=f"{after.mention} ({after.id}) has changed their avatar",
                    fields={"Before": before.avatar.url, "After": after.avatar.url},
                    footer="Sersi Member Logging",
                )
                .set_thumbnail(url=before.avatar.url)
                .set_image(url=after.avatar.url)
            )
        if before.name != after.name:
            await self.bot.get_channel(self.config.channels.user_chanes).send(
                embed=SersiEmbed(
                    description=f"{after.mention} ({after.id}) has changed their username",
                    fields={"Before": before.name, "After": after.name},
                    footer="Sersi Member Logging",
                )
            )
        if before.discriminator != after.discriminator:
            await self.bot.get_channel(self.config.channels.user_chanes).send(
                embed=SersiEmbed(
                    description=f"{after.mention} ({after.id}) has changed their discriminator",
                    fields={"Before": str(before), "After": str(after)},
                    footer="Sersi Member Logging",
                )
            )

    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        """Called when a Member updates their profile.
        This is called when one or more of the following things change:
            nickname
            roles
            pending"""
        if before.nick != after.nick:

            log: nextcord.AuditLogEntry = (
                await after.guild.audit_logs(
                    limit=1, action=nextcord.AuditLogAction.member_update
                ).flatten()
            )[0]

            if log.target.id == after.id:
                await after.guild.get_channel(self.config.channels.user_chanes).send(
                    embed=SersiEmbed(
                        description=f"{after.mention}'s nickname was changed",
                        fields={
                            "Before": before.nick,
                            "After": after.nick,
                            "Changed By": f"{log.user.mention} ({log.user.id})",
                        },
                        footer="Sersi Member Logging",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )
            else:
                await after.guild.get_channel(self.config.channels.user_chanes).send(
                    embed=SersiEmbed(
                        description=f"{after.mention} has updated their nickname",
                        fields={"Before": before.nick, "After": after.nick},
                        footer="Sersi Member Logging",
                    )
                )
        if before.roles != after.roles:
            log: nextcord.AuditLogEntry = (
                await after.guild.audit_logs(
                    action=nextcord.AuditLogAction.member_role_update, limit=1
                ).flatten()
            )[0]

            if log.before.roles:
                # audit log shows roles as previously had, so this is a role removal entry
                logging = SersiEmbed(
                    description="A role has been removed",
                    footer="Sersi Role Logging",
                    fields={"User affected:": before.mention},
                ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

                for role in log.before.roles:
                    logging.add_field(
                        name="Role removed:", value=role.mention, inline=False
                    )
                    logging.add_field(
                        name="IDs:",
                        value=f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```",
                        inline=False,
                    )

                await after.guild.get_channel(self.config.channels.user_chanes).send(
                    embed=logging
                )

            elif log.after.roles:
                # audit log shows roles as now have, so this is an added role entry
                logging = SersiEmbed(
                    description="A role has been added",
                    footer="Sersi Role Logging",
                    fields={"User affected:": before.mention},
                ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

                for role in log.after.roles:
                    logging.add_field(
                        name="Role added:", value=role.mention, inline=False
                    )
                    logging.add_field(
                        name="IDs:",
                        value=f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```",
                        inline=False,
                    )

                await after.guild.get_channel(self.config.channels.user_chanes).send(
                    embed=logging
                )

        if (
            before.communication_disabled_until != after.communication_disabled_until
            and after.communication_disabled_until
        ):
            log: nextcord.AuditLogEntry = (
                await after.guild.audit_logs(
                    action=nextcord.AuditLogAction.member_role_update, limit=1
                ).flatten()
            )[0]

            await after.guild.get_channel(self.config.channels.user_chanes).send(
                embed=SersiEmbed(
                    description=f"{after.mention} was muted",
                    fields={
                        "Communication Disabled Until": f"{get_discord_timestamp(after.communication_disabled_until)} "
                        f"({get_discord_timestamp(after.communication_disabled_until, relative=True)})",
                        "Changed By": f"{log.user.mention} ({log.user.id})",
                        "Reason": log.reason,
                    },
                    footer="Sersi Member Logging",
                ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
            )

        if before.display_avatar != after.display_avatar:
            await self.bot.get_channel(self.config.channels.user_chanes).send(
                embed=SersiEmbed(
                    description=f"{after.mention} ({after.id}) has changed their display avatar",
                    fields={
                        "Before": before.display_avatar.url,
                        "After": after.display_avatar.url,
                    },
                    footer="Sersi Member Logging",
                )
                .set_thumbnail(url=before.display_avatar.url)
                .set_image(url=after.display_avatar.url)
            )

    @commands.Cog.listener()
    async def on_presence_update(self, before: nextcord.Member, after: nextcord.Member):
        """Called when a Member updates their presence.
        This is called when one or more of the following things change:
            status
            activity"""
        ...


def setup(bot, **kwargs):
    bot.add_cog(UserLogging(bot, kwargs["config"]))
