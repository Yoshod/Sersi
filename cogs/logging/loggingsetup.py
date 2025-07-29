import nextcord
from nextcord.ext import commands, application_checks
from utils.database import (
    guild_db_manager,
    LoggingChannels,
)
from utils.language import lang_manager
from utils.modules import check_module_enabled
from utils.logging import create_log


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
            guild=interaction.guild,
            log_category="global",
            title=lang_manager.get_string(
                interaction.guild.id, "logging.setup.express.log_title"
            ),
            description=lang_manager.get_string(
                interaction.guild.id, "logging.setup.express.log_description"
            ),
        )
        return


def setup(bot: commands.Bot):
    bot.add_cog(LoggingSetup(bot))
