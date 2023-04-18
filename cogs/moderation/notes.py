import nextcord
import time
from nextcord.ext import commands

from baseutils import SersiEmbed, PageView
from noteutils import (
    get_note_by_id,
    fetch_notes_by_partial_id,
    create_note_embed,
    fetch_noted_notes,
    fetch_noter_notes,
    delete_note,
    fetch_all_notes,
    delete_all_notes,
    create_note,
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
    async def note(self, interaction: nextcord.Interaction):
        pass

    @note.subcommand(description="Add a note to a user")
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


def setup(bot, **kwargs):
    bot.add_cog(Notes(bot, kwargs["config"]))
