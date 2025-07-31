import nextcord
from nextcord.ext import commands, application_checks
from utils.database import (
    guild_db_manager,
    LoggingChannels,
)
from utils.language import lang_manager
from utils.modules import check_module_enabled
from utils.logging import create_log
from utils.base import encode_button_id, decode_button_id


class TamperLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.tamper_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="tamper_logs"),
        )


class GlobalLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.global_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="global_logs"),
        )


class PublicLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.public_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="public_logs"),
        )


class ModLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(guild.id, "logging.setup.buttons.mod_logs"),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="mod_logs"),
        )


class GuildLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(guild.id, "logging.setup.buttons.guild_logs"),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="guild_logs"),
        )


class ChannelLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.channel_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="channel_logs"),
        )


class RoleLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(guild.id, "logging.setup.buttons.role_logs"),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="role_logs"),
        )


class JoinLeaveLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.join_leave_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="join_leave_logs"),
        )


class VoiceLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(guild.id, "logging.setup.buttons.voice_logs"),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="voice_logs"),
        )


class UserLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(guild.id, "logging.setup.buttons.user_logs"),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="user_logs"),
        )


class DeletedMessageLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.deleted_message_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id(
                "logging_setup", category="deleted_message_logs"
            ),
        )


class DeletedImageLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.deleted_image_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="deleted_image_logs"),
        )


class EditedMessageLogsButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False, guild: nextcord.Guild = None):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.edited_message_logs"
            ),
            style=(
                nextcord.ButtonStyle.grey
                if not selected
                else nextcord.ButtonStyle.green
            ),
            custom_id=encode_button_id("logging_setup", category="edited_message_logs"),
        )


class ChannelSelector(nextcord.ui.ChannelSelect):
    def __init__(self, guild: nextcord.Guild):
        super().__init__(
            placeholder=lang_manager.get_string(
                guild.id, "logging.setup.select_channel"
            ),
            min_values=1,
            max_values=1,
            channel_types=[nextcord.ChannelType.text],
        )


class LoggingSetupView(nextcord.ui.View):
    def __init__(self, guild: nextcord.Guild):
        super().__init__(timeout=None)
        self.guild = guild

        self.add_item(TamperLogsButton(guild=guild))
        self.add_item(GlobalLogsButton(guild=guild))
        self.add_item(PublicLogsButton(guild=guild))
        self.add_item(ModLogsButton(guild=guild))
        self.add_item(GuildLogsButton(guild=guild))
        self.add_item(ChannelLogsButton(guild=guild))
        self.add_item(RoleLogsButton(guild=guild))
        self.add_item(JoinLeaveLogsButton(guild=guild))
        self.add_item(VoiceLogsButton(guild=guild))
        self.add_item(UserLogsButton(guild=guild))
        self.add_item(DeletedMessageLogsButton(guild=guild))
        self.add_item(DeletedImageLogsButton(guild=guild))
        self.add_item(EditedMessageLogsButton(guild=guild))

        self.add_item(ChannelSelector(guild))


class LoggingSetup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup_logging",
        description="Setup logging channels for the server",
        guild_ids=[977377117895536640, 1166770860787515422, 1383162647171567626],
    )
    async def setup_logging(self, interaction: nextcord.Interaction):
        pass

    @setup_logging.subcommand(
        name="express",
        description="Sersi will create logging channels for you.",
    )
    @application_checks.has_guild_permissions(administrator=True)
    async def express_setup(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not check_module_enabled(interaction.guild.id, "logging"):
            return await interaction.followup.send(
                lang_manager.get_string(
                    interaction.guild.id,
                    "module_disabled",
                    module_name="Logging",
                ),
                ephemeral=True,
            )

        try:
            logging_category = await interaction.guild.create_category(
                name="Logging",
                reason="Created by Sersi's logging setup command.",
            )
        except nextcord.Forbidden:
            return await interaction.followup.send(
                lang_manager.get_string(
                    interaction.guild.id,
                    "logging.setup.express.forbidden",
                ),
                ephemeral=True,
            )
        except nextcord.HTTPException:
            return await interaction.followup.send(
                lang_manager.get_string(
                    interaction.guild.id,
                    "logging.setup.express.http_exception",
                ),
                ephemeral=True,
            )

        try:
            global_log = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.global_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            public_log = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.public_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            tamper_log = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.tamper_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            mod_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.mod_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            guild_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.guild_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            channel_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.channel_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            role_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.role_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            join_leave_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.join_leave_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            voice_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.voice_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            user_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.user_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            deleted_message_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.deleted_message_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            deleted_image_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.deleted_image_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

            edited_message_logs = await interaction.guild.create_text_channel(
                name=lang_manager.get_string(
                    interaction.guild.id, "logging.setup.express.edited_message_logs"
                ),
                category=logging_category,
                reason="Created by Sersi's logging setup command.",
            )

        except nextcord.Forbidden:
            return await interaction.followup.send(
                lang_manager.get_string(
                    interaction.guild.id,
                    "logging.setup.express.forbidden",
                ),
                ephemeral=True,
            )
        except nextcord.HTTPException:
            return await interaction.followup.send(
                lang_manager.get_string(
                    interaction.guild.id,
                    "logging.setup.express.http_exception",
                ),
                ephemeral=True,
            )

        with guild_db_manager.get_session(interaction.guild.id) as session:
            session.add(
                LoggingChannels(
                    log_type="global",
                    channel_id=global_log.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="public",
                    channel_id=public_log.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="tamper",
                    channel_id=tamper_log.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="moderation",
                    channel_id=mod_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="guild",
                    channel_id=guild_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="channel",
                    channel_id=channel_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="role",
                    channel_id=role_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="join_leave",
                    channel_id=join_leave_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="voice",
                    channel_id=voice_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="user",
                    channel_id=user_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="deleted_message",
                    channel_id=deleted_message_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="deleted_image",
                    channel_id=deleted_image_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    log_type="edited_message",
                    channel_id=edited_message_logs.id,
                )
            )
            session.commit()

        await interaction.followup.send(
            lang_manager.get_string(
                interaction.guild.id,
                "logging.setup.express.success",
            ),
            ephemeral=True,
        )

        await create_log(
            interaction.guild,
            "logging_setup_complete",
            "global",
        )
        return

    @setup_logging.subcommand(
        name="custom",
        description="Setup logging channels with custom names.",
    )
    @application_checks.has_guild_permissions(administrator=True)
    async def custom_setup(self, interaction: nextcord.Interaction):
        await interaction.response.defer()

        if not check_module_enabled(interaction.guild.id, "logging"):
            return await interaction.followup.send(
                lang_manager.get_string(
                    interaction.guild.id,
                    "module_disabled",
                    module_name="Logging",
                ),
                ephemeral=True,
            )

        view = nextcord.ui.View(timeout=None)


def setup(bot: commands.Bot):
    bot.add_cog(LoggingSetup(bot))
