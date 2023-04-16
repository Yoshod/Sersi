import nextcord
import sqlite3
from nextcord.ext import commands
from configutils import Configuration
from permutils import is_dark_mod, permcheck


class Database(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to create the Sersi Database",
    )
    async def database_create(self, interaction: nextcord.Interaction):
        conn = sqlite3.connect(self.config.datafiles.sersi_db)
        cursor = conn.cursor()

        if not await permcheck(interaction, is_dark_mod):
            return

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS cases
                  (id INTEGER PRIMARY KEY,
                   type TEXT,
                   offender INTEGER,
                   moderator INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "slur cases"
                  (id INTEGER PRIMARY KEY,
                   slur_used TEXT,
                   offender INTEGER,
                   report_url TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "bad faith ping cases"
                  (id INTEGER PRIMARY KEY,
                   offender INTEGER,
                   report_url TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "probation cases"
                  (id INTEGER PRIMARY KEY,
                   offender INTEGER,
                   initial_moderator INTEGER,
                   approving_moderator INTEGER,
                   reason TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "reformation cases"
                  (id INTEGER PRIMARY KEY,
                   case_number INTEGER,
                   offender INTEGER,
                   moderator INTEGER,
                   cell_id INTEGER,
                   reason TEXT)"""
        )


def setup(bot, **kwargs):
    bot.add_cog(Database(bot, kwargs["config"]))
