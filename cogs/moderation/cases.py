import nextcord
from nextcord.ext import commands

from baseutils import PageView, SersiEmbed
from caseutils import get_case_by_id
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
    async def get_case(
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
                case_embed = SersiEmbed()
                case_embed.add_field(
                    name="Case:", value=f"`{sersi_case['ID']}`", inline=True
                )
                case_embed.add_field(name="Type:", value="`Slur Usage`", inline=True)

                moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

                if not moderator:
                    case_embed.add_field(
                        name="Moderator:",
                        value=f"`{sersi_case['Moderator ID']}`",
                        inline=True,
                    )

                else:
                    case_embed.add_field(
                        name="Moderator:", value=f"{moderator.mention}", inline=True
                    )

                offender = interaction.guild.get_member(sersi_case["Offender ID"])

                if not offender:
                    case_embed.add_field(
                        name="Offender:",
                        value=f"`{sersi_case['Offender ID']}`",
                        inline=True,
                    )

                else:
                    case_embed.add_field(
                        name="Offender:", value=f"{offender.mention}", inline=True
                    )
                    case_embed.set_thumbnail(url=offender.display_avatar.url)

                case_embed.add_field(
                    name="Slur Used:", value=sersi_case["Slur Used"], inline=False
                )

                case_embed.add_field(
                    name="Report URL:", value=sersi_case["Report URL"], inline=False
                )

                case_embed.add_field(
                    name="Timestamp:",
                    value=(f"<t:{sersi_case['Timestamp']}:R>"),
                    inline=True,
                )

                case_embed.set_footer(text="Sersi Case Tracking")

        await interaction.followup.send(embed=case_embed)


def setup(bot, **kwargs):
    bot.add_cog(Cases(bot, kwargs["config"]))
