import nextcord


from nextcord.ext import commands
from utils.config import Configuration
from utils.sersi_embed import SersiEmbed


class MemberRoles(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: nextcord.Role):
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
        log: nextcord.AuditLogEntry = (
            await after.guild.audit_logs(
                action=nextcord.AuditLogAction.role_update, limit=1
            ).flatten()
        )[0]

        logging_embed: nextcord.Embed = SersiEmbed(
            description=f"Role {after.mention} {after.name} was updated",
            colour=after.colour
            if int(after.colour) != 0
            else nextcord.Color.from_rgb(237, 91, 6),
            footer="Sersi Role Logging",
        )

        if before.permissions != after.permissions:
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
                                before_permissions += f"{self.config.emotes.success} `{before_permission}`\n"
                            case False:
                                before_permissions += (
                                    f"{self.config.emotes.fail} `{before_permission}`\n"
                                )

                        match after_value:
                            case True:
                                after_permissions += f"{self.config.emotes.success} `{after_permission}`\n"
                            case False:
                                after_permissions += (
                                    f"{self.config.emotes.fail} `{after_permission}`\n"
                                )

            logging_embed.add_field(
                name="Permissions Changed",
                value=f"Before:\n{before_permissions}\nAfter:\n{after_permissions}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.colour != after.colour:
            logging_embed.add_field(
                name="Colour",
                value=f"Before:\n{before.colour}\nAfter:\n{after.colour}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.mentionable != after.mentionable:
            logging_embed.add_field(
                name="Mentionable",
                value=f"Before:\n{before.mentionable}\nAfter:\n{after.mentionable}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.hoist != after.hoist:
            logging_embed.add_field(
                name="Hoist",
                value=f"Before:\n{before.hoist}\nAfter:\n{after.hoist}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.name != after.name:
            logging_embed.add_field(
                name="Name",
                value=f"Before:\n{before.name}\nAfter:\n{after.name}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if logging_embed.fields:
            await after.guild.get_channel(self.config.channels.role_logs).send(
                embed=logging_embed
            )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(MemberRoles(bot, kwargs["config"]))
