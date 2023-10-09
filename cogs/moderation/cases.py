from nextcord.ext import commands
import nextcord

from utils.base import PageView
from utils.cases import fetch_cases_by_partial_id
from utils.cases import create_case_embed
from utils.cases import (
    fetch_all_cases,
    get_case_by_id,
)
from utils.config import Configuration
from utils.database import db_session, Case, ScrubbedCase, Offence
from utils.perms import permcheck, is_mod, is_senior_mod, is_dark_mod
from utils.sersi_embed import SersiEmbed


class Cases(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to get a case",
    )
    async def cases(self, interaction: nextcord.Interaction):
        pass

    @cases.subcommand(description="Used to display all cases")
    async def list(
        self,
        interaction: nextcord.Interaction,
        page: int = nextcord.SlashOption(
            name="page",
            description="The page you want to view",
            min_value=1,
            default=1,
            required=False,
        ),
        case_type: str = nextcord.SlashOption(
            name="case_type",
            description="The specific case type you are looking for",
            required=False,
            choices=[
                "Ban",
                "Bad Faith Ping",
                "Kick",
                "Probation",
                "Reformation",
                "Slur Usage",
                "Timeout",
                "Warn",
            ],
        ),
        moderator: nextcord.Member = nextcord.SlashOption(
            name="moderator",
            description="The moderator whos cases you are looking for",
            required=False,
        ),
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The offender whos cases you are looking for",
            required=False,
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence you are looking for",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if case_type == "scrubbed_cases" and not await permcheck(
            interaction, is_senior_mod
        ):
            return

        await interaction.response.defer(ephemeral=False)

        cases_embed = SersiEmbed(title=f"{interaction.guild.name} Cases")
        cases_embed.set_thumbnail(interaction.guild.icon.url)

        view = PageView(
            config=self.config,
            base_embed=cases_embed,
            fetch_function=fetch_all_cases,
            author=interaction.user,
            entry_form="{entry}",
            field_title="{entries[0].id}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            case_type=case_type,
            moderator_id=moderator.id if moderator else None,
            offender_id=offender.id if offender else None,
            offence=offence,
        )

        await view.send_followup(interaction)

    @cases.subcommand(description="Used to get a case by its ID")
    async def detail(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=22,
            max_length=22,
        ),
        scrubbed: bool = nextcord.SlashOption(
            name="scrubbed",
            description="Specify if you're looking for a scrubbed case",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        sersi_case = get_case_by_id(case_id)

        await interaction.followup.send(
            embed=create_case_embed(sersi_case, interaction, self.config)
        )

    @cases.subcommand(description="Used to scrub a Sersi Case")
    async def scrub(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=22,
            max_length=22,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason you are scrubbing the case",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return

        await interaction.response.defer(ephemeral=False)

        with db_session(interaction.user) as session:
            case: Case = session.query(Case).filter(Case.id == case_id).first()

            if not case:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} Case {case_id} does not exist."
                )
                return
            
            if case.scrubbed:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} Case {case_id} has already been scrubbed."
                )
                return
            
            case.scrubbed = True
            session.add(
                ScrubbedCase(
                    case_id=case_id,
                    scrubber=interaction.user.id,
                    reason=reason
                )
            )

        logging_embed = SersiEmbed(
            title="Case Scrubbed",
        )

        logging_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
        logging_embed.add_field(
            name="Senior Moderator",
            value=f"{interaction.user.mention}",
            inline=True,
        )
        logging_embed.add_field(name="Reason", value=f"`{reason}`", inline=False)

        logging_embed.set_thumbnail(interaction.user.display_avatar.url)

        logging_channel = interaction.guild.get_channel(
            self.config.channels.logging
        )

        await logging_channel.send(embed=logging_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} Case {case_id} successfully scrubbed."
        )


    @cases.subcommand(description="Used to delete a scrubbed Sersi Case")
    async def delete(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=22,
            max_length=22,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason you are deleting the case",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=False)

        with db_session() as session:
            case: Case = session.query(Case).filter(Case.id == case_id).first()

            session.delete(case)
            session.commit()

        if case:
            logging_embed = SersiEmbed(
                title="Case Deleted",
            )

            logging_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
            logging_embed.add_field(
                name="Mega Administrator",
                value=f"{interaction.user.mention}",
                inline=True,
            )
            logging_embed.add_field(name="Reason", value=f"`{reason}`", inline=False)

            logging_embed.set_thumbnail(interaction.user.display_avatar.url)

            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )

            await logging_channel.send(embed=logging_embed)

            await interaction.followup.send(
                f"{self.config.emotes.success} Case {case_id} successfully deleted."
            )

        else:
            logging_embed = SersiEmbed(
                title="Case Deletion Attempted",
            )

            logging_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
            logging_embed.add_field(
                name="Mega Administrator",
                value=f"{interaction.user.mention}",
                inline=True,
            )
            logging_embed.add_field(name="Reason", value=f"`{reason}`", inline=False)

            logging_embed.set_thumbnail(interaction.user.display_avatar.url)

            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )

            await logging_channel.send(embed=logging_embed)

            await interaction.followup.send(
                f"{self.config.emotes.fail} Case {case_id} has not been deleted."
            )

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to do stuff with offences",
    )
    async def offence(self, interaction: nextcord.Interaction):
        pass

    @offence.subcommand(description="Used to add a new offence")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offence_name: str = nextcord.SlashOption(
            name="offence",
            description="The name of the new offence",
            min_length=4,
            max_length=64,
        ),
        offence_description: str = nextcord.SlashOption(
            name="description",
            description="A description of the new offence",
            min_length=32,
            max_length=1024,
        ),
        offence_severity: str = nextcord.SlashOption(
            name="severity",
            description="The severity of the new offence",
            min_value=1,
            max_value=5,
            required=False,
        ),
        offence_group: str = nextcord.SlashOption(
            name="group",
            description="The group of the new offence",
            min_length=4,
            max_length=64,
            required=False,
        ),
        first_punishment: str = nextcord.SlashOption(
            name="first_punishment",
            description="This is the punishment for the first instance of the offence",
            choices={
                "Informal Warning": "Informal Warning",
                "Warning": "Warning",
                "Reformation": "Reformation Centre",
                "Temporary Ban": "Temporary Ban",
                "Priority Ban": "Priority Ban",
                "Emergency Ban": "Emergency Ban",
                "Emergency Ban & Trust and Safety": "Emergency Ban & TnS Report",
            },
            required=False,
        ),
        second_punishment: str = nextcord.SlashOption(
            name="second_punishment",
            description="This is the punishment for the second instance of the offence",
            choices={
                "Informal Warning": "Informal Warning",
                "Warning": "Warning",
                "Reformation": "Reformation Centre",
                "Temporary Ban": "Temporary Ban",
                "Priority Ban": "Priority Ban",
                "Emergency Ban": "Emergency Ban",
                "Emergency Ban & Trust and Safety": "Emergency Ban & TnS Report",
            },
            required=False,
        ),
        third_punishment: str = nextcord.SlashOption(
            name="third_punishment",
            description="This is the punishment for the third instance of the offence",
            choices={
                "Informal Warning": "Informal Warning",
                "Warning": "Warning",
                "Reformation": "Reformation Centre",
                "Temporary Ban": "Temporary Ban",
                "Priority Ban": "Priority Ban",
                "Emergency Ban": "Emergency Ban",
                "Emergency Ban & Trust and Safety": "Emergency Ban & TnS Report",
            },
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return

        await interaction.response.defer(ephemeral=False)

        punishments = [first_punishment, second_punishment, third_punishment]

        with db_session(interaction.user) as session:
            session.add(
                Offence(
                    offence=offence_name,
                    detail=offence_description,
                    warn_severity=offence_severity,
                    group=offence_group,
                    punishments="|".join([p for p in punishments if p]),
                )
            )

        offence_added_log = SersiEmbed(
            title="New Offence Added",
            fields={
                "Offence": f"`{offence_name}`",
                "Description": f"`{offence_description}`",
                "First Instance": f"`{first_punishment}`",
                "Second Instance": f"`{second_punishment}`",
                "Third Instance": f"`{third_punishment}`",
            },
        )
        offence_added_log.set_footer(text="Sersi Offences")

        logging_channel: nextcord.TextChannel = interaction.guild.get_channel(
            self.config.channels.logging
        )

        await logging_channel.send(embed=offence_added_log)

        await interaction.followup.send(embed=offence_added_log)

    @detail.on_autocomplete("case_id")
    @scrub.on_autocomplete("case_id")
    async def cases_by_id(self, interaction: nextcord.Interaction, case: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        cases = fetch_cases_by_partial_id(case)
        await interaction.response.send_autocomplete(cases)


def setup(bot, **kwargs):
    bot.add_cog(Cases(bot, kwargs["config"]))
