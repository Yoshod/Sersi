import nextcord
from nextcord.ext import commands

from utils.base import SersiEmbed, get_discord_timestamp
from utils.config import Configuration


def decypher_permission(permission: nextcord.Permissions) -> list[str]:
    human_readable_permissions: list[str] = []
    if permission.administrator:
        human_readable_permissions.append("administrator")
    if permission.attach_files:
        human_readable_permissions.append("attach_files")
    if permission.ban_members:
        human_readable_permissions.append("ban_members")
    if permission.change_nickname:
        human_readable_permissions.append("change_nickname")
    if permission.connect:
        human_readable_permissions.append("connect")
    if permission.create_instant_invite:
        human_readable_permissions.append("create_instant_invite")
    if permission.create_private_threads:
        human_readable_permissions.append("create_private_threads")
    if permission.create_public_threads:
        human_readable_permissions.append("create_public_threads")
    if permission.deafen_members:
        human_readable_permissions.append("deafen_members")
    if permission.embed_links:
        human_readable_permissions.append("embed_links")
    if permission.external_emojis:
        human_readable_permissions.append("external_emojis")
    if permission.external_stickers:
        human_readable_permissions.append("external_stickers")
    if permission.kick_members:
        human_readable_permissions.append("kick_members")
    if permission.manage_channels:
        human_readable_permissions.append("manage_channels")
    if permission.manage_emojis:
        human_readable_permissions.append("manage_emojis")
    if permission.manage_emojis_and_stickers:
        human_readable_permissions.append("manage_emojis_and_stickers")
    if permission.manage_events:
        human_readable_permissions.append("manage_events")
    if permission.manage_guild:
        human_readable_permissions.append("manage_guild")
    if permission.manage_messages:
        human_readable_permissions.append("manage_messages")
    if permission.manage_nicknames:
        human_readable_permissions.append("manage_nicknames")
    if permission.manage_permissions:
        human_readable_permissions.append("manage_permissions")
    if permission.manage_roles:
        human_readable_permissions.append("manage_roles")
    if permission.manage_threads:
        human_readable_permissions.append("manage_threads")
    if permission.manage_webhooks:
        human_readable_permissions.append("manage_webhooks")
    if permission.mention_everyone:
        human_readable_permissions.append("mention_everyone")
    if permission.moderate_members:
        human_readable_permissions.append("moderate_members")
    if permission.move_members:
        human_readable_permissions.append("move_members")
    if permission.mute_members:
        human_readable_permissions.append("mute_members")
    if permission.priority_speaker:
        human_readable_permissions.append("priority_speaker")
    if permission.read_message_history:
        human_readable_permissions.append("read_message_history")
    if permission.read_messages:
        human_readable_permissions.append("read_messages")
    if permission.request_to_speak:
        human_readable_permissions.append("request_to_speak")
    if permission.send_messages:
        human_readable_permissions.append("send_messages")
    if permission.send_messages_in_threads:
        human_readable_permissions.append("send_messages_in_threads")
    if permission.send_tts_messages:
        human_readable_permissions.append("send_tts_messages")
    if permission.speak:
        human_readable_permissions.append("speak")
    if permission.start_embedded_activities:
        human_readable_permissions.append("start_embedded_activities")
    if permission.stream:
        human_readable_permissions.append("stream")
    if permission.use_external_emojis:
        human_readable_permissions.append("use_external_emojis")
    if permission.use_external_stickers:
        human_readable_permissions.append("use_external_stickers")
    if permission.use_slash_commands:
        human_readable_permissions.append("use_slash_commands")
    if permission.use_voice_activation:
        human_readable_permissions.append("use_voice_activation")
    if permission.view_audit_log:
        human_readable_permissions.append("view_audit_log")
    if permission.view_channel:
        human_readable_permissions.append("view_channel")
    if permission.view_guild_insights:
        human_readable_permissions.append("view_guild_insights")
    return human_readable_permissions


class Channels(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: nextcord.abc.GuildChannel):

        entries = await channel.guild.audit_logs(
            action=nextcord.AuditLogAction.channel_delete, limit=1
        ).flatten()
        log: nextcord.AuditLogEntry = entries[0]

        logging_embed: nextcord.Embed = SersiEmbed(
            description=f"{type(channel).__name__} deleted",
            fields={
                "Name": channel.name,
                "Created At": get_discord_timestamp(channel.created_at),
                "Position": channel.position,
            },
            footer="Sersi Channel Logs",
        ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        for overwrite in channel.overwrites:
            type_of_overwrite: str = type(overwrite).__name__

            permissions: list[str] = []
            for permission, value in channel.overwrites[overwrite]:
                if value is None:
                    continue
                permissions.append(permission)

            logging_embed.add_field(
                name=overwrite,
                value=f"Type: {type_of_overwrite}\nPermissions: {', '.join(permissions)}",
                inline=False,
            )

        await channel.guild.get_channel(self.config.channels.channel_logs).send(
            embed=logging_embed
        )

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: nextcord.abc.GuildChannel):
        entries = await channel.guild.audit_logs(
            action=nextcord.AuditLogAction.channel_create, limit=1
        ).flatten()
        log: nextcord.AuditLogEntry = entries[0]

        logging_embed: nextcord.Embed = SersiEmbed(
            description=f"{type(channel).__name__} Created",
            fields={
                "Name": f"{channel.mention} {channel.name} (`{channel.id}`)",
                "Created At": get_discord_timestamp(channel.created_at),
                "Position": channel.position,
            },
            footer="Sersi Channel Logs",
        ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        for overwrite in channel.overwrites:
            type_of_overwrite: str = type(overwrite).__name__

            permissions: list[str] = []
            for permission, value in channel.overwrites[overwrite]:
                if value is None:
                    continue
                permissions.append(permission)

            logging_embed.add_field(
                name=overwrite,
                value=f"Type: {type_of_overwrite}\nPermissions: {', '.join(permissions)}",
                inline=False,
            )

        await channel.guild.get_channel(self.config.channels.channel_logs).send(
            embed=logging_embed
        )

    @commands.Cog.listener()
    async def on_guild_channel_update(
        self,
        before: nextcord.abc.GuildChannel,
        after: nextcord.abc.GuildChannel,
    ):
        async def get_audit_log(guild: nextcord.Guild) -> nextcord.AuditLogEntry:
            # getting the 10 most recent entries of the audit log
            entries: list[nextcord.AuditLogEntry] = await guild.audit_logs(
                limit=10
            ).flatten()

            for entry in entries:
                if entry.action in [
                    nextcord.AuditLogAction.channel_update,
                    nextcord.AuditLogAction.overwrite_create,
                    nextcord.AuditLogAction.overwrite_update,
                    nextcord.AuditLogAction.overwrite_delete,
                ]:
                    return entry

        if after.position != before.position:
            await after.guild.get_channel(self.config.channels.channel_logs).send(
                embed=SersiEmbed(
                    description=f"{type(after).__name__} {after.mention} was moved",
                    fields={
                        "Created At": get_discord_timestamp(after.created_at),
                        "Before": f"Position {before.position}",
                        "After": f"Position {after.position}",
                    },
                    footer="Sersi Channel Logs",
                )
            )

        log: nextcord.AuditLogEntry = await get_audit_log(after.guild)

        match log.action:
            case nextcord.AuditLogAction.channel_update:
                after_values: str = ""
                for attribute, value in log.after:
                    after_values = f"{after_values}{attribute}: {value}\n"

                before_values: str = ""
                for attribute, value in log.before:
                    before_values = f"{before_values}{attribute}: {value}\n"

                await after.guild.get_channel(self.config.channels.channel_logs).send(
                    embed=SersiEmbed(
                        description=f"{type(log.target).__name__} {log.target.mention} was updated",
                        fields={
                            "Created At": get_discord_timestamp(log.target.created_at),
                            "Before": before_values,
                            "After": after_values,
                        },
                        footer="Sersi Channel Logs",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )

            case nextcord.AuditLogAction.overwrite_create:

                await after.guild.get_channel(self.config.channels.channel_logs).send(
                    embed=SersiEmbed(
                        description=f"Overwrite for {type(log.target).__name__} {log.target.mention} created",
                        fields={
                            "Created At": get_discord_timestamp(log.target.created_at),
                            "Overwrite Created For": f"[{type(log.extra).__name__}] {log.extra.mention}",
                        },
                        footer="Sersi Channel Logs",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )

            case nextcord.AuditLogAction.overwrite_update:
                before_values: str = ""
                before_perms: nextcord.PermissionOverwrite = before.overwrites[
                    log.extra
                ]
                after_values: str = ""
                after_perms: nextcord.PermissionOverwrite = after.overwrites[log.extra]

                for before_permission, before_value in before_perms:
                    for after_permission, after_value in after_perms:
                        if (
                            before_permission == after_permission
                            and before_value != after_value
                        ):
                            match before_value:
                                case True:
                                    before_values += f"{self.config.emotes.success} `{before_permission}`\n"
                                case False:
                                    before_values += f"{self.config.emotes.fail} `{before_permission}`\n"
                                case None:
                                    before_values += f"{self.config.emotes.inherit} `{before_permission}`\n"

                            match after_value:
                                case True:
                                    after_values += f"{self.config.emotes.success} `{after_permission}`\n"
                                case False:
                                    after_values += f"{self.config.emotes.fail} `{after_permission}`\n"
                                case None:
                                    after_values += f"{self.config.emotes.inherit} `{after_permission}`\n"

                if not before_values or not after_values:
                    return

                await after.guild.get_channel(self.config.channels.channel_logs).send(
                    embed=SersiEmbed(
                        description=f"Overwrite for {type(log.target).__name__} {log.target.mention} updated",
                        fields={
                            "Created At": get_discord_timestamp(log.target.created_at),
                            "Overwrite Updated For": f"[{type(log.extra).__name__}] {log.extra.mention}",
                            "Before": before_values,
                            "After": after_values,
                        },
                        footer="Sersi Channel Logs",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )

            case nextcord.AuditLogAction.overwrite_delete:
                before_values: str = ""
                for attribute, value in log.before:
                    if attribute == "deny":
                        permission: list[str] = decypher_permission(value)
                        for permission in permission:
                            before_values = f"{before_values}{self.config.emotes.fail} `{permission}`\n"

                    if attribute == "allow":
                        permission: list[str] = decypher_permission(value)
                        for permission in permission:
                            before_values = f"{before_values}{self.config.emotes.success} `{permission}`\n"

                await after.guild.get_channel(self.config.channels.channel_logs).send(
                    embed=SersiEmbed(
                        description=f"Overwrite for {type(log.target).__name__} {log.target.mention} deleted",
                        fields={
                            "Created At": get_discord_timestamp(log.target.created_at),
                            "Overwrite Deleted For": f"[{type(log.extra).__name__}] {log.extra.mention}",
                            "Was": before_values,
                        },
                        footer="Sersi Channel Logs",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )


def setup(bot, **kwargs):
    bot.add_cog(Channels(bot, kwargs["config"]))
