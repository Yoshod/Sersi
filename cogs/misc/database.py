import sqlite3
import yaml

import nextcord
from nextcord.ext import commands
from sqlalchemy.sql import text

from utils.database import (
    db_session,
    Case,
    CaseAudit,
    CaseApproval,
    ScrubbedCase,
    PeerReview,
    Offence,
    Note,
    NoteEdits,
    TicketCategory,
    Slur,
    Goodword,
    create_db_tables,
    BlacklistCase,
    StaffBlacklist,
)
from utils.config import Configuration
from utils.perms import is_sersi_contributor, permcheck
from utils.sersi_embed import SersiEmbed


class Database(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Used to create the Sersi Database",
    )
    async def database(self, interaction):
        pass

    @database.subcommand(
        description="Used to create the Sersi Database",
    )
    async def create(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        await interaction.response.defer(ephemeral=True)

        create_db_tables()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to populate the category tables",
    )
    async def import_ticket_categories(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        await interaction.response.defer(ephemeral=True)

        with open("files/import/ticket_categories.yaml", "r") as f:
            categories = yaml.safe_load(f)
        with db_session(interaction.user) as session:
            for category in categories:
                for subcategory in category["subcategories"]:
                    session.merge(
                        TicketCategory(
                            category=category["category"],
                            subcategory=subcategory,
                        )
                    )
            session.commit()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to populate the offences table",
    )
    async def import_offences(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        await interaction.response.defer(ephemeral=True)

        with open("files/import/offences.yaml", "r") as f:
            offences = yaml.safe_load(f)
        with db_session(interaction.user) as session:
            for offence in offences:
                session.merge(
                    Offence(
                        offence=offence["offence"],
                        detail=offence["detail"],
                        warn_severity=offence["severity"],
                        punishments="|".join(offence["punishments"]),
                    )
                )
            session.commit()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")
    
    @database.subcommand(
        description="Migrates staff blacklist to Blacklist cases",
    )
    async def migrate_staff_blacklist(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session(interaction.user) as session:
            for blacklist in session.query(StaffBlacklist).all():
                session.add(
                    BlacklistCase(
                        offender=blacklist.blacklisted_user,
                        moderator=blacklist.staff_member,
                        blacklist="Staff",
                        reason=blacklist.reason,
                        created_at=blacklist.timestamp,
                    )
                )
            session.commit()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to drop a table from the Sersi Database",
    )
    async def drop(
        self,
        interaction: nextcord.Interaction,
        table_name: str = nextcord.SlashOption(
            name="table", description="The table you are dropping"
        ),
    ):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        if not self.config.bot.dev_mode:
            await interaction.response.send_message(
                "This command is not allowed on live Sersi!",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect("persistent_data/sersi.db")
        cursor = conn.cursor()

        try:
            cursor.execute(f"DROP TABLE {table_name}")
            conn.commit()
            await interaction.followup.send(
                f"{self.config.emotes.success}The table '{table_name}' has been dropped."
            )
        except sqlite3.Error as error_code:
            await interaction.followup.send(
                f"{self.config.emotes.fail}An error occurred: {error_code}"
            )
        finally:
            cursor.close()
            conn.close()

    @database.subcommand(
        description="Execute a raw SQL query on the Sersi Database",
    )
    async def execute(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(
            name="query", description="The query you are executing"
        ),
    ):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        await interaction.response.defer(ephemeral=True)

        session = db_session(interaction.user)

        try:
            session.execute(text(query))
            session.commit()

            await interaction.followup.send(
                f"{self.config.emotes.success}The query has been executed."
            )

            # logging
            await interaction.guild.get_channel(self.config.channels.logging).send(
                embed=SersiEmbed(
                    title="SQL Query Executed",
                    fields={
                        "Query:": query,
                        "User:": f"{interaction.user} ({interaction.user.id})",
                    },
                    footer="Sersi Database",
                ).set_author(
                    name=interaction.user.display_name,
                    icon_url=interaction.user.avatar.url,
                )
            )

        except sqlite3.Error as error_code:
            session.rollback()
            await interaction.followup.send(
                f"{self.config.emotes.fail}An error occurred: {error_code}"
            )
        finally:
            session.close()

    @database.subcommand()
    async def cleanup(self, interaction: nextcord.Interaction):
        pass

    @cleanup.subcommand(
        description="Deletes orphaned records that should have been cascade deleted"
    )
    async def prune_orphans(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session(interaction.user) as session:
            goodwords = (
                session.query(Goodword)
                .filter(Goodword.slur.not_in(session.query(Slur.slur)))
                .delete()
            )

            case_logs = (
                session.query(CaseAudit)
                .filter(CaseAudit.case_id.not_in(session.query(Case.id)))
                .delete()
            )

            case_approvals = (
                session.query(CaseApproval)
                .filter(CaseApproval.case_id.not_in(session.query(Case.id)))
                .delete()
            )

            scrubbed_cases = (
                session.query(ScrubbedCase)
                .filter(ScrubbedCase.case_id.not_in(session.query(Case.id)))
                .delete()
            )

            peer_reviews = (
                session.query(PeerReview)
                .filter(PeerReview.case_id.not_in(session.query(Case.id)))
                .delete()
            )

            note_edits = (
                session.query(NoteEdits)
                .filter(NoteEdits.note_id.not_in(session.query(Note.id)))
                .delete()
            )

            session.commit()

        total = (
            goodwords
            + case_logs
            + case_approvals
            + scrubbed_cases
            + peer_reviews
            + note_edits
        )

        if total == 0:
            await interaction.followup.send(
                f"{self.config.emotes.success} No orphaned records found."
            )
            return

        log = [
            f"- {goodwords:3} Goodwords" if goodwords else None,
            f"- {case_logs:3} Case Logs" if case_logs else None,
            f"- {case_approvals:3} Case Approvals" if case_approvals else None,
            f"- {scrubbed_cases:3} Scrubbed Cases" if scrubbed_cases else None,
            f"- {peer_reviews:3} Peer Reviews" if peer_reviews else None,
            f"- {note_edits:3} Note Edits" if note_edits else None,
        ]

        await interaction.followup.send(
            f"{self.config.emotes.success} Pruned {total} orphaned records from the database:\n"
            + "\n".join([line for line in log if line])
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Database(bot, kwargs["config"]))
