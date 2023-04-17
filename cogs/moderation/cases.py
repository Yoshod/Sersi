import nextcord
from nextcord.ext import commands

from baseutils import PageView
from caseutils import (
    get_case_by_id,
    create_slur_case_embed,
    create_reformation_case_embed,
    create_probation_case_embed,
    create_bad_faith_ping_case_embed,
)
from configutils import Configuration
from permutils import permcheck, is_mod


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
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        sersi_case = get_case_by_id(self.config, case_id)

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
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)


def setup(bot, **kwargs):
    bot.add_cog(Cases(bot, kwargs["config"]))
