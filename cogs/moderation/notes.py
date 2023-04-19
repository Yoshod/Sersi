import nextcord
import time
from nextcord.ext import commands

from baseutils import SersiEmbed, PageView
from noteutils import (
    create_note,
    get_note_by_id,
    fetch_notes_by_partial_id,
    create_note_embed,
)
from configutils import Configuration
from permutils import permcheck, is_mod, is_senior_mod


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


def setup(bot, **kwargs):
    bot.add_cog(Notes(bot, kwargs["config"]))
