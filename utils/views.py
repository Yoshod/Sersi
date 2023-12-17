import nextcord
import nextcord.ext.commands as commands
from nextcord.ui import View, Button

from utils.config import Configuration
from utils.perms import permcheck, is_dark_mod
from utils.sersi_embed import SersiEmbed

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
                config: Configuration,
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
                config: Configuration,
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
        config: Configuration,
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
