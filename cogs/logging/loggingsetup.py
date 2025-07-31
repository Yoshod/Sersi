import nextcord
from nextcord.ext import commands, application_checks
from utils.database import (
    SessionLocal,
    LoggingChannels,
)
from utils.language import lang_manager
from utils.modules import check_module_enabled
from utils.logging import create_log
from utils.base import encode_button_id, decode_button_id
from utils.sersi_embed import SersiEmbed


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


class FinishSetupButton(nextcord.ui.Button):
    def __init__(self, guild: nextcord.Guild):
        super().__init__(
            label=lang_manager.get_string(
                guild.id, "logging.setup.buttons.finish_setup"
            ),
            style=nextcord.ButtonStyle.green,
            custom_id=encode_button_id("logging_setup", category="finish_setup"),
        )

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.message.delete()
        await create_log(
            interaction.guild,
            "logging_setup_complete",
            "global",
        )
        await interaction.followup.send(
            lang_manager.get_string(
                interaction.guild.id, "logging.setup.finish.success"
            ),
            ephemeral=True,
        )


class ChannelSelector(nextcord.ui.ChannelSelect):
    def __init__(self, guild: nextcord.Guild, start: bool = False):
        super().__init__(
            placeholder=lang_manager.get_string(
                guild.id, "logging.setup.select_channel"
            ),
            min_values=1,
            max_values=1,
            channel_types=[nextcord.ChannelType.text],
            disabled=start,
        )

    async def callback(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("values") is None:
            return

        with SessionLocal() as session:
            existing_channel = (
                session.query(LoggingChannels)
                .filter_by(
                    guild_id=interaction.guild.id,
                    log_type=interaction.message.embeds[0]
                    .title.lower()
                    .replace(" ", "_"),
                )
                .first()
            )

            if existing_channel:
                existing_channel.channel_id = int(self.values[0].id)
            else:
                new_channel = LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type=interaction.message.embeds[0]
                    .title.lower()
                    .replace(" ", "_"),
                    channel_id=int(self.values[0].id),
                )
                session.add(new_channel)

            session.commit()

            view = LoggingSetupView(interaction.guild, start=False)

            completed = (
                session.query(LoggingChannels)
                .filter_by(guild_id=interaction.guild.id)
                .count()
                == 13
            )
            if completed:
                view.add_item(FinishSetupButton(interaction.guild))

        await interaction.message.edit(
            view=view,
        )


class LoggingSetupView(nextcord.ui.View):
    def __init__(self, guild: nextcord.Guild, start: bool = False):
        super().__init__(timeout=None)
        self.guild = guild

        with SessionLocal() as session:
            existing_channels = (
                session.query(LoggingChannels).filter_by(guild_id=guild.id).all()
            )

        self.add_item(
            TamperLogsButton(
                guild=guild,
                selected="tamper" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            GlobalLogsButton(
                guild=guild,
                selected="global" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            PublicLogsButton(
                guild=guild,
                selected="public" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            ModLogsButton(
                guild=guild,
                selected="moderation" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            GuildLogsButton(
                guild=guild, selected="guild" in [c.log_type for c in existing_channels]
            )
        )
        self.add_item(
            ChannelLogsButton(
                guild=guild,
                selected="channel" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            RoleLogsButton(
                guild=guild, selected="role" in [c.log_type for c in existing_channels]
            )
        )
        self.add_item(
            JoinLeaveLogsButton(
                guild=guild,
                selected="join_leave" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            VoiceLogsButton(
                guild=guild, selected="voice" in [c.log_type for c in existing_channels]
            )
        )
        self.add_item(
            UserLogsButton(
                guild=guild, selected="user" in [c.log_type for c in existing_channels]
            )
        )
        self.add_item(
            DeletedMessageLogsButton(
                guild=guild,
                selected="deleted_messages" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            DeletedImageLogsButton(
                guild=guild,
                selected="deleted_images" in [c.log_type for c in existing_channels],
            )
        )
        self.add_item(
            EditedMessageLogsButton(
                guild=guild,
                selected="edited_messages" in [c.log_type for c in existing_channels],
            )
        )

        self.add_item(ChannelSelector(guild=guild, start=start))


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

        with SessionLocal() as session:
            existing_channels = (
                session.query(LoggingChannels)
                .filter_by(guild_id=interaction.guild.id)
                .all()
            )

            if existing_channels:
                return await interaction.followup.send(
                    lang_manager.get_string(
                        interaction.guild.id,
                        "logging.setup.express.already_setup",
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

        with SessionLocal() as session:
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="global",
                    channel_id=global_log.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="public",
                    channel_id=public_log.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="tamper",
                    channel_id=tamper_log.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="moderation",
                    channel_id=mod_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="guild",
                    channel_id=guild_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="channel",
                    channel_id=channel_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="role",
                    channel_id=role_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="join_leave",
                    channel_id=join_leave_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="voice",
                    channel_id=voice_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="user",
                    channel_id=user_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="deleted_messages",
                    channel_id=deleted_message_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="deleted_images",
                    channel_id=deleted_image_logs.id,
                )
            )
            session.add(
                LoggingChannels(
                    guild_id=interaction.guild.id,
                    log_type="edited_messages",
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
    async def custom_setup(
        self,
        interaction: nextcord.Interaction,
        tamper_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="tamper_logs", description="Channel for tamper logs", required=False
        ),
        global_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="global_logs", description="Channel for global logs", required=False
        ),
        public_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="public_logs",
            description="Channel for public mod logs",
            required=False,
        ),
        mod_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="mod_logs", description="Channel for mod logs", required=False
        ),
        guild_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="guild_logs", description="Channel for guild logs", required=False
        ),
        channel_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="channel_logs", description="Channel for channel logs", required=False
        ),
        role_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="role_logs", description="Channel for role logs", required=False
        ),
        join_leave_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="join_leave_logs",
            description="Channel for join/leave logs",
            required=False,
        ),
        voice_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="voice_logs", description="Channel for voice logs", required=False
        ),
        user_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="user_logs", description="Channel for user logs", required=False
        ),
        deleted_message_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="deleted_message_logs",
            description="Channel for deleted message logs",
            required=False,
        ),
        deleted_image_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="deleted_image_logs",
            description="Channel for deleted image logs",
            required=False,
        ),
        edited_message_logs: nextcord.TextChannel = nextcord.SlashOption(
            name="edited_message_logs",
            description="Channel for edited message logs",
            required=False,
        ),
    ):
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

        with SessionLocal() as session:
            existing_channels = (
                session.query(LoggingChannels)
                .filter_by(guild_id=interaction.guild.id)
                .all()
            )

            if existing_channels:
                return await interaction.followup.send(
                    lang_manager.get_string(
                        interaction.guild.id,
                        "logging.setup.custom.already_setup",
                    ),
                    ephemeral=True,
                )

            # If the user has provided channels using the optional args we should set those in the database here
            if tamper_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="tamper",
                        channel_id=tamper_logs.id,
                    )
                )
            if global_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="global",
                        channel_id=global_logs.id,
                    )
                )
            if public_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="public",
                        channel_id=public_logs.id,
                    )
                )
            if mod_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="moderation",
                        channel_id=mod_logs.id,
                    )
                )
            if guild_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="guild",
                        channel_id=guild_logs.id,
                    )
                )
            if channel_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="channel",
                        channel_id=channel_logs.id,
                    )
                )
            if role_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="role",
                        channel_id=role_logs.id,
                    )
                )
            if join_leave_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="join_leave",
                        channel_id=join_leave_logs.id,
                    )
                )
            if voice_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="voice",
                        channel_id=voice_logs.id,
                    )
                )
            if user_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="user",
                        channel_id=user_logs.id,
                    )
                )
            if deleted_message_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="deleted_messages",
                        channel_id=deleted_message_logs.id,
                    )
                )
            if deleted_image_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="deleted_images",
                        channel_id=deleted_image_logs.id,
                    )
                )
            if edited_message_logs:
                session.add(
                    LoggingChannels(
                        guild_id=interaction.guild.id,
                        log_type="edited_messages",
                        channel_id=edited_message_logs.id,
                    )
                )
            session.commit()

        view = LoggingSetupView(interaction.guild, start=True)
        embed = SersiEmbed(
            title=lang_manager.get_string(
                interaction.guild.id, "logging.setup.custom.title"
            ),
            description=lang_manager.get_string(
                interaction.guild.id, "logging.setup.custom.description"
            ),
        )

        await interaction.followup.send(
            embed=embed,
            view=view,
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        """Listens for button clicks and dropdown selections from the setup message."""
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        if not interaction.data["custom_id"].startswith("logging_setup"):
            return

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        if action == "logging_setup" and "category" in kwargs:
            category = kwargs["category"]

            await interaction.message.edit(
                embed=SersiEmbed(
                    title=lang_manager.get_string(
                        interaction.guild.id, f"logging.setup.{category}.title"
                    ),
                    description=lang_manager.get_string(
                        interaction.guild.id, f"logging.setup.{category}.description"
                    ),
                ),
                view=LoggingSetupView(
                    interaction.guild,
                    start=False,
                ),
            )


def setup(bot: commands.Bot):
    bot.add_cog(LoggingSetup(bot))
