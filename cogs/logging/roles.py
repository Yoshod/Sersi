import nextcord
from nextcord.ext import commands
from configutils import Configuration
from baseutils import SersiEmbed


class MemberRoles(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: nextcord.Role):
        """A new role was created.
        When this is the action, the type of target is the Role or a Object with the ID.
        Possible attributes for AuditLogDiff:
            colour
            mentionable
            hoist
            name
            permissions"""
        log: nextcord.AuditLogEntry = (
            await role.guild.audit_logs(
                action=nextcord.AuditLogAction.role_create, limit=1
            ).flatten()
        )[0]

        role_permissions: str = ""
        for permission, value in role.permissions:
            if value:
                role_permissions += f"{self.config.emotes.success} `{permission}`\n"

        await role.guild.get_channel(self.config.channels.role_logs).send(
            embed=SersiEmbed(
                description="A role was created",
                fields={
                    "Name": f"{role.mention} {role.name}",
                    "Colour": f"`{role.colour}`",
                    "Mentionable": role.mentionable,
                    "Hoist": role.hoist,
                    "Permissions": role_permissions,
                    "IDs": f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```",
                },
                colour=role.colour,
                footer="Sersi Role Logging",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: nextcord.Role):
        log: nextcord.AuditLogEntry = (
            await role.guild.audit_logs(
                action=nextcord.AuditLogAction.role_delete, limit=1
            ).flatten()
        )[0]

        role_permissions: str = ""
        for permission, value in role.permissions:
            if value:
                role_permissions += f"{self.config.emotes.success} `{permission}`\n"

        await role.guild.get_channel(self.config.channels.role_logs).send(
            embed=SersiEmbed(
                description="A role was deleted",
                fields={
                    "Name": f"{role.name}",
                    "Colour": f"`{role.colour}`",
                    "Mentionable": role.mentionable,
                    "Hoist": role.hoist,
                    "Permissions": role_permissions,
                    "IDs": f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```",
                },
                colour=role.colour,
                footer="Sersi Role Logging",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: nextcord.Role, after: nextcord.Role):
        """
        A role was updated (Over 18's Verified)
        Name
        Now: Over 18's Verified
        Was: Adult Only Verified
        ---
        A role was updated. This triggers in the following situations:
        The name has changed
        The permissions have changed
        The colour has changed
        Its hoist/mentionable state has changed

        When this is the action, the type of target is the Role or a Object with the ID.

        Possible attributes for AuditLogDiff:
            colour
            mentionable
            hoist
            name
            permissions"""
        log: nextcord.AuditLogEntry = (
            await after.guild.audit_logs(
                action=nextcord.AuditLogAction.role_update, limit=1
            ).flatten()
        )[0]

        if not after == log.target:  # it likes to trigger this even willy nilly
            return

        before_permissions: str = ""
        after_permissions: str = ""
        for before_permission, before_value in before.permissions:
            for after_permission, after_value in after.permissions:
                if (
                    before_permission == after_permission
                    and before_value != after_value
                ):
                    match before_value:
                        case True:
                            before_permissions += (
                                f"{self.config.emotes.success} `{before_permission}`\n"
                            )
                        case False:
                            before_permissions += (
                                f"{self.config.emotes.fail} `{before_permission}`\n"
                            )
                        case None:
                            before_permissions += (
                                f"{self.config.emotes.inherit} `{before_permission}`\n"
                            )

                    match after_value:
                        case True:
                            after_permissions += (
                                f"{self.config.emotes.success} `{after_permission}`\n"
                            )
                        case False:
                            after_permissions += (
                                f"{self.config.emotes.fail} `{after_permission}`\n"
                            )
                        case None:
                            after_permissions += (
                                f"{self.config.emotes.inherit} `{after_permission}`\n"
                            )

        logging_embed: nextcord.Embed = SersiEmbed(
            description=f"Role {after.mention} {after.name} was updated",
            colour=after.colour,
            footer="Sersi Role Logging",
        ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.permissions != after.permissions:
            logging_embed.add_field(
                name="Permissions Changed",
                value=f"**Before:**\n{before_permissions}\n**After:**\n{after_permissions}",
                inline=False,
            )
        if before.colour != after.colour:
            logging_embed.add_field(
                name="Colour",
                value=f"**Before:**\n{before.colour}\n**After:**\n{after.colour}",
                inline=False,
            )
        if before.mentionable != after.mentionable:
            logging_embed.add_field(
                name="Mentionable",
                value=f"**Before:**\n{before.mentionable}\n**After:**\n{after.mentionable}",
                inline=False,
            )
        if before.hoist != after.hoist:
            logging_embed.add_field(
                name="Hoist",
                value=f"**Before:**\n{before.hoist}\n**After:**\n{after.hoist}",
                inline=False,
            )
        if before.name != after.name:
            logging_embed.add_field(
                name="Name",
                value=f"**Before:**\n{before.name}\n**After:**\n{after.name}",
                inline=False,
            )

        await after.guild.get_channel(self.config.channels.role_logs).send(
            embed=logging_embed
        )


def setup(bot, **kwargs):
    bot.add_cog(MemberRoles(bot, kwargs["config"]))
