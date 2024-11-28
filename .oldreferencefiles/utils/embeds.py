from dataclasses import dataclass
import nextcord
from utils.base import get_page
from utils.database import db_session, Autopost, TemporaryRoles, IssuedTemporaryRoles
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


@dataclass
class AutopostData:
    """
    Represents data for autoposting embeds.

    Attributes:
        author (int): The ID of the author.
        title (str): The title of the embed.
        description (str): The description of the embed.
        embed_type (str): The type of the embed.
        channel (int): The ID of the text channel.
        timedelta (str): The time interval for autoposting.
        active (bool): Indicates if autoposting is active.
        fields (dict | None): The fields of the embed.
        media_url (str | None): The URL of the media.
    """

    author: int
    title: str
    description: str
    embed_type: str
    channel: nextcord.TextChannel.id
    timedelta: str
    active: bool
    fields: dict | None
    media_url: str | None


async def determine_embed_type(
    title: str,
    body: str,
    embed_type: str,
    interaction: nextcord.Interaction,
    config: Configuration,
    media_url: str | None,
    fields: dict[str, str] | None,
) -> nextcord.Embed:
    if "\\n" in body:
        body_list = body.split("\\n")
        body = "\n".join(body_list)

    if "/n" in body:
        body_list = body.split("/n")
        body = "\n".join(body_list)

    announcement_embed: nextcord.Embed = SersiEmbed(
        title=title, description=body, footer="Sersi Announcement"
    )

    if media_url:
        announcement_embed.set_image(url=media_url)

    if fields:
        for name, value in fields.items():
            announcement_embed.add_field(name=name, value=value)

    announcement_embed.set_thumbnail(url=interaction.guild.icon.url)

    match embed_type:
        case "moderator":
            role: nextcord.Role = interaction.guild.get_role(config.roles.staff.mod)

            announcement_embed.colour = role.colour
            if role.icon:
                announcement_embed.set_author(
                    name="Moderator Announcement", icon_url=role.icon.url
                )
            else:
                announcement_embed.set_author(name="Moderator Announcement")

        case "admin":
            role: nextcord.Role = interaction.guild.get_role(config.roles.staff.admin)

            announcement_embed.colour = role.colour
            if role.icon:
                announcement_embed.set_author(
                    name="Administration Announcement", icon_url=role.icon.url
                )
            else:
                announcement_embed.set_author(name="Administration Announcement")

        case "cet":
            role: nextcord.Role = interaction.guild.get_role(config.roles.staff.cet)

            announcement_embed.colour = role.colour
            if role.icon:
                announcement_embed.set_author(
                    name="Community Announcement", icon_url=role.icon.url
                )
            else:
                announcement_embed.set_author(name="Community Announcement")

        case "staff":
            announcement_embed.set_author(name="Staff Announcement")

    return announcement_embed


def fetch_all_autoposts(
    config: Configuration,
    page: int,
    per_page: int,
    autopost_type: str | None,
    active: bool | None,
):
    with db_session() as session:
        _query = session.query(Autopost)

        if autopost_type:
            _query = _query.filter_by(embed_type=autopost_type)

        if active is not None:
            _query = _query.filter_by(active=active)

        autoposts = _query.order_by(Autopost.autopost_id).all()

        if not autoposts:
            return None, 0, 0

        page_autoposts, page, pages = get_page(autoposts, page, per_page)
        for autopost in page_autoposts:
            repr(autopost)

        return page_autoposts, page, pages


def fetch_all_temporary_roles(
    config: Configuration,
    page: int,
    per_page: int,
):
    with db_session() as session:
        _query = session.query(TemporaryRoles)

        temporary_roles = _query.order_by(TemporaryRoles.role_id).all()

        if not temporary_roles:
            return None, 0, 0

        page_temporary_roles, page, pages = get_page(temporary_roles, page, per_page)
        for temporary_role in page_temporary_roles:
            repr(temporary_role)

        return page_temporary_roles, page, pages


def fetch_all_issued_temporary_roles(
    config: Configuration,
    page: int,
    per_page: int,
    role: nextcord.Role | None,
    issued_to: nextcord.Member | None,
    issued_by: nextcord.Member | None,
):
    with db_session() as session:
        _query = session.query(IssuedTemporaryRoles)

        if role:
            _query = _query.filter_by(role_id=role.id)

        if issued_to:
            _query = _query.filter_by(user_id=issued_to.id)

        if issued_by:
            _query = _query.filter_by(added_by=issued_by.id)

        issued_temporary_roles = _query.order_by(IssuedTemporaryRoles.issued_date).all()

        if not issued_temporary_roles:
            return None, 0, 0

        page_issued_temporary_roles, page, pages = get_page(
            issued_temporary_roles, page, per_page
        )
        for issued_temporary_role in page_issued_temporary_roles:
            repr(issued_temporary_role)

        return page_issued_temporary_roles, page, pages
