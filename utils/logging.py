import nextcord
from utils.sersi_embed import SersiEmbed
from utils.database import SessionLocal, LoggingChannels
from utils.language import lang_manager


async def create_log(guild: nextcord.Guild, log_type: str, log_category: str, **kwargs):
    """
    Create a log entry in the database for the specified guild and log type.

    :param guild: The guild where the log is being created.
    :param log_type: The type of log (e.g., 'message_delete', 'user_ban').
    :param log_category: The category of the log (e.g., 'global', 'guild').
    :param kwargs: Additional keyword arguments to include in the log.
    """
    with SessionLocal() as session:
        logging_channel = (
            session.query(LoggingChannels)
            .filter_by(log_type=log_category, guild_id=guild.id)
            .first()
        )

        logging_channel = guild.get_channel(logging_channel.channel_id)

        if not logging_channel:
            return

        match log_type:
            case "logging_setup_complete":
                embed = SersiEmbed(
                    title=lang_manager.get_string(
                        guild.id, "logging.setup.complete.title"
                    ),
                    description=lang_manager.get_string(
                        guild.id, "logging.setup.complete.description"
                    ),
                )

            case "message_delete":
                embed = SersiEmbed(
                    description=lang_manager.get_string(
                        guild.id, "logging.message_delete.description"
                    ).format(**kwargs),
                    thumbnail_url=kwargs.get("thumbnail_url", None),
                    author=kwargs.get("author", None),
                    footer=lang_manager.get_string(
                        guild.id, "logging.message_delete.footer"
                    ),
                    fields=[
                        {
                            lang_manager.get_string(
                                guild.id,
                                "logging.message_delete.fields.message_content",
                            ): kwargs.get("message_content"),
                            lang_manager.get_string(
                                guild.id, "logging.message_delete.fields.channel"
                            ): kwargs.get("channel_id"),
                            lang_manager.get_string(
                                guild.id, "logging.message_delete.fields.created"
                            ): kwargs.get("created_at", None),
                            lang_manager.get_string(
                                guild.id, "logging.message_delete.fields.deleted"
                            ): kwargs.get("deleted_at", None),
                            lang_manager.get_string(
                                guild.id, "logging.message_delete.fields.deleted_by"
                            ): kwargs.get("deleted_by", None),
                        }
                    ],
                )

        return await logging_channel.send(embed=embed)
