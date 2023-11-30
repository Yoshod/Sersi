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
from utils.perms import permcheck, is_dark_mod
from utils.sersi_embed import SersiEmbed


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


class ConfirmView(nextcord.ui.View):
    def __init__(
        self,
        on_proceed,
        timeout: float = 60.0,
    ):
        super().__init__(timeout=timeout)
        btn_proceed = Button(label="Proceed", style=nextcord.ButtonStyle.green)
        btn_proceed.callback = on_proceed
        btn_cancel = Button(label="Cancel", style=nextcord.ButtonStyle.red)
        btn_cancel.callback = self.cb_cancel
        self.add_item(btn_proceed)
        self.add_item(btn_cancel)
        self.message: nextcord.Message
        self.author: nextcord.Member

    async def cb_cancel(self, interaction: nextcord.Interaction):
        await interaction.message.edit(
            content="Action canceled!", embed=None, view=None
        )

    async def on_timeout(self):
        self.message = await self.message.channel.fetch_message(self.message.id)
        if self.message.components != []:
            await self.message.edit(content="Action timed out!", embed=None, view=None)

    async def interaction_check(self, interaction: nextcord.Interaction):
        return interaction.user == self.author

    async def send_as_reply(
        self, ctx: commands.Context, content: str = None, embed=None
    ):
        self.author = ctx.author
        self.message = await ctx.reply(content, embed=embed, view=self)

    async def send_as_followup_response(
        self, interaction: nextcord.Interaction, content: str = None, embed=None
    ):
        self.author = interaction.user
        self.message = await interaction.followup.send(content, embed=embed, view=self)

    @staticmethod
    def query(title: str, prompt: str, embed_args: dict = {}) -> callable:
        def wrapper(func: callable) -> callable:
            async def confirm(
                bot: commands.Bot,
                config: utils.config.Configuration,
                interaction: nextcord.Interaction,
            ):
                embed_fields = embed_args.copy()
                dialog_embed = SersiEmbed(
                    title=title,
                    description=prompt,
                    fields=embed_fields,
                )

                async def cb_proceed(interaction: nextcord.Interaction):
                    await interaction.message.edit(view=None)
                    new_embed = await func(bot, config, interaction)
                    if new_embed is not None:
                        await interaction.message.edit(embed=new_embed)

                view = ConfirmView(cb_proceed)
                await view.send_as_followup_response(interaction, embed=dialog_embed)

            return confirm

        return wrapper


class DualCustodyView(View):
    def __init__(self, on_confirm, author, has_perms, timeout: float = 600.0):
        super().__init__(timeout=timeout)
        btn_confirm = Button(label="Confirm Action", style=nextcord.ButtonStyle.green)
        btn_confirm.callback = on_confirm
        self.add_item(btn_confirm)
        self.has_perms = has_perms
        self.author = author
        self.message: nextcord.Message

    async def on_timeout(self):
        await self.message.edit(view=None)

    async def interaction_check(self, interaction: nextcord.Interaction):
        if interaction.user == self.author:
            return False

        return await permcheck(interaction, self.has_perms)

    async def send_dialogue(self, channel, content: str = None, embed=None):
        self.message = await channel.send(content, embed=embed, view=self)

    @staticmethod
    def query(
        title: str,
        prompt: str,
        perms: callable,
        embed_args: dict = {},
        bypass: bool = False,
    ) -> callable:
        def wrapper(func: callable) -> callable:
            async def dual_custody(
                bot: commands.Bot,
                config: utils.config.Configuration,
                interaction: nextcord.Interaction,
            ) -> nextcord.Embed:
                # if command used by admin, skip dual custody query
                if bypass and is_dark_mod(interaction.user):
                    return await func(
                        bot, config, interaction, confirming_moderator=interaction.user
                    )

                embed_fields = embed_args.copy()
                embed_fields.update({"Moderator": interaction.user.mention})
                dialog_embed = SersiEmbed(
                    title=title,
                    description=prompt,
                    fields=embed_fields,
                )

                async def cb_confirm(interaction: nextcord.Interaction):
                    await interaction.message.edit(view=None)
                    new_embed = await func(
                        bot, config, interaction, confirming_moderator=interaction.user
                    )
                    if new_embed is None:
                        new_embed = dialog_embed
                    new_embed.add_field(
                        name="Confirmed by:", value=interaction.user.mention
                    )
                    await interaction.message.edit(embed=new_embed)

                channel = bot.get_channel(config.channels.alert)
                view = DualCustodyView(cb_confirm, interaction.user, perms)
                await view.send_dialogue(channel, embed=dialog_embed)

                await interaction.followup.send(
                    embed=SersiEmbed(
                        title=title,
                        description="Pending review by another moderator",
                    ),
                    ephemeral=True,
                )

            return dual_custody

        return wrapper


class PageView(View):
    def __init__(
        self,
        config: utils.config.Configuration,
        base_embed: nextcord.Embed,
        fetch_function: callable,
        author: nextcord.Member,
        entry_form: str = "**•**\u00A0{entry}",
        field_title: str = "{start} \u2014 {end}",
        inline_fields: bool = True,
        cols: int = 1,
        per_col: int = 10,
        init_page: int = 1,
        no_entries: str = "{config.emotes.fail} There are no entries to display.",
        ephemeral: bool = False,
        **kwargs,
    ):
        super().__init__()
        btn_prev = Button(label="< prev")
        btn_prev.callback = self.cb_prev_page
        btn_next = Button(label="next >")
        btn_next.callback = self.cb_next_page
        self.add_item(btn_prev)
        self.add_item(btn_next)
        self.config = config
        self.page = init_page
        self.kwargs = kwargs
        self.author = author
        self.columns = cols
        self.per_column = per_col
        self.embed_base = base_embed
        self.entry_format = entry_form
        self.column_title = field_title
        self.inline_fields = inline_fields
        self.get_entries = fetch_function
        self.no_entries = no_entries
        self.ephemeral = ephemeral
        self.message: nextcord.Message

    def make_column(self, entries):
        entry_list = []
        if callable(self.entry_format):
            for entry in entries:
                entry_list.append(self.entry_format(config=self.config, entry=entry))
        elif isinstance(self.entry_format, str):
            for entry in entries:
                entry_list.append(
                    self.entry_format.format(config=self.config, entry=entry)
                )
        else:
            raise ValueError(
                "Invalid entry_format type. Must be a function or a string."
            )
        return "\n".join(entry_list)

    def make_embed(self, page: int):
        embed = self.embed_base.copy()
        entries, pages, self.page = self.get_entries(
            self.config,
            page=page,
            per_page=self.columns * self.per_column,
            **self.kwargs,
        )
        if not entries:
            embed.description = self.no_entries.format(config=self.config)
            return embed
        cols = min(self.columns, 1 + (len(entries) - 1) // self.per_column)
        offset = (self.page - 1) * self.columns * self.per_column
        for col in range(1, cols + 1):
            col_start = (col - 1) * self.per_column
            col_end = len(entries) if col == cols else col * self.per_column
            col_entries = entries[col_start:col_end]
            embed.add_field(
                name=self.column_title.format(
                    config=self.config,
                    start=col_start + offset + 1,
                    end=col_end + offset,
                    entries=col_entries,
                ),
                value=self.make_column(col_entries),
                inline=self.inline_fields,
            )
        embed.set_footer(text=f"page {self.page}/{pages}")
        return embed

    async def update_embed(self, page: int):
        await self.message.edit(embed=self.make_embed(page))

    async def cb_next_page(self, interaction: nextcord.Interaction):
        await self.update_embed(self.page + 1)

    async def cb_prev_page(self, interaction: nextcord.Interaction):
        await self.update_embed(self.page - 1)

    async def on_timeout(self):
        await self.message.edit(view=None)

    async def interaction_check(self, interaction: nextcord.Interaction):
        return interaction.user == self.author

    async def send_embed(self, channel: nextcord.TextChannel):
        self.message = await channel.send(embed=self.make_embed(self.page), view=self)

    async def send_followup(self, interaction: nextcord.Interaction):
        self.message = await interaction.followup.send(
            embed=self.make_embed(self.page), view=self, ephemeral=self.ephemeral
        )


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
