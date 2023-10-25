import sqlite3
import pickle
import yaml
from datetime import datetime

import nextcord
from nextcord.ext import commands

from utils.database import (
    db_session,
    BadFaithPingCase,
    ProbationCase,
    ReformationCase,
    SlurUsageCase,
    CaseApproval,
    Offence,
    TicketCategory,
    Slur,
    Goodword,
    create_db_tables,
)
from utils.config import Configuration
from utils.perms import is_dark_mod, permcheck
from slurdetector import leet


class Database(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[Configuration.guilds.main, Configuration.guilds.errors],
        description="Used to create the Sersi Database",
    )
    async def database(self, interaction):
        pass

    @database.subcommand(
        description="Used to create the Sersi Database",
    )
    async def create(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        create_db_tables()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to populate the category tables",
    )
    async def import_ticket_categories(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
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

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to populate the offences table",
    )
    async def import_offences(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
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
        description="Used to migrate case data",
    )
    async def case_migration(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        # Load the first pickle file containing the case data
        with open(self.config.datafiles.casehistory, "rb") as f:
            cases_dict = pickle.load(f)

        # Load the second pickle file containing the case details
        with open(self.config.datafiles.casedetails, "rb") as f:
            details_dict = pickle.load(f)

        with db_session() as session:
            for __, case_list in cases_dict.items():
                for case in case_list:
                    case_id, case_type, timestamp = case
                    # Ignore Anonymous Message Mute cases
                    if case_type == "Anonymous Message Mute":
                        continue
                    # Process the case details
                    if case_id in details_dict:
                        details_list = details_dict[case_id]
                        case_type = details_list[0]
                        if case_type == "Bad Faith Ping":
                            (
                                report_url,
                                offender_id,
                                moderator_id,
                                timestamp,
                            ) = details_list[1:]
                            session.add(
                                BadFaithPingCase(
                                    id=case_id[0:10],
                                    report_url=report_url,
                                    offender=offender_id,
                                    moderator=moderator_id,
                                    created=datetime.fromtimestamp(timestamp),
                                )
                            )
                        elif case_type == "Probation":
                            (
                                offender_id,
                                primary_moderator_id,
                                secondary_moderator_id,
                                reason,
                                timestamp,
                            ) = details_list[1:]
                            session.add(
                                ProbationCase(
                                    id=case_id[0:10],
                                    offender=offender_id,
                                    moderator=primary_moderator_id,
                                    reason=reason,
                                    created=datetime.fromtimestamp(timestamp),
                                )
                            )
                            if secondary_moderator_id:
                                session.add(
                                    CaseApproval(
                                        case_id=case_id[0:10],
                                        action="Add",
                                        approval_type="Dual Custody",
                                        approver=secondary_moderator_id,
                                    )
                                )
                        elif case_type == "Reformation":
                            (
                                case_number,
                                offender_id,
                                moderator_id,
                                channel_id,
                                reason,
                                timestamp,
                            ) = details_list[1:]
                            session.add(
                                ReformationCase(
                                    id=case_id[0:10],
                                    case_number=case_number,
                                    offender=offender_id,
                                    moderator=moderator_id,
                                    cell_channel=channel_id,
                                    details=reason,
                                    created=datetime.fromtimestamp(timestamp),
                                )
                            )
                        elif case_type == "Slur Usage":
                            (
                                slur_used,
                                report_url,
                                offender_id,
                                moderator_id,
                                timestamp,
                            ) = details_list[1:]
                            session.add(
                                SlurUsageCase(
                                    id=case_id[0:10],
                                    slur_used=slur_used,
                                    report_url=report_url,
                                    offender=offender_id,
                                    moderator=moderator_id,
                                    created=datetime.fromtimestamp(timestamp),
                                )
                            )

            session.commit()

        await interaction.followup.send(f"{self.config.emotes.success} Complete")

    @database.subcommand(
        description="Used to migrate the slur detection stuff",
    )
    async def migrate_slur_detection(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        with open(self.config.datafiles.slurfile, "r") as f:
            slur_list = [slur.replace("\n", "") for slur in f]

        with open(self.config.datafiles.goodwordfile, "r") as f:
            goodword_list = [goodword.replace("\n", "") for goodword in f]

        with db_session() as session:
            for slur in slur_list:
                session.merge(
                    Slur(
                        slur=slur,
                        added_by=interaction.user.id,
                    )
                )

            for goodword in goodword_list:
                matched_slur = None
                for slur in slur_list:
                    for leet_slur in leet(slur):
                        if leet_slur in goodword:
                            matched_slur = slur
                            break

                session.merge(
                    Goodword(
                        goodword=goodword,
                        slur=matched_slur,
                        added_by=interaction.user.id,
                    )
                )

            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Complete, imported {len(slur_list)} slurs and {len(goodword_list)} goodwords"
        )

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
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect(self.config.datafiles.sersi_db)
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


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Database(bot, kwargs["config"]))
