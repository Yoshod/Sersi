import nextcord
import nextcord.ext.commands as commands
import configutils
from nextcord.ui import View, Button
import re
from datetime import datetime
import pytz

from permutils import permcheck, is_dark_mod

config = configutils.Configuration.from_yaml_file("./persistent_data/config.yaml")


class SersiEmbed(nextcord.Embed):
    def __init__(
        self,
        *,
        fields: dict[str, str] = None,
        footer: str = nextcord.embeds.EmptyEmbed,
        footer_icon: str = nextcord.embeds.EmptyEmbed,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Configure Embed Footer
        self.set_footer(text=footer, icon_url=footer_icon)
        self.timestamp = datetime.now(pytz.UTC)

        # Configure Colour
        if "color" not in kwargs and "colour" not in kwargs:
            self.colour = nextcord.Color.from_rgb(237, 91, 6)

        # Configure Fields
        if fields:
            for field in fields:
                self.add_field(name=field, value=fields[field], inline=False)


def sanitize_mention(string: str) -> str:
    return re.sub(r"[^0-9]*", "", string)


async def ban(config: configutils.Configuration, member: nextcord.Member, kind, reason):
    goodbye_embed = nextcord.Embed(
        title=f"You have been banned from {member.guild.name}",
        colour=nextcord.Color.from_rgb(237, 91, 6),
    )

    if kind == "rf":
        goodbye_embed.description = f"You have been deemed to have failed reformation. As a result, you have been banned from {member.guild.name}\n\nIf you wish to appeal your ban, please join the ban appeal server:\n{config.invites.ban_appeal_server}"
    elif kind == "leave":
        goodbye_embed.description = f"You have left {member.guild.name} whilst in Reformation, as a result you have been banned\n\nIf you wish to appeal your ban, please join the ban appeal server:\n{config.invites.ban_appeal_server}"

    try:
        await member.send(embed=goodbye_embed)

    except nextcord.errors.Forbidden:
        return

    await member.ban(reason=reason, delete_message_days=0)


def modmention_check(config: configutils.Configuration, message: str) -> bool:
    modmentions = [
        f"<@&{config.permission_roles.trial_moderator}>",
        f"<@&{config.permission_roles.moderator}>",
        f"<@&{config.permission_roles.senior_moderator}>",
        f"<@&{config.permission_roles.dark_moderator}>",
    ]

    for modmention in modmentions:
        if modmention in message:
            return True
    return False


def get_page(entry_list: list, page: int, per_page: int = 10):
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


class ConfirmView(View):
    def __init__(self, on_proceed, timeout: float = 60.0, bypass_button: bool = False):
        super().__init__(timeout=timeout)
        btn_proceed = Button(label="Proceed", style=nextcord.ButtonStyle.green)
        btn_proceed.callback = on_proceed
        btn_cancel = Button(label="Cancel", style=nextcord.ButtonStyle.red)
        btn_cancel.callback = self.cb_cancel
        self.add_item(btn_proceed)
        self.add_item(btn_cancel)
        self.message: nextcord.Message

    async def cb_cancel(self, interaction: nextcord.Interaction):
        await interaction.message.edit("Action canceled!", embed=None, view=None)

    async def on_timeout(self):
        self.message = await self.message.channel.fetch_message(self.message.id)
        if self.message.components != []:
            await self.message.edit("Action timed out!", embed=None, view=None)

    async def interaction_check(self, interaction: nextcord.Interaction):
        return interaction.user == interaction.message.reference.cached_message.author

    async def send_as_reply(
        self, ctx: commands.Context, content: str = None, embed=None
    ):
        self.message = await ctx.reply(content, embed=embed, view=self)

    @staticmethod
    def query(title: str, prompt: str, embed_args: dict = {}) -> callable:
        def wrapper(func: callable) -> callable:
            async def confirm(
                bot: commands.Bot,
                config: configutils.Configuration,
                ctx: commands.Context,
            ):
                embed_fields = embed_args.copy()
                dialog_embed = SersiEmbed(
                    title=title,
                    description=prompt,
                    fields=embed_fields,
                )

                async def cb_proceed(interaction: nextcord.Interaction):
                    await interaction.message.edit(view=None)
                    dialog_embed = await func(bot, config, ctx)
                    if dialog_embed is not None:
                        await interaction.message.edit(embed=dialog_embed)

                view = ConfirmView(cb_proceed)
                await view.send_as_reply(ctx, embed=dialog_embed)

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
        title: str, prompt: str, perms: callable, embed_args: dict = {}
    ) -> callable:
        def wrapper(func: callable) -> callable:
            async def dual_custody(
                bot: commands.Bot,
                config: configutils.Configuration,
                ctx: commands.Context,
            ) -> nextcord.Embed:

                # if command used by admin, skip dual custody query
                if is_dark_mod(ctx.author):
                    return await func(bot, config, ctx, confirming_moderator=ctx.author)

                embed_fields = embed_args.copy()
                embed_fields.update({"Moderator": ctx.author.mention})
                dialog_embed = SersiEmbed(
                    title=title,
                    description=prompt,
                    fields=embed_fields,
                )

                async def cb_confirm(interaction: nextcord.Interaction):
                    await interaction.message.edit(view=None)
                    new_embed = await func(
                        bot, config, ctx, confirming_moderator=interaction.user
                    )
                    if new_embed is None:
                        new_embed = dialog_embed
                    new_embed.add_field(
                        name="Confirmed by:", value=interaction.user.mention
                    )
                    await interaction.message.edit(embed=new_embed)

                channel = bot.get_channel(config.channels.alert)
                view = DualCustodyView(cb_confirm, ctx.author, perms)
                await view.send_dialogue(channel, embed=dialog_embed)

                return SersiEmbed(
                    title=title,
                    description="Pending review by another moderator",
                )

            return dual_custody

        return wrapper


class PageView(View):
    def __init__(
        self,
        config: configutils.Configuration,
        base_embed,
        fetch_function,
        author,
        entry_form="**•**\u00A0{entry}",
        cols=1,
        per_col=10,
        init_page=1,
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
        self.get_entries = fetch_function
        self.message: nextcord.Message

    def make_column(self, entries):
        entry_list = []
        for entry in entries:
            entry_list.append(self.entry_format.format(entry=entry))
        return "\n".join(entry_list)

    def make_embed(self, page):
        embed = self.embed_base.copy()
        entries, pages, self.page = self.get_entries(
            self.config,
            page=page,
            per_page=self.columns * self.per_column,
            **self.kwargs,
        )
        cols = min(self.columns, 1 + (len(entries) - 1) // self.per_column)
        for col in range(1, cols + 1):
            if col == cols:
                embed.add_field(
                    name="\u200b",
                    value=self.make_column(entries[(col - 1) * self.per_column :]),
                )
            else:
                embed.add_field(
                    name="\u200b",
                    value=self.make_column(
                        entries[(col - 1) * self.per_column : col * self.per_column]
                    ),
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

    async def send_embed(self, channel):
        self.message = await channel.send(embed=self.make_embed(self.page), view=self)
