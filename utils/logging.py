import nextcord
from utils.sersi_embed import SersiEmbed
from utils.database import guild_db_manager, LoggingChannels


async def create_log(
    guild: nextcord.Guild,
    log_category: str,
    author_id: int | None = None,
    colour: nextcord.Colour | None = None,
    description: str | None = None,
    footer: str | None = None,
    image_url: str | None = None,
    thumbnail_url: str | None = None,
    title: str | None = None,
    title_url: str | None = None,
    video_url: str | None = None,
    fields: dict[str, str] | None = None,
):
    """
    Create a log message and send it to the appropriate logging channel.
    """
    with guild_db_manager.get_session(guild.id) as session:
        channel = (
            session.query(LoggingChannels).filter_by(log_category=log_category).first()
        )

        if not channel:
            return

        channel_id = channel.channel_id

        embed = SersiEmbed(
            title=title,
            description=description,
            colour=colour,
            footer=footer,
            image=image_url,
            thumbnail=thumbnail_url,
            url=title_url,
            video=video_url,
            fields=fields,
        )

        if author_id:
            member = nextcord.utils.get(
                session.query(nextcord.Member).filter_by(id=author_id).all()
            )
            if member:
                embed.set_author(name=str(member), icon_url=member.avatar.url)

        log_channel = guild.get_channel(channel_id)
        if log_channel:
            await log_channel.send(embed=embed)
        else:
            print(
                f"Log channel {channel_id} not found in guild {guild.name} ({guild.id})"
            )
            return
