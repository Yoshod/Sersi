import nextcord
from configutils import get_config_int, get_config
from nextcord.ui import View, Button
import re

from permutils import permcheck


def sanitize_mention(string: str) -> str:
    return re.sub(r"[^0-9]*", "",  string)


async def ban(member: nextcord.Member, kind, reason):
    goodbye_embed = nextcord.Embed(
        title=f"You have been banned from {member.guild.name}",
        colour=nextcord.Color.from_rgb(237, 91, 6))

    if kind == "rf":
        goodbye_embed.description = f"You have been deemed to have failed reformation. As a result, you have been banned from {member.guild.name}\n\nIf you wish to appeal your ban, please join the ban appeal server:\n{get_config('INVITES', 'appeal server')}"
    elif kind == "leave":
        goodbye_embed.description = f"You have left {member.guild.name} whilst in Reformation, as a result you have been banned\n\nIf you wish to appeal your ban, please join the ban appeal server:\n{get_config('INVITES', 'appeal server')}"

    await member.send(embed=goodbye_embed)

    await member.ban(reason=reason, delete_message_days=0)


def modmention_check(messageData):
    modmentions = [
        f"<@&{get_config_int('PERMISSION ROLES', 'trial moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'senior moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'dark moderator')}>"
    ]

    for modmention in modmentions:
        if modmention in messageData:
            return True
    return False


def get_page(entry_list, page, per_page=10):
    pages = 1 + (len(entry_list) - 1) // per_page

    index = page - 1
    if index < 0:
        index = 0
    elif index >= pages:
        index = pages - 1

    page = index + 1
    if page == pages:
        return entry_list[index * per_page:], pages, page
    else:
        return entry_list[index * per_page: page * per_page], pages, page


class ConfirmView(View):
    def __init__(self, on_proceed, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        btn_proceed = Button(label="Proceed", style=nextcord.ButtonStyle.green)
        btn_proceed.callback = on_proceed
        btn_cancel = Button(label="Cancel", style=nextcord.ButtonStyle.red)
        btn_cancel.callback = self.cb_cancel
        self.add_item(btn_proceed)
        self.add_item(btn_cancel)

    async def cb_cancel(self, interaction):
        await interaction.message.edit("Action canceled!", embed=None, view=None)

    async def on_timeout(self):
        self.message = await self.message.channel.fetch_message(self.message.id)
        if self.message.components != []:
            await self.message.edit("Action timed out!", embed=None, view=None)

    async def interaction_check(self, interaction):
        return interaction.user == interaction.message.reference.cached_message.author

    async def send_as_reply(self, ctx, content: str = None, embed=None):
        self.message = await ctx.reply(content, embed=embed, view=self)


class DualCustodyView(View):
    def __init__(self, on_confirm, author, has_perms, timeout: float = 600.0):
        super().__init__(timeout=timeout)
        btn_confirm = Button(label="Confirm Action", style=nextcord.ButtonStyle.green)
        btn_confirm.callback = on_confirm
        self.add_item(btn_confirm)
        self.has_perms = has_perms
        self.author = author

    async def on_timeout(self):
        await self.message.edit(view=None)

    async def interaction_check(self, interaction):
        if interaction.user == self.author:
            return False

        return permcheck(interaction, self.has_perms)

    async def send_dialogue(self, channel, content: str = None, embed=None):
        self.message = await channel.send(content, embed=embed, view=self)


class PageView(View):
    def __init__(self, base_embed, fetch_function, author, entry_form="**•**\u00A0{entry}", cols=1, per_col=10, init_page=1, **kwargs):
        super().__init__()
        btn_prev = Button(label="< prev")
        btn_prev.callback = self.cb_prev_page
        btn_next = Button(label="next >")
        btn_next.callback = self.cb_next_page
        self.add_item(btn_prev)
        self.add_item(btn_next)
        self.page = init_page
        self.kwargs = kwargs
        self.author = author
        self.columns = cols
        self.per_column = per_col
        self.embed_base = base_embed
        self.entry_format = entry_form
        self.get_entries = fetch_function

    def make_column(self, entries):
        entry_list = []
        for entry in entries:
            entry_list.append(self.entry_format.format(entry=entry))
        return "\n".join(entry_list)

    def make_embed(self, page):
        embed = self.embed_base.copy()
        entries, pages, self.page = self.get_entries(page=page, per_page=self.columns * self.per_column, **self.kwargs)
        cols = min(self.columns, 1 + (len(entries) - 1) // self.per_column)
        for col in range(1, cols + 1):
            if col == cols:
                embed.add_field(name="\u200b", value=self.make_column(entries[(col - 1) * self.per_column:]))
            else:
                embed.add_field(name="\u200b", value=self.make_column(entries[(col - 1) * self.per_column: col * self.per_column]))
        embed.set_footer(text=f"page {self.page}/{pages}")
        return embed

    async def update_embed(self, page):
        await self.message.edit(embed=self.make_embed(page))

    async def cb_next_page(self, interaction):
        await self.update_embed(self.page + 1)

    async def cb_prev_page(self, interaction):
        await self.update_embed(self.page - 1)

    async def on_timeout(self):
        await self.message.edit(view=None)

    async def interaction_check(self, interaction):
        return interaction.user == self.author

    async def send_embed(self, channel):
        self.message = await channel.send(embed=self.make_embed(self.page), view=self)
