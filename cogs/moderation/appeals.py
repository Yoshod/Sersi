import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.database import db_session, BanCase, TimeoutCase
from utils.sersi_embed import SersiEmbed
from utils.dialog import confirm
from utils.base import encode_button_id, decode_button_id
from utils.appeals import AppealsSubmitView, AppealReceivedView, AppealOngoingView


class AppealsModal(nextcord.ui.Modal):
    def __init__(
        self,
        config: Configuration,
        appeal_type: str,
        appeal_reason: str,
        bot: commands.Bot,
    ):
        super().__init__(f"{appeal_type} Appeal")
        self.config = config
        self.appeal_type = appeal_type
        self.appeal_reason = appeal_reason
        self.bot = bot

        if self.appeal_reason == "unjust":
            self.why = nextcord.ui.TextInput(
                label="Why was your punishment was overly harsh?",
                min_length=10,
                max_length=1024,
                required=True,
                style=nextcord.TextInputStyle.paragraph,
            )
            self.add_item(self.why)

        elif self.appeal_reason == "no_rule_broken":
            self.why = nextcord.ui.TextInput(
                label="Why do you think you did not break any rules?",
                min_length=10,
                max_length=1024,
                required=True,
                style=nextcord.TextInputStyle.paragraph,
            )
            self.add_item(self.why)

        else:
            raise ValueError("Invalid appeal reason provided.")

    async def callback(self, interaction: nextcord.Interaction):
        """Run whenever the 'submit' button is pressed."""
        if not await confirm(
            interaction, "Are you sure you want to submit this appeal?"
        ):
            return

        await interaction.response.defer(ephemeral=True)

        appeal = self.why.value

        if self.appeal_type == "Ban":
            with db_session() as session:
                case = (
                    session.query(BanCase)
                    .filter(
                        BanCase.offender == interaction.user.id, BanCase.active is True
                    )
                    .order_by(BanCase.created.desc())
                    .first()
                )

            if case is None:
                await interaction.followup.send(
                    "You do not have an active ban case.", ephemeral=True
                )
                return

        elif self.appeal_type == "Timeout":
            with db_session() as session:
                case = (
                    session.query(TimeoutCase)
                    .filter(
                        TimeoutCase.offender == interaction.user.id,
                    )
                    .order_by(TimeoutCase.created.desc())
                    .first()
                )

            if case is None:
                await interaction.followup.send(
                    "You do not have an active timeout case.", ephemeral=True
                )
                return

        appeal_embed = SersiEmbed(
            title=f"{self.appeal_type} Appeal Submitted",
            description="A user has submitted an appeal. Please review the information below and take appropriate action. You can discuss this appeal with the appellant by pressing the DM Appellant button.",
            footer="Sersi Appeals",
        )
        appeal_embed.add_field(
            name="User",
            value=f"{interaction.user.display_name} ({interaction.user.id})",
            inline=False,
        )

        moderator: nextcord.User = await self.bot.get_user(case.moderator)

        appeal_embed.add_field(name="Offence", value=case.offence, inline=False)
        appeal_embed.add_field(name="Detail", value=case.details, inline=True)

        if not moderator:
            appeal_embed.add_field(name="Moderator", value="Unknown", inline=True)
        else:
            appeal_embed.add_field(
                name="Moderator",
                value=f"{moderator.mention} ({moderator.id})",
                inline=True,
            )

        appeal_embed.add_field(name="Case ID", value=f"`{case.id}`", inline=False)
        appeal_embed.add_field(
            name="Case Created",
            value=f"{case.created} ({nextcord.utils.format_dt(case.created, 'R')})",
            inline=True,
        )

        appeal_embed.add_field(name="Appeal Reason", value=appeal, inline=False)

        view = AppealReceivedView(case.id, case.offender)

        message = await self.bot.get_channel(self.config.channels.staff.appeals).send(
            embed=appeal_embed, view=view
        )

        thread = await message.create_thread(
            name=f"appeal-{case.id}", auto_archive_duration=7
        )

        await interaction.user.send(
            embed=SersiEmbed(
                title="Appeal Submitted",
                description="Your appeal has been received and is now under review. You will be notified of the outcome in due course. Please note that appeals can take up to 7 days to be reviewed. If you have any further information to provide, please use the button below to send a message to the moderation team.",
                footer="Sersi Appeals",
            ),
            view=AppealOngoingView(thread.id),
        )

        await interaction.followup.send(
            "Appeal submitted successfully. The moderation team will review your appeal and you will be notified of the outcome in due course.",
            ephemeral=True,
        )


class Appeals(commands.Cog):
    def __init__(self, bot: commands.Bot, config=Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        if member.guild.id != self.config.guilds.appeals:
            return

        if member.bot:
            return

        await member.send(
            embed=SersiEmbed(
                title="Welcome to the Appeals Server",
                description="You have joined the Appeals server. If you have been banned from a server and would like to appeal your ban, you can do so here. Please note that you will only be able to appeal if you have been banned from a server that uses the Sersi moderation bot.",
                footer="Sersi Appeals",
                fields={
                    "How to Appeal": "To appeal your ban please follow the instructions below. Please note that if you leave the Appeals Server the bot will be unable to DM you with the outcome of your appeal.",
                    "Step 1: Understand Your Ban": "Before appealing your ban, please ensure you understand why you were banned. You can find this information in the ban message you received when you were banned.",
                    "Step 2: Make Sure You're Calm": "Before appealing your ban, please ensure you are calm and collected. If you are angry or upset, it may be best to wait until you are in a better frame of mind before appealing. Any appeals that are aggressive, rude, or otherwise inappropriate will be rejected and you will never be able to appeal again.",
                    "Step 3: Submit Your Appeal": "To submit your appeal, please click one of the buttons below. One of the buttons will allow you to submit an appeal if you believe your ban was unfair or overlyharsh. By submitting this type of appeal you admit to breaking the rules as stated in the ban message, but that the punishment was not suitable. The other button will allow you to submit an appeal if you believe you did not break any rules. Please ensure you provide as much information as possible in your appeal.",
                    "Step 4: Await a Response": "Once you have submitted your appeal, the Administration Team will review your appeal and you will be notified of the outcome in due course. Please note that appeals can take up to 7 days to be reviewed. If you have any further information to provide, there will be a button which allows you to send a message to the Administration Team.",
                    "Step 5: Respect the Outcome": "Once the Administration Team has reviewed your appeal, you will be notified of the outcome. Please respect the decision of the Administration Team. If your appeal is accepted, you will be unbanned from the server and receive an invite. If your appeal is denied, you will remain banned from the server and will not be able to appeal again.",
                },
            ),
            view=AppealsSubmitView(),
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        acceptable_starts = [
            "submit_appeal",
            "appeal_denied",
            "appeal_accepted",
            "appeal_view_case",
            "appeal_dm_user",
            "appeal_dm_moderators",
        ]
        if not interaction.data["custom_id"].startswith(tuple(acceptable_starts)):
            return

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        if action == "submit_appeal":
            if kwargs["type_of_appeal"] == "ban":
                await interaction.response.send_modal(
                    AppealsModal(self.config, "Ban", kwargs["reason"])
                )

            elif kwargs["type_of_appeal"] == "timeout":
                await interaction.response.send_modal(
                    AppealsModal(self.config, "Timeout", kwargs["reason"])
                )

        elif action == "appeal_denied":
            pass

        elif action == "appeal_accepted":
            pass

        elif action == "appeal_view_case":
            pass

        elif action == "appeal_dm_user":
            pass

        elif action == "appeal_dm_moderators":
            pass


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Appeals(bot, kwargs["config"]))
