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
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect(self.config.datafiles.sersi_db)
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS cases
                  (id TEXT PRIMARY KEY,
                   type TEXT,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS slur_cases
                  (id TEXT PRIMARY KEY,
                   slur_used TEXT,
                   report_url TEXT,
                   offender INTEGER,
                   moderator INTEGER,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS "bad_faith_ping_cases"
                  (id TEXT PRIMARY KEY,
                   report_url TEXT,
                   offender INTEGER,
                   moderator INTEGER,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS probation_cases
                  (id TEXT PRIMARY KEY,
                   offender INTEGER,
                   initial_moderator INTEGER,
                   approving_moderator INTEGER,
                   reason TEXT,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS reformation_cases
                  (id TEXT PRIMARY KEY,
                   case_number INTEGER,
                   offender INTEGER,
                   moderator INTEGER,
                   cell_id INTEGER,
                   reason TEXT,
                   timestamp INTEGER)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS tickets
                (ticket_id TEXT PRIMARY KEY,
                ticket_escalation_initial TEXT,
                ticket_escalation_final TEXT,
                ticket_channel_id INTEGER,
                ticket_creator_id INTEGER,
                ticket_active BOOLEAN,
                ticket_closer_id INTEGER,
                timestamp_opened INTEGER,
                timestamp_closed INTEGER,
                priority_initial TEXT,
                priority_final TEXT,
                main_category TEXT,
                sub_category TEXT,
                related_tickets TEXT
                survey_sent BOOLEAN
                survey_score INTEGER
                survery_response TEXT)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS ticket_categories
            (category TEXT PRIMARY KEY)"""
        )

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS ticket_subcategories
            (category TEXT,
            subcategory TEXT)"""
        )

        conn.commit()

        conn.close()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")


def setup(bot, **kwargs):
    bot.add_cog(Database(bot, kwargs["config"]))
