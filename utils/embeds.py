from dataclasses import dataclass
import nextcord
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
            role: nextcord.Role = interaction.guild.get_role(
                config.permission_roles.moderator
            )

            announcement_embed.colour = role.colour
            if role.icon:
                announcement_embed.set_author(
                    name="Moderator Announcement", icon_url=role.icon.url
                )
            else:
                announcement_embed.set_author(name="Moderator Announcement")

        case "admin":
            role: nextcord.Role = interaction.guild.get_role(
                config.permission_roles.dark_moderator
            )

            announcement_embed.colour = role.colour
            if role.icon:
                announcement_embed.set_author(
                    name="Administration Announcement", icon_url=role.icon.url
                )
            else:
                announcement_embed.set_author(name="Administration Announcement")

        case "cet":
            role: nextcord.Role = interaction.guild.get_role(
                config.permission_roles.cet
            )

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
