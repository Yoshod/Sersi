import asyncio
import datetime
from nextcord.ext import commands, tasks
import nextcord

from utils.config import Configuration
from utils.compliance import (
    get_moderation_report,
    get_moderation_report_embed,
    ModerationReport,
)

from utils.perms import permcheck, is_admin, is_compliance


class Compliance(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        if self.bot.is_ready():
            self.compliance_report_loop.start()

    def cog_unload(self):
        self.compliance_report_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        await asyncio.sleep(5)
        self.compliance_report_loop.start()

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Moderation report.",
    )
    async def moderation_report(self, interaction: nextcord.Interaction):
        pass

    @moderation_report.subcommand()
    async def create(self, interaction: nextcord.Interaction):
        pass

    @create.subcommand(description="Create a moderation report by date.")
    async def custom(
        self,
        interaction: nextcord.Interaction,
        start_day: int = nextcord.SlashOption(
            description="The day the report starts on."
        ),
        start_month: int = nextcord.SlashOption(
            description="The month the report starts on."
        ),
        start_year: int = nextcord.SlashOption(
            description="The year the report starts on."
        ),
        end_day: int = nextcord.SlashOption(description="The day the report ends on."),
        end_month: int = nextcord.SlashOption(
            description="The month the report ends on."
        ),
        end_year: int = nextcord.SlashOption(
            description="The year the report ends on."
        ),
    ):
        if not await permcheck(interaction, is_admin) or not await permcheck(
            interaction, is_compliance
        ):
            return

        try:
            start_date = datetime.datetime(start_year, start_month, start_day, 0, 0, 0)

        except ValueError:
            await interaction.send(
                f"{self.config.emotes.fail} The start date is invalid!",
                ephemeral=True,
            )
            return

        try:
            end_date = datetime.datetime(end_year, end_month, end_day, 0, 0, 0)

        except ValueError:
            await interaction.send(
                f"{self.config.emotes.fail} The end date is invalid!",
                ephemeral=True,
            )
            return

        if start_date > end_date:
            await interaction.send(
                f"{self.config.emotes.fail} The start date cannot be after the end date!",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        report: ModerationReport = await get_moderation_report(start_date, end_date)

        embed = get_moderation_report_embed(
            report, start_date, end_date, "Custom Moderation Report"
        )

        await interaction.followup.send(embed=embed)

    @create.subcommand(
        description="Create a compliance report using a predefined set of durations."
    )
    async def preset(
        self,
        interaction: nextcord.Interaction,
        preset: str = nextcord.SlashOption(
            description="The preset to use.",
            choices=[
                "Month to Date",
                "Quarter to Date",
                "Year to Date",
                "All Time",
            ],
        ),
    ):
        if not await permcheck(interaction, is_admin) or not await permcheck(
            interaction, is_compliance
        ):
            return

        await interaction.response.defer()

        match preset:
            case "Month to Date":
                start_date = datetime.datetime.today().replace(day=1)
                end_date = datetime.datetime.today()

            case "Quarter to Date":
                start_date = datetime.datetime.today().replace(
                    month=(datetime.datetime.today().month - 1) // 3 * 3 + 1, day=1
                )
                end_date = datetime.datetime.today()

            case "Year to Date":
                start_date = datetime.datetime.today().replace(month=1, day=1)
                end_date = datetime.datetime.today()

            case "All Time":
                start_date = datetime.datetime(2023, 1, 1)
                end_date = datetime.datetime.today()

        report: ModerationReport = await get_moderation_report(start_date, end_date)

        embed = get_moderation_report_embed(
            report, start_date, end_date, f"{preset} Moderation Report"
        )

        await interaction.followup.send(embed=embed)

    @tasks.loop(minutes=1)
    async def compliance_report_loop(self):
        if datetime.datetime.now().hour != 6:
            return

        start_date = datetime.datetime.today().replace(
            day=datetime.datetime.today().day - 1, hour=0, minute=0, second=0
        )
        end_date = datetime.datetime.today().replace(hour=0, minute=0, second=0)
        report: ModerationReport = await get_moderation_report(start_date, end_date)

        embed = get_moderation_report_embed(
            report, start_date, end_date, "Daily Moderation Report"
        )

        await self.bot.get_channel(self.config.channels.compliance_review).send(
            embed=embed
        )

        await self.bot.get_channel(self.config.channels.alert).send(embed=embed)

        if datetime.datetime.now().day == 1:
            if datetime.datetime.now().month == 1:
                start_date = datetime.datetime.now().replace(
                    year=datetime.datetime.now().year - 1,
                    month=12,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                )

                end_date = datetime.datetime.now().replace(
                    year=datetime.datetime.now().year - 1,
                    month=12,
                    day=31,
                    hour=0,
                    minute=0,
                    second=0,
                )

            else:
                start_date = datetime.datetime.now().replace(
                    month=datetime.datetime.now().month - 1,
                    day=1,
                    hour=0,
                    minute=0,
                    second=0,
                )

                now = datetime.datetime.now().replace(hour=0, minute=0, second=0)
                previous_month = now.month - 1 if now.month != 1 else 12

                match previous_month:
                    case 4 | 6 | 9 | 11:
                        day = 30
                    case 2:
                        day = (
                            29
                            if (now.year % 4 == 0 and now.year % 100 != 0)
                            or (now.year % 400 == 0)
                            else 28
                        )
                    case _:
                        day = 31

                end_date = now.replace(month=previous_month, day=day)

            report: ModerationReport = await get_moderation_report(start_date, end_date)

            embed = get_moderation_report_embed(
                report, start_date, end_date, "Monthly Moderation Report"
            )

            await self.bot.get_channel(self.config.channels.compliance_review).send(
                embed=embed
            )

            await self.bot.get_channel(self.config.channels.alert).send(embed=embed)

        if datetime.datetime.now().day == 1 and datetime.datetime.now().month == 1:
            start_date = datetime.datetime.now().replace(
                year=datetime.datetime.now().year - 1, month=1, day=1
            )

            end_date = datetime.datetime.now().replace(
                year=datetime.datetime.now().year - 1, month=12, day=31
            )

            report: ModerationReport = await get_moderation_report(start_date, end_date)

            embed = get_moderation_report_embed(
                report, start_date, end_date, "Yearly Moderation Report"
            )

            await self.bot.get_channel(self.config.channels.compliance_review).send(
                embed=embed
            )

            await self.bot.get_channel(self.config.channels.alert).send(embed=embed)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Compliance(bot, kwargs["config"]))
