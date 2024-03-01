import io
import re
import datetime

import nextcord
import nextcord.ext.commands as commands
from shortuuid.main import int_to_string, string_to_int
from chat_exporter import export

from utils.config import Configuration


def get_discord_timestamp(time: datetime.datetime, *, relative: bool = False) -> str:
    if relative:
        return f"<t:{int(time.timestamp())}:R>"
    else:
        return f"<t:{int(time.timestamp())}:f>"


def sanitize_mention(string: str) -> str:
    return re.sub(r"[^0-9]*", "", string)


async def ban(
    member: nextcord.Member,
    kind: str,
    reason: str,
):
    goodbye_embed = nextcord.Embed(
        title=f"You have been banned from {member.guild.name}",
        colour=nextcord.Color.from_rgb(237, 91, 6),
    )

    if kind == "rf":
        goodbye_embed.description = (
            f"You have been deemed to have failed reformation. As a result, you have been banned from {member.guild.name}\n"
            "If you would like to appeal your ban you can do so:\n"
            "https://appeals.wickbot.com"
        )
    elif kind == "leave":
        goodbye_embed.description = (
            f"You have left {member.guild.name} whilst in Reformation, as a result you have been banned\n"
            "If you would like to appeal your ban you can do so:\n"
            "https://appeals.wickbot.com"
        )
    else:
        goodbye_embed.description = (
            f"You have been banned from {member.guild.name}\n"
            "If you would like to appeal your ban you can do so:\n"
            "https://appeals.wickbot.com"
        )
        goodbye_embed.add_field(name="Reason:", value=reason)

    try:
        await member.send(embed=goodbye_embed)

    except nextcord.errors.Forbidden:
        pass

    await member.ban(reason=reason, delete_message_days=0)


def modmention_check(config: Configuration, message: str) -> bool:
    modmentions: list[str] = [
        f"<@&{config.permission_roles.trial_moderator}>",
        f"<@&{config.permission_roles.moderator}>",
        f"<@&{config.permission_roles.senior_moderator}>",
        f"<@&{config.permission_roles.dark_moderator}>",
    ]

    for modmention in modmentions:
        if modmention in message:
            return True
    return False


def get_page(entry_list: list, page: int, per_page: int = 10) -> tuple[list, int, int]:
    pages = 1 + (len(entry_list) - 1) // per_page

    index = page - 1
    if index < 0:
        index = 0
    elif index >= pages:
        index = pages - 1

    page = index + 1
    if page == pages:
        return entry_list[index * per_page :], pages, page
    else:
        return entry_list[index * per_page : page * per_page], pages, page


def format_entry(entry: tuple[str]) -> str:
    if len(entry[3]) >= 16:
        return "`{}`... <t:{}:R>".format(entry[3][:15], entry[4])
    else:
        return "`{}` <t:{}:R>".format(entry[3], entry[4])


def convert_mention_to_id(mention: str) -> int:
    return int(re.sub(r"\D", "", mention))


def ignored_message(
    config: Configuration,
    message: nextcord.Message,
    *,
    ignore_bots: bool = True,
    ignore_channels: bool = True,
    ignore_categories: bool = True,
    ignore_other_guilds: bool = True,
) -> bool:
    """Check if a message should be ignored by the bot."""
    if message.guild is None:
        return True  # ignore DMs
    if ignore_bots and message.author.bot:
        return True  # ignore bots
    if ignore_channels and message.channel.id in config.ignored_channels.values():
        return True  # ignore specified channels
    if ignore_categories and message.channel.category.name in config.ignored_categories:
        return True  # ignore specified categories
    if ignore_other_guilds and message.guild.id != config.guilds.main:
        return True  # ignore other guilds

    match message.content:
        case "<:sersisuccess:979066662856822844> The help menu has been updated.":
            return True

    return False


def convert_to_timedelta(timespan: str, duration: int) -> datetime.timedelta | None:
    match timespan:
        case "m":
            return datetime.timedelta(minutes=duration)

        case "h":
            if not duration > 672:
                return datetime.timedelta(hours=duration)

        case "d":
            if not duration > 28:
                return datetime.timedelta(days=duration)

        case "w":
            if not duration > 4:
                return datetime.timedelta(weeks=duration)

    return None


def limit_string(string: str, length: int = 1024) -> str:
    if len(string) > length:
        return string[: length - 3].rstrip(" .,\n") + "..."
    else:
        return string


# base on https://github.com/skorokithakis/shortuuid
_alphabet = list("23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")


def encode_snowflake(snowflake: int) -> str:
    return int_to_string(snowflake, _alphabet, padding=11)


def decode_snowflake(string: str) -> int:
    return string_to_int(string, _alphabet)


def encode_button_id(label: str, *args, **kwargs) -> str:
    id = ":".join([label, *args, *[f"{key}={value}" for key, value in kwargs.items()]])

    if len(id) > 100:
        raise ValueError("Button ID too long, must be <= 100 characters.")

    return id


def decode_button_id(custom_id: str) -> tuple[str, list[str], dict[str, str]]:
    split = custom_id.split(":")
    label = split[0]
    args = []
    kwargs = {}

    for arg in split[1:]:
        if "=" not in arg:
            args.append(arg)
            continue

        key, value = arg.split("=")
        kwargs[key] = value

    return label, args, kwargs


async def get_message_from_url(bot: commands.Bot, url: str) -> nextcord.Message | None:
    *_, guild_id, channel_id, message_id = url.split("/")

    guild = bot.get_guild(int(guild_id))
    if guild is None:
        return None

    channel = guild.get_channel(int(channel_id))
    if channel is None:
        return None

    try:
        return await channel.fetch_message(int(message_id))
    except nextcord.HTTPException:
        return None


def parse_roles(guild: nextcord.Guild, *roles: nextcord.Role | int):
    """Parses roles for use in role assignment/removal on member."""
    for role in roles:
        match role:
            case nextcord.Role():
                yield role
            case int():
                role_obj = guild.get_role(role)
                if role_obj is not None:
                    yield role_obj


async def make_transcript(
    from_channel: nextcord.TextChannel,
    to_channel: nextcord.TextChannel = None,
    embed: nextcord.Embed = None,
) -> str | None:
    """Make a transcript from a channel and send it to another channel if specified."""
    transcript: str = await export(from_channel, military_time=True)

    if transcript is None:
        return None

    transcript_file = nextcord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{from_channel.name}.html",
    )

    if to_channel is not None:
        await to_channel.send(file=transcript_file, embed=embed)

    return transcript


def get_member_level(config: Configuration, member: nextcord.Member) -> int:
    for level, role in config.level_roles.items():
        level_role = member.guild.get_role(role)
        if level_role in member.roles:
            return level
    return 0


def serialise_timedelta(duration: int, timespan: str) -> str:
    td = convert_to_timedelta(timespan, duration)

    if td is None:
        raise ValueError("Invalid duration/timespan combination")

    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"PT{int(hours)}H{int(minutes)}M{int(seconds)}S"


def deserialise_timedelta(td_str: str) -> datetime.timedelta:
    parts = td_str.strip("PT").strip("S").split("H")
    hours = int(parts[0])
    minutes, seconds = parts[1].split("M")
    minutes = int(minutes)
    seconds = int(seconds)
    return datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
