import nextcord
import time
from nextcord.ext import commands

from baseutils import SersiEmbed, PageView
from noteutils import (
    create_note,
    get_note_by_id,
    fetch_notes_by_partial_id,
    create_note_embed,
    get_note_by_user,
)
from configutils import Configuration
from permutils import permcheck, is_mod, is_senior_mod


def format_entry(entry):
    if len(entry[3]) >= 16:
        return "`{}`... <t:{}:R>".format(entry[3][:15], entry[4])
    else:
        return "`{}` <t:{}:R>".format(entry[3], entry[4])


class Notes(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Note base command",
    )
    async def notes(self, interaction: nextcord.Interaction):
        pass

    @notes.subcommand(description="Add a note to a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        noted: nextcord.Member,
        note: str = nextcord.SlashOption(
            name="note",
            description="The thing you wish to note",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        create_note(self.config, noted, interaction.user, note, int(time.time()))

        await interaction.followup.send(
            f"{self.config.emotes.success} The note on {noted.mention} has been successfully created."
        )

    @notes.subcommand(description="Used to get a note by its ID")
    async def by_id(
        self,
        interaction: nextcord.Interaction,
        note_id: str = nextcord.SlashOption(
            name="note_id",
            description="Note ID",
            min_length=22,
            max_length=22,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        sersi_note = get_note_by_id(self.config, note_id)

        note_embed = create_note_embed(sersi_note, interaction)

        await interaction.followup.send(embed=note_embed)

    @by_id.on_autocomplete("note_id")
    async def notes_by_id(self, interaction: nextcord.Interaction, note: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        notes = fetch_notes_by_partial_id(self.config, note)
        await interaction.response.send_autocomplete(notes)

    @notes.subcommand(description="Used to get a note by its user")
    async def by_user(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption,
        page: int = nextcord.SlashOption(
            name="page",
            description="The page you want to view",
            min_value=1,
            default=1,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        note_embed = SersiEmbed(title=f"{user.name}'s Notes")
        note_embed.set_thumbnail(user.display_avatar.url)

        view = PageView(
            config=self.config,
            base_embed=note_embed,
            fetch_function=get_note_by_user,
            author=interaction.user,
            entry_form=format_entry,
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            user_id=str(user.id),
        )

        await view.send_followup(interaction)


def setup(bot, **kwargs):
    bot.add_cog(Notes(bot, kwargs["config"]))
