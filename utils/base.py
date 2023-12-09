# Nextcord Imports
import nextcord
import nextcord.ext.commands as commands
from nextcord.ui import View, Button

# Library Imports
import re
import datetime
from shortuuid.main import int_to_string, string_to_int

# Sersi Config Imports
import utils.config


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


def modmention_check(config: utils.config.Configuration, message: str) -> bool:
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
    config: utils.config.Configuration,
    message: nextcord.Message,
    *,
    ignore_bots: bool = True,
    ignore_channels: bool = True,
    ignore_categories: bool = True,
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
    id = ":".join(
        [label, *args, *[f"{key}={value}" for key, value in kwargs.items()]]
    )

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
