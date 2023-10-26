import io
import sqlite3

import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.perms import is_sersi_contributor, permcheck


class DBExport(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
        description="Exports the DB into an SQL Script",
    )
    async def export(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return
        await interaction.response.defer(ephemeral=True)

        buffer = io.StringIO()
        con = sqlite3.connect(self.config.datafiles.sersi_db)

        for line in con.iterdump():
            buffer.write("%s\n" % line)

        buffer.seek(0)

        await interaction.followup.send(file=nextcord.File(buffer, "dump.sql"))


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(DBExport(bot, kwargs["config"]))
