import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.database import GithubIntegrationBlacklist, db_session
from utils.sersi_embed import SersiEmbed
from utils.dialog import confirm, ButtonPreset
from utils.base import (
    encode_button_id,
    decode_button_id,
    encode_snowflake,
    decode_snowflake,
)

from utils.github import submit_issue


class SubmitToGithubButton(nextcord.ui.Button):
    def __init__(self, user_id: int, report_type: str, guild_id: int, message_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="Submit to GitHub",
            custom_id=encode_button_id(
                "github_submit",
                report_type=report_type,
                user_id=encode_snowflake(user_id),
                guild_id=encode_snowflake(guild_id),
                message_id=encode_snowflake(message_id),
            ),
            disabled=False,
        )


class RejectReportButton(nextcord.ui.Button):
    def __init__(self, user_id: int, report_type: str, guild_id: int, message_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.red,
            label="Reject Report",
            custom_id=encode_button_id(
                "github_reject",
                report_type=report_type,
                user_id=encode_snowflake(user_id),
                guild_id=encode_snowflake(guild_id),
                message_id=encode_snowflake(message_id),
            ),
            disabled=False,
        )


class ReportBlacklistButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.red,
            label="Blacklist",
            custom_id=encode_button_id(
                "github_blacklist", user_id=encode_snowflake(user_id)
            ),
            disabled=False,
        )


class ReportView(nextcord.ui.View):
    def __init__(self, user_id: int, report_type: str, guild_id: int, message_id: int):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(SubmitToGithubButton(user_id, report_type, guild_id, message_id))
        self.add_item(RejectReportButton(user_id, report_type, guild_id, message_id))
        self.add_item(ReportBlacklistButton(user_id))


class FeatureRequestModal(nextcord.ui.Modal):
    def __init__(
        self,
        bot: nextcord.Client,
        config: Configuration,
        user_id: int,
        guild_id: int,
        message_id: int,
    ):
        super().__init__(title="Feature Request", timeout=None, auto_defer=False)
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.message_id = message_id
        self.config = config

        self.proposed_solution = nextcord.ui.TextInput(
            label="Do you have a proposed solution?",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.proposed_solution)

        self.impact = nextcord.ui.TextInput(
            label="What impact will this feature have?",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.impact)

        self.priority = nextcord.ui.TextInput(
            label="What priority should this feature have?",
            min_length=5,
            max_length=5,
            required=True,
            style=nextcord.TextInputStyle.short,
        )
        self.add_item(self.priority)

        self.priority_reason = nextcord.ui.TextInput(
            label="Why should this feature have this priority?",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.priority_reason)

        self.milestone = nextcord.ui.TextInput(
            label="What milestone should this be included in?",
            min_length=5,
            max_length=5,
            required=True,
            style=nextcord.TextInputStyle.short,
        )
        self.add_item(self.milestone)

    async def callback(self, interaction: nextcord.Interaction):
        """Run whenever the 'submit' button is pressed."""

        print("Scream!!!! AHHHHHHHH")

        await interaction.response.defer(ephemeral=True)

        modal_data = {
            "proposed_solution": self.proposed_solution.value,
            "impact": self.impact.value,
            "priority": self.priority.value,
            "priority_reason": self.priority_reason.value,
            "milestone": self.milestone.value,
        }

        issue_number = submit_issue("feature", interaction, modal_data=modal_data)

        message: nextcord.Message = await interaction.guild.get_channel(
            self.config.channels.feature_requests
        ).fetch_message(decode_snowflake(self.message_id))

        if not message:
            return await interaction.followup.send(
                f"{self.config.emotes.fail} The message could not be found",
            )

        try:
            await (
                self.bot.get_guild(decode_snowflake(self.guild_id))
                .get_member(decode_snowflake(self.user_id))
                .send(
                    embed=SersiEmbed(
                        title="Submission Accepted",
                        description=f"Your suggestion has been accepted. Thanks for your contribution to Sersi!",
                        fields={
                            "Developer": f"{interaction.user.display_name} ({interaction.user.id})",
                            "Development Server": "discord.gg/N5z7azzhTN",
                            "Issue": f"https://github.com/Yoshod/Sersi/issues/{issue_number}",
                        },
                    )
                )
            )
            dm_sent = True
        except nextcord.Forbidden:
            dm_sent = False

        updated_embed = message.embeds[0]

        updated_embed.add_field(
            name="Status",
            value="Submitted",
            inline=False,
        )

        await message.edit(view=None)

        await message.thread.send(
            embed=SersiEmbed(
                title="Feature Request Submitted",
                description=f"This feature request has been submitted. This thread is now locked.",
                fields={
                    "Proposed Solution": self.proposed_solution.value,
                    "Impact": self.impact.value,
                    "Priority": self.priority.value,
                    "Priority Reason": self.priority_reason.value,
                    "Milestone": self.milestone.value,
                    "Developer": f"{interaction.user.display_name} ({interaction.user.id})",
                    "DM Sent": (
                        self.config.emotes.success
                        if dm_sent
                        else self.config.emotes.fail
                    ),
                    "Issue": f"https://github.com/Yoshod/Sersi/issues/{issue_number}",
                },
            )
        )

        await message.thread.edit(archived=True, locked=True)

        await interaction.followup.send(
            f"{self.config.emotes.success} Feature request submitted!",
            ephemeral=True,
        )


class RejectReasonModal(nextcord.ui.Modal):
    def __init__(
        self,
        bot: nextcord.Client,
        config: Configuration,
        user_id: int,
        guild_id: int,
        message_id: int,
        report_type: str,
    ):
        super().__init__(
            title="Reject Report",
            timeout=None,
            auto_defer=False,
        )
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.message_id = message_id
        self.report_type = report_type
        self.config = config

        self.reason = nextcord.ui.TextInput(
            label="What is the reason for rejecting this report?",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction):
        """Run whenever the 'submit' button is pressed."""

        await interaction.response.defer(ephemeral=True)

        try:
            await (
                self.bot.get_guild(decode_snowflake(self.guild_id))
                .get_member(decode_snowflake(self.user_id))
                .send(
                    embed=SersiEmbed(
                        title="Submission Rejected",
                        description=f"Your submission has been rejected. Please do not resubmit this report. To discuss this further, please contact a member of the Sersi team on the Sersi Discord server.",
                        fields={
                            "Reason": self.reason.value,
                            "Developer": f"{interaction.user.display_name} ({interaction.user.id})",
                            "Development Server": "discord.gg/N5z7azzhTN",
                        },
                    )
                )
            )
            dm_sent = True
        except nextcord.Forbidden:
            dm_sent = False

        if self.report_type == "feature":
            message: nextcord.WebhookMessage = await interaction.guild.get_channel(
                self.config.channels.feature_requests
            ).fetch_message(decode_snowflake(self.message_id))

            if not message:
                return await interaction.followup.send(
                    f"{self.config.emotes.fail} The message could not be found",
                )

            updated_embed = message.embeds[0]

            updated_embed.add_field(
                name="Status",
                value="Rejected",
                inline=False,
            )

            await message.edit(view=None, embed=updated_embed)

            await message.thread.send(
                embed=SersiEmbed(
                    title="Submission Rejected",
                    description=f"This submission has been rejected. This thread is now locked.",
                    fields={
                        "Reason": self.reason.value,
                        "Developer": f"{interaction.user.display_name} ({interaction.user.id})",
                        "Development Server": "discord.gg/N5z7azzhTN",
                        "DM Sent": (
                            self.config.emotes.success
                            if dm_sent
                            else self.config.emotes.fail
                        ),
                    },
                )
            )

            await message.thread.edit(archived=True, locked=True)

        elif self.report_type == "bug":
            message: nextcord.WebhookMessage = await interaction.guild.get_channel(
                self.config.channels.bug_reports
            ).fetch_message(decode_snowflake(self.message_id))

            if not message:
                return await interaction.followup.send(
                    f"{self.config.emotes.fail} The message could not be found",
                )

            updated_embed = message.embeds[0]

            updated_embed.add_field(
                name="Status",
                value="Rejected",
                inline=False,
            )

            await message.edit(view=None, embed=updated_embed)

            await message.thread.send(
                embed=SersiEmbed(
                    title="Submission Rejected",
                    description=f"This submission has been rejected. This thread is now locked.",
                    fields={
                        "Reason": self.reason.value,
                        "Developer": f"{interaction.user.display_name} ({interaction.user.id})",
                        "Development Server": "discord.gg/N5z7azzhTN",
                        "DM Sent": (
                            self.config.emotes.success
                            if dm_sent
                            else self.config.emotes.fail
                        ),
                    },
                )
            )

            await message.thread.edit(archived=True, locked=True)

        await interaction.followup.send(
            f"{self.config.emotes.success} Report rejected!",
            ephemeral=True,
        )


class ReportBlacklistModal(nextcord.ui.Modal):
    def __init__(self, config: Configuration, user_id: int):
        super().__init__(title="Blacklist User", timeout=None, auto_defer=False)
        self.config = config
        self.user_id = user_id

        self.reason = nextcord.ui.TextInput(
            label="Why blacklisting this user?",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.reason)

    async def callback(self, interaction: nextcord.Interaction):
        """Run whenever the 'submit' button is pressed."""

        await interaction.response.defer(ephemeral=True)

        await interaction.message.delete()

        with db_session() as session:
            blacklist = GithubIntegrationBlacklist(
                user=decode_snowflake(self.user_id),
                added_by=interaction.user.id,
                reason=self.reason.value,
            )
            session.add(blacklist)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} User blacklisted!",
            ephemeral=True,
        )


class GithubIntegration(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Submit Feedback",
    )
    async def feedback(
        self,
        interaction: nextcord.Interaction,
    ):
        pass

    @feedback.subcommand(
        name="bug_report",
        description="Report a bug",
    )
    async def bug_report(
        self,
        interaction: nextcord.Interaction,
        user_type: str = nextcord.SlashOption(
            name="user_type",
            description="The type of user you are",
            required=True,
            choices={
                "Sersi Developer": "developer",
                "Sersi Tester": "tester",
                "Server Administator": "admin",
                "Server Moderator": "mod",
                "Server Member": "member",
            },
        ),
        title: str = nextcord.SlashOption(
            name="title",
            description="The title of the bug report",
            required=True,
        ),
        description: str = nextcord.SlashOption(
            name="description",
            description="The description of the bug",
            required=True,
        ),
        reproduction: str = nextcord.SlashOption(
            name="reproduction",
            description="How to reproduce the bug",
            required=True,
        ),
        expected: str = nextcord.SlashOption(
            name="expected",
            description="What you expected to happen",
            required=True,
        ),
        client_type: str = nextcord.SlashOption(
            name="client_type",
            description="The client type you are using",
            required=True,
            choices={
                "Desktop": "desktop",
                "Mobile": "mobile",
                "Web": "web",
            },
        ),
        client_version: str = nextcord.SlashOption(
            name="client_version",
            description="The version of the client you are using",
            required=True,
            choices={
                "Stable": "stable",
                "Public Test Build": "ptb",
                "Canary": "canary",
            },
        ),
        additional_info: str = nextcord.SlashOption(
            name="additional_info",
            description="Any additional information you would like to provide",
            required=False,
        ),
        screenshot: nextcord.Attachment = nextcord.SlashOption(
            name="screenshot",
            description="Screenshots of the bug",
            required=False,
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            user = (
                session.query(GithubIntegrationBlacklist)
                .filter_by(user=interaction.user.id)
                .first()
            )

            if user:
                return await interaction.followup.send(
                    f"{self.config.emotes.fail} You are blacklisted",
                    ephemeral=True,
                )

        app_info = await self.bot.application_info()

        if (
            interaction.user.id
            not in [developer.id for developer in app_info.team.members]
            and user_type == "developer"
        ):
            return await interaction.followup.send(
                "You are not a developer",
                ephemeral=True,
            )

        if screenshot:
            if screenshot.content_type not in [
                "image/png",
                "image/jpeg",
                "image/jpg",
                "image/gif",
            ]:
                return await interaction.followup.send(
                    "Invalid file type. Please upload a PNG, JPEG, JPG, or GIF file",
                    ephemeral=True,
                )

        bug_report_embed = SersiEmbed(
            title=f"Bug Report: {title}",
            fields={
                "User Type": user_type,
                "Description": description,
                "Reproduction": reproduction,
                "Expected": expected,
                "Client Type": client_type,
                "Client Version": client_version,
                "Additional Info": additional_info,
            },
        )

        if screenshot:
            bug_report_embed.set_image(url=screenshot.url)

        if await confirm(
            interaction,
            embed=bug_report_embed,
            content="Are you sure you want to submit this bug report?",
            true_button=ButtonPreset.YES,
            false_button=ButtonPreset.NO,
        ):
            bug_post = (
                await self.bot.get_guild(self.config.guilds.errors)
                .get_channel(self.config.channels.bug_reports)
                .send(
                    embed=bug_report_embed,
                )
            )

            await bug_post.edit(
                view=ReportView(
                    interaction.user.id, "bug", interaction.guild.id, bug_post.id
                )
            )

            await bug_post.create_thread(
                name=f"Bug Report: {title}",
            )

            await interaction.followup.send(
                f"{self.config.emotes.success} Bug report submitted!",
                ephemeral=True,
            )

    @feedback.subcommand(
        name="feature_request",
        description="Request a feature",
    )
    async def feature_request(
        self,
        interaction: nextcord.Interaction,
        user_type: str = nextcord.SlashOption(
            name="user_type",
            description="The type of user you are",
            required=True,
            choices={
                "Sersi Developer": "developer",
                "Sersi Tester": "tester",
                "Server Administator": "admin",
                "Server Moderator": "mod",
                "Server Member": "member",
            },
        ),
        title: str = nextcord.SlashOption(
            name="title",
            description="The title of the feature request",
            required=True,
        ),
        description: str = nextcord.SlashOption(
            name="description",
            description="The description of the feature",
            required=True,
        ),
        use_case: str = nextcord.SlashOption(
            name="use_case",
            description="The use case of the feature",
            required=True,
        ),
        additional_info: str = nextcord.SlashOption(
            name="additional_info",
            description="Any additional information you would like to provide",
            required=False,
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            user = (
                session.query(GithubIntegrationBlacklist)
                .filter_by(user=interaction.user.id)
                .first()
            )

            if user:
                return await interaction.followup.send(
                    f"{self.config.emotes.fail} You are blacklisted",
                    ephemeral=True,
                )

        app_info = await self.bot.application_info()

        if (
            interaction.user.id
            not in [developer.id for developer in app_info.team.members]
            and user_type == "developer"
        ):
            return await interaction.followup.send(
                "You are not a developer",
                ephemeral=True,
            )

        feature_request_embed = SersiEmbed(
            title=f"Feature Request: {title}",
            fields={
                "User Type": user_type,
                "Description": description,
                "Use Case": use_case,
                "Additional Info": additional_info,
            },
        )

        if await confirm(
            interaction,
            embed=feature_request_embed,
            content="Are you sure you want to submit this feature request?",
            true_button=ButtonPreset.YES,
            false_button=ButtonPreset.NO,
        ):
            feature_post = (
                await self.bot.get_guild(self.config.guilds.errors)
                .get_channel(self.config.channels.feature_requests)
                .send(
                    embed=feature_request_embed,
                )
            )

            await feature_post.edit(
                view=ReportView(
                    interaction.user.id,
                    "feature",
                    interaction.guild.id,
                    feature_post.id,
                )
            )

            await feature_post.create_thread(
                name=f"Feature Request: {title}",
            )

            await interaction.followup.send(
                f"{self.config.emotes.success} Feature request submitted!",
                ephemeral=True,
            )

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640],
        description="Remove from blacklist",
    )
    async def remove_blacklist(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.User = nextcord.SlashOption(
            name="user",
            description="The user to remove from the blacklist",
            required=True,
        ),
    ):
        app_info = await self.bot.application_info()

        if interaction.user.id not in [
            developer.id for developer in app_info.team.members
        ]:
            return await interaction.followup.send(
                "You are not a developer",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            user = (
                session.query(GithubIntegrationBlacklist)
                .filter_by(user=user.id)
                .first()
            )

            if not user:
                return await interaction.followup.send(
                    f"{self.config.emotes.fail} User is not blacklisted",
                    ephemeral=True,
                )

            session.delete(user)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} User removed from blacklist",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        acceptable_starts = ["github_submit", "github_reject", "github_blacklist"]
        if not interaction.data["custom_id"].startswith(tuple(acceptable_starts)):
            return

        app_info = await self.bot.application_info()

        if interaction.user.id not in [
            developer.id for developer in app_info.team.members
        ]:
            return await interaction.followup.send(
                "You are not a developer",
                ephemeral=True,
            )

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        user_id = kwargs["user_id"]
        try:
            guild_id = kwargs["guild_id"]
            report_type = kwargs["report_type"]
            message_id = kwargs["message_id"]
        except KeyError:
            guild_id = None
            report_type = None
            message_id = None

        if (
            interaction.data["custom_id"].startswith("github_submit")
            and report_type == "feature"
        ):
            await interaction.response.send_modal(
                FeatureRequestModal(
                    self.bot, self.config, user_id, guild_id, message_id
                )
            )

        elif (
            interaction.data["custom_id"].startswith("github_submit")
            and report_type == "bug"
        ):
            await interaction.response.defer(ephemeral=True)

            issue_number = submit_issue("bug", interaction, modal_data=None)

            try:
                await (
                    self.bot.get_guild(decode_snowflake(guild_id))
                    .get_member(decode_snowflake(user_id))
                    .send(
                        embed=SersiEmbed(
                            title="Bug Report Accepted",
                            description=f"Your bug report has been accepted. Thanks for your contribution to Sersi!",
                            fields={
                                "Developer": f"{interaction.user.display_name} ({interaction.user.id})",
                                "Development Server": "discord.gg/N5z7azzhTN",
                                "Issue": f"https://github.com/Yoshod/Sersi/issues/{issue_number}",
                            },
                        )
                    )
                )
                dm_sent = True
            except nextcord.Forbidden:
                dm_sent = False

            updated_embed = interaction.message.embeds[0]

            updated_embed.add_field(
                name="DM Sent",
                value=(
                    self.config.emotes.success if dm_sent else self.config.emotes.fail
                ),
                inline=False,
            )

            updated_embed.add_field(
                name="Status",
                value="Submitted",
                inline=False,
            )

            await interaction.message.edit(view=None, embed=updated_embed)

            await interaction.message.thread.send(
                embed=SersiEmbed(
                    title="Bug Report Submitted",
                    description=f"This bug report has been submitted. This thread is now locked.",
                    fields={
                        "Developer": f"{interaction.user.display_name} ({interaction.user.id})",
                        "Issue": f"https://github.com/Yoshod/Sersi/issues/{issue_number}",
                    },
                )
            )

            await interaction.message.thread.edit(archived=True, locked=True)

            await interaction.followup.send(
                f"{self.config.emotes.success} Bug report submitted!",
                ephemeral=True,
            )

        elif interaction.data["custom_id"].startswith("github_reject"):
            await interaction.response.send_modal(
                RejectReasonModal(
                    self.bot, self.config, user_id, guild_id, message_id, report_type
                )
            )

        elif interaction.data["custom_id"].startswith("github_blacklist"):
            await interaction.response.send_modal(
                ReportBlacklistModal(self.config, user_id)
            )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(GithubIntegration(bot, kwargs["config"]))
