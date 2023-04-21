import nextcord
from nextcord.ext import commands

from baseutils import SersiEmbed, PageView
from caseutils import (
    get_case_by_id,
    fetch_cases_by_partial_id,
    create_slur_case_embed,
    create_reformation_case_embed,
    create_probation_case_embed,
    create_bad_faith_ping_case_embed,
    fetch_offender_cases,
    fetch_moderator_cases,
    scrub_case,
    fetch_all_cases,
    delete_case,
    create_scrubbed_case_embed,
)
from configutils import Configuration
from permutils import permcheck, is_mod, is_senior_mod, is_dark_mod


class Cases(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to get a case",
    )
    async def get_case(self, interaction: nextcord.Interaction):
        pass

    @get_case.subcommand(description="Used to display all cases")
    async def all_cases(
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
            choices={
                "Slur Usage": "slur_cases",
                "Probation": "probation_cases",
                "Reformation": "reformation_cases",
                "Bad Faith Ping": "bad_faith_ping_cases",
                "Scrubbed Cases": "scrubbed_cases",
            },
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
            entry_form="{entry[1]} <t:{entry[2]}:R>",
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            case_type=case_type,
        )

        await view.send_followup(interaction)

    @get_case.subcommand(description="Used to get a case by its ID")
    async def by_id(
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

        sersi_case = get_case_by_id(self.config, case_id, scrubbed)

        if scrubbed:
            case_embed = create_scrubbed_case_embed(sersi_case, interaction)
            await interaction.followup.send(embed=case_embed)
            return

        match (sersi_case["Case Type"]):
            case "Slur Usage":
                case_embed = create_slur_case_embed(sersi_case, interaction)

            case "Reformation":
                case_embed = create_reformation_case_embed(sersi_case, interaction)

            case "Probation":
                case_embed = create_probation_case_embed(sersi_case, interaction)

            case "Bad Faith Ping":
                case_embed = create_bad_faith_ping_case_embed(sersi_case, interaction)

        await interaction.followup.send(embed=case_embed)

    @get_case.subcommand(description="Used to get a case by Offender")
    async def by_offender(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The user whos cases you are looking for",
        ),
        case_type: str = nextcord.SlashOption(
            name="case_type",
            description="The specific case type you are looking for",
            required=False,
            choices={
                "Slur Usage": "slur_cases",
                "Probation": "probation_cases",
                "Reformation": "reformation_cases",
                "Bad Faith Ping": "bad_faith_ping_cases",
                "Scrubbed Cases": "scrubbed_cases",
            },
        ),
        page: int = nextcord.SlashOption(
            name="page",
            description="The page you want to view",
            min_value=1,
            default=1,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            interaction.response.send_message(
                f"{self.config.emotes.fail} You do not have permission to run this command."
            )
            return

        if case_type == "scrubbed_cases" and not await permcheck(
            interaction, is_senior_mod
        ):
            return

        await interaction.response.defer(ephemeral=False)

        cases_embed = SersiEmbed(title=f"{offender.name}'s Cases")
        cases_embed.set_thumbnail(offender.display_avatar.url)

        view = PageView(
            config=self.config,
            base_embed=cases_embed,
            fetch_function=fetch_offender_cases,
            author=interaction.user,
            entry_form="{entry[1]} <t:{entry[2]}:R>",
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            offender=offender,
            case_type=case_type,
        )

        await view.send_followup(interaction)

    @get_case.subcommand(description="Used to get a case by Moderator")
    async def by_moderator(
        self,
        interaction: nextcord.Interaction,
        moderator: nextcord.Member = nextcord.SlashOption(
            name="moderator",
            description="The user whos cases you are looking for",
        ),
        case_type: str = nextcord.SlashOption(
            name="case_type",
            description="The specific case type you are looking for",
            required=False,
            choices={
                "Slur Usage": "slur_cases",
                "Probation": "probation_cases",
                "Reformation": "reformation_cases",
                "Bad Faith Ping": "bad_faith_ping_cases",
                "Scrubbed Cases": "scrubbed_cases",
            },
        ),
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

        if case_type == "scrubbed_cases" and not await permcheck(
            interaction, is_senior_mod
        ):
            return

        await interaction.response.defer(ephemeral=False)

        cases_embed = SersiEmbed(title=f"{moderator.name}'s Cases")
        cases_embed.set_thumbnail(moderator.display_avatar.url)

        view = PageView(
            config=self.config,
            base_embed=cases_embed,
            fetch_function=fetch_moderator_cases,
            author=interaction.user,
            entry_form="{entry[1]} <t:{entry[2]}:R>",
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            moderator=moderator,
            case_type=case_type,
        )

        await view.send_followup(interaction)

    @get_case.subcommand(description="Used to scrub a Sersi Case")
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

        outcome = scrub_case(
            self.config,
            case_id,
            interaction.user,
            reason,
        )

        if outcome:
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

        else:
            logging_embed = SersiEmbed(
                name="Case Scrub Attempted",
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
                f"{self.config.emotes.fail} Case {case_id} has not been scrubbed. Please contact Sèitheach."
            )

    @get_case.subcommand(description="Used to delete a scrubbed Sersi Case")
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

        outcome = delete_case(self.config, case_id)

        if outcome:
            await interaction.followup.send(
                f"{self.config.emotes.success} Case {case_id} successfully deleted."
            )
            logging_embed = SersiEmbed(
                name="Case Deleted",
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

            logging_channel.send(embed=logging_embed)

        else:
            await interaction.followup.send(
                f"{self.config.emotes.fail} Case {case_id} has not been deleted."
            )
            logging_embed = SersiEmbed(
                name="Case Deletion Attempted",
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

            logging_channel.send(embed=logging_embed)

    @by_id.on_autocomplete("case_id")
    @scrub.on_autocomplete("case_id")
    async def cases_by_id(self, interaction: nextcord.Interaction, case: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        cases = fetch_cases_by_partial_id(self.config, case)
        await interaction.response.send_autocomplete(cases)


def setup(bot, **kwargs):
    bot.add_cog(Cases(bot, kwargs["config"]))
