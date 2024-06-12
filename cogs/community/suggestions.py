import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.perms import is_admin, is_cet, permcheck
from utils.suggestions import (
    check_if_marked,
    get_suggestion_by_id,
    update_embed_outcome,
    update_embed_votes,
)
from utils.database import (
    SubmittedSuggestion,
    SuggestionVote,
    db_session,
    SuggestionReview,
    SuggestionOutcome,
)
from utils.base import encode_button_id, decode_button_id


class SuggestionApproveButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.green,
            label="Approve",
            custom_id=encode_button_id(
                "suggestion_review", outcome="approve", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionDenyButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.red,
            label="Deny",
            custom_id=encode_button_id(
                "suggestion_review", outcome="deny", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionSubmittedView(nextcord.ui.View):
    def __init__(self, suggestion_id: int):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(SuggestionApproveButton(suggestion_id))
        self.add_item(SuggestionDenyButton(suggestion_id))


class SubmitASuggestionButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="Submit a Suggestion",
            custom_id=encode_button_id("suggestion_submit"),
            disabled=False,
        )


class SubmitASuggestionView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(SubmitASuggestionButton())


class SuggestionMarkConsideringButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: str, currently_selected: bool):
        super().__init__(
            style=(
                nextcord.ButtonStyle.green
                if currently_selected
                else nextcord.ButtonStyle.blurple
            ),
            label="Considering",
            custom_id=encode_button_id(
                "suggestion_mark", outcome="Considering", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionMarkPlannedButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: str, currently_selected: bool):
        super().__init__(
            style=(
                nextcord.ButtonStyle.green
                if currently_selected
                else nextcord.ButtonStyle.blurple
            ),
            label="Planned",
            custom_id=encode_button_id(
                "suggestion_mark", outcome="Planned", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionMarkInProgressButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: str, currently_selected: bool):
        super().__init__(
            style=(
                nextcord.ButtonStyle.green
                if currently_selected
                else nextcord.ButtonStyle.blurple
            ),
            label="In Progress",
            custom_id=encode_button_id(
                "suggestion_mark", outcome="In Progress", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionMarkOnHoldButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: str, currently_selected: bool):
        super().__init__(
            style=(
                nextcord.ButtonStyle.green
                if currently_selected
                else nextcord.ButtonStyle.blurple
            ),
            label="On Hold",
            custom_id=encode_button_id(
                "suggestion_mark", outcome="On Hold", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionMarkCompletedButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: str, currently_selected: bool):
        super().__init__(
            style=(
                nextcord.ButtonStyle.green
                if currently_selected
                else nextcord.ButtonStyle.blurple
            ),
            label="Completed",
            custom_id=encode_button_id(
                "suggestion_mark", outcome="Completed", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionMarkNotHappeningButton(nextcord.ui.Button):
    def __init__(self, suggestion_id: str, currently_selected: bool):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red
                if currently_selected
                else nextcord.ButtonStyle.red
            ),
            label="Not Happening",
            custom_id=encode_button_id(
                "suggestion_mark", outcome="Not Happening", suggestion_id=suggestion_id
            ),
            disabled=False,
        )


class SuggestionMarkView(nextcord.ui.View):
    def __init__(self, suggestion_id: str, current_status: str = "Not Marked"):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(
            SuggestionMarkConsideringButton(
                suggestion_id, True if current_status == "Considering" else False
            )
        )
        self.add_item(
            SuggestionMarkPlannedButton(
                suggestion_id, True if current_status == "Planned" else False
            )
        )
        self.add_item(
            SuggestionMarkInProgressButton(
                suggestion_id, True if current_status == "In Progress" else False
            )
        )
        self.add_item(
            SuggestionMarkOnHoldButton(
                suggestion_id, True if current_status == "On Hold" else False
            )
        )
        self.add_item(
            SuggestionMarkCompletedButton(
                suggestion_id, True if current_status == "Completed" else False
            )
        )
        self.add_item(
            SuggestionMarkNotHappeningButton(
                suggestion_id, True if current_status == "Not Happening" else False
            )
        )


class SuggestionMarkModal(Modal):
    def __init__(self, config: Configuration, suggestion_id: str, outcome: str):
        super().__init__(f"Suggestion {outcome}")
        self.config = config
        self.suggestion_id = suggestion_id
        self.outcome = outcome

        self.suggestion_reason = nextcord.ui.TextInput(
            label=f"Reason for marking {self.outcome}",
            min_length=8,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.suggestion_reason)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        suggestion_instance: SubmittedSuggestion | None = get_suggestion_by_id(
            interaction, self.suggestion_id
        )

        logging_embed = SersiEmbed(
            title="Suggestion Marked",
            description="A change has been processed on a suggestion.",
            fields={
                "Suggestion ID": suggestion_instance.id,
                "Suggestion Outcome": self.outcome,
                "Reason": self.suggestion_reason.value,
                "Marked By": interaction.user.mention,
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=logging_embed
        )

        if check_if_marked(interaction, suggestion_instance):
            with db_session(interaction.user) as session:
                update_suggestion = (
                    session.query(SuggestionOutcome)
                    .filter_by(id=suggestion_instance.id)
                    .first()
                )

                update_suggestion.outcome = self.outcome
                update_suggestion.outcome_comment = self.suggestion_reason.value
                update_suggestion.outcome_reviewer = interaction.user.id
                session.commit()

        else:
            with db_session(interaction.user) as session:
                suggestion_outcome = SuggestionOutcome(
                    id=suggestion_instance.id,
                    outcome=self.outcome,
                    outcome_comment=self.suggestion_reason.value,
                    outcome_reviewer=interaction.user.id,
                )
                session.add(suggestion_outcome)
                session.commit()

        original_message: nextcord.WebhookMessage = await interaction.guild.get_channel(
            self.config.channels.suggestion_voting
        ).fetch_message(suggestion_instance.vote_message_id)

        if original_message is None:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The suggestion message could not be found. Please contact an administrator.",
                ephemeral=False,
            )

            interaction.message.edit(view=None)
            return

        with db_session(interaction.user) as session:
            updated_embed = await update_embed_outcome(
                interaction, original_message.embeds[0], self.suggestion_id, session
            )

        await original_message.edit(embed=updated_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} Suggestion marked as {self.outcome}!",
            ephemeral=True,
        )

        cet_embed = interaction.message.embeds[0]

        i = 0

        for field in cet_embed.fields:
            if field.name == "Current Status":
                updated_cet_embed = cet_embed.set_field_at(
                    index=i, name="Current Status", value=self.outcome, inline=False
                )
                await interaction.message.edit(
                    embed=updated_cet_embed,
                    view=SuggestionMarkView(self.suggestion_id, self.outcome),
                )
                break

            i += 1

        if self.outcome == "Not Happening":
            await interaction.guild.get_member(suggestion_instance.suggester).send(
                f"Your suggestion has been marked as `Not Happening` by {interaction.user.mention}. If you have any questions or concerns, please open a Community Engagement Team Ticket."
            )

            await interaction.message.edit(view=None)
            await original_message.edit(view=None)

            await original_message.thread.send(
                embed=SersiEmbed(
                    title="Suggestion Closed",
                    description="This suggestion has been marked as `Not Happening` and is now closed for further discussion.",
                )
            )
            await original_message.thread.edit(locked=True, archived=True)

        elif self.outcome == "Completed":
            await interaction.guild.get_member(suggestion_instance.suggester).send(
                f"Your suggestion has been marked as `Completed` by {interaction.user.mention}. Thank you for your contribution to the community!"
            )

            await interaction.message.edit(view=None)
            await original_message.edit(view=None)

            await original_message.thread.send(
                embed=SersiEmbed(
                    title="Suggestion Closed",
                    description="This suggestion has been marked as `Completed` and is now closed for further discussion.",
                )
            )
            await original_message.thread.edit(locked=True, archived=True)

            if suggestion_instance.suggester != interaction.user.id:
                bot: commands.Bot = interaction.client
                bot.dispatch("add_xp", interaction.user, 500, "COMMUNITY")


class SuggestionReviewModal(Modal):
    def __init__(self, config: Configuration, passed: bool, suggestion_id: str):
        super().__init__("Review Suggestion")
        self.config = config
        self.passed = passed
        self.suggestion_id = suggestion_id

        self.review_reason = nextcord.ui.TextInput(
            label="Reason for your decision",
            min_length=8,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.review_reason)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        suggestion_instance: SubmittedSuggestion = get_suggestion_by_id(
            interaction, self.suggestion_id
        )

        if self.passed:
            suggestion_embed = SersiEmbed(
                description=suggestion_instance.suggestion_text,
            )
            suggestion_embed.set_footer(text=f"Suggestion ID: {suggestion_instance.id}")
            suggestion_embed.set_thumbnail(
                url=interaction.guild.get_member(
                    suggestion_instance.suggester
                ).display_avatar.url
            )
            suggestion_embed.set_author(
                icon_url=interaction.guild.get_member(
                    suggestion_instance.suggester
                ).display_avatar.url,
                name=f"Suggestion from {interaction.guild.get_member(suggestion_instance.suggester).display_name}",
            )

            if suggestion_instance.media_url:
                suggestion_embed.add_field(
                    name="Media URL", value=suggestion_instance.media_url, inline=False
                )
                suggestion_embed.set_image(url=suggestion_instance.media_url)

            suggestion_embed.add_field(name="Yes Votes", value="`1`", inline=False)
            suggestion_embed.add_field(name="No Votes", value="`0`", inline=False)
            suggestion_embed.add_field(name="Net Approval", value="`+1`", inline=False)

            upvote = Button(
                label="Upvote",
                emoji="👍",
                style=nextcord.ButtonStyle.green,
                custom_id=encode_button_id(
                    "suggestion_vote",
                    vote_type="upvote",
                    suggestion_id=suggestion_instance.id,
                ),
            )

            downvote = Button(
                label="Downvote",
                emoji="👎",
                style=nextcord.ButtonStyle.red,
                custom_id=encode_button_id(
                    "suggestion_vote",
                    vote_type="downvote",
                    suggestion_id=suggestion_instance.id,
                ),
            )

            button_view = View(timeout=None, auto_defer=False)
            button_view.add_item(upvote)
            button_view.add_item(downvote)

            suggestion_post: nextcord.WebhookMessage = (
                await interaction.guild.get_channel(
                    self.config.channels.suggestion_voting
                ).send(embed=suggestion_embed, view=button_view)
            )

            await suggestion_post.create_thread(
                name=f"Suggestion {suggestion_instance.id}"
            )

            with db_session(interaction.user) as session:
                review_instance = SuggestionReview(
                    id=suggestion_instance.id,
                    review=True,
                    reviewer=interaction.user.id,
                    reason=self.review_reason.value,
                )
                session.add(review_instance)

                session.add(
                    SuggestionVote(
                        id=suggestion_instance.id,
                        voter=interaction.user.id,
                        vote=True,
                    )
                )

                update_suggestion = (
                    session.query(SubmittedSuggestion).filter_by(
                        id=suggestion_instance.id
                    )
                ).first()

                update_suggestion.vote_message_id = suggestion_post.id
                session.commit()

            approved_embed = SersiEmbed(
                title="Suggestion Approved",
                description=(
                    "Your suggestion has been approved and is now open for voting."
                ),
            )

            await interaction.guild.get_member(suggestion_instance.suggester).send(
                embed=approved_embed
            )

            await interaction.followup.send(
                f"{self.config.emotes.success} Suggestion made public for voting!"
            )

            await interaction.message.edit(
                view=SuggestionMarkView(suggestion_instance.id, "Not Marked"),
                embed=interaction.message.embeds[0].add_field(
                    name="Current Status", value="Not Marked", inline=False
                ),
            )

            if suggestion_instance.suggester != interaction.user.id:
                bot: commands.Bot = interaction.client
                bot.dispatch("add_xp", interaction.user, 100, "COMMUNITY")

        else:
            deny_embed = SersiEmbed(
                title="Suggestion Denied",
                description=(
                    "Your suggestion has been denied. For more information please open a Community Engagement Team Ticket."
                ),
                fields={
                    "Suggestion ID": suggestion_instance.id,
                    "Suggestion": suggestion_instance.suggestion_text,
                    "Media URL": suggestion_instance.media_url,
                    "Reason": self.review_reason.value,
                },
            )

            await interaction.guild.get_member(suggestion_instance.suggester).send(
                embed=deny_embed
            )

            await interaction.followup.send(
                f"{self.config.emotes.success} Suggestion denied!"
            )

            with db_session(interaction.user) as session:
                review_instance = SuggestionReview(
                    id=suggestion_instance.id,
                    review=False,
                    reviewer=interaction.user.id,
                    reason=self.review_reason.value,
                )
                session.add(review_instance)
                session.commit()

            await interaction.message.edit(view=None)


class SuggestionSubmitModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Submit Suggestion")
        self.config = config

        self.body = nextcord.ui.TextInput(
            label="What is your suggestion?",
            min_length=10,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.body)

        self.media_url = nextcord.ui.TextInput(
            label="Media URL (Optional)",
            min_length=10,
            max_length=1024,
            required=False,
            style=nextcord.TextInputStyle.short,
        )
        self.add_item(self.media_url)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        has_valid_media = False

        if self.media_url.value:
            if not self.media_url.value.startswith("http"):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The media URL provided is not valid. Please provide a valid URL. If you do not have a media URL, please leave this field empty. A media URL should start with `http` or `https`.",
                    ephemeral=True,
                )
                return

            if not self.media_url.value.endswith((".png", ".jpg", ".jpeg", ".gif")):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The media URL provided is not an image. Please provide a valid image URL. If you do not have a media URL, please leave this field empty. A media URL should end with `.png`, `.jpg`, `.jpeg`, or `.gif`.",
                    ephemeral=True,
                )
                return

            has_valid_media = True

        with db_session(interaction.user) as session:
            suggestion_instance = SubmittedSuggestion(
                suggestion_text=self.body.value,
                media_url=self.media_url.value,
                suggester=interaction.user.id,
            )
            session.add(suggestion_instance)
            session.commit()

            suggestion_instance = (
                session.query(SubmittedSuggestion)
                .filter_by(id=suggestion_instance.id)
                .first()
            )

        suggest_embed = SersiEmbed(
            title=f"New Suggestion By {interaction.user.display_name}",
            description=(
                "A new suggestion has been submitted for review. Please make due considerations before deciding to "
                "publish the suggestion or reject it."
            ),
            fields={
                "Suggester": f"{interaction.user.mention} ({interaction.user.id})",
                "Suggestion": self.body.value,
                "Media URL": self.media_url.value,
            },
        )
        suggest_embed.set_footer(text=f"Suggestion ID: {suggestion_instance.id}")
        if has_valid_media:
            suggest_embed.set_image(self.media_url.value)

        review_channel: nextcord.TextChannel = interaction.guild.get_channel(
            self.config.channels.suggestion_review
        )

        await review_channel.send(
            embed=suggest_embed, view=SuggestionSubmittedView(suggestion_instance.id)
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} Your suggestion has been submitted to the Community Engagement Team for review. If you want to edit the suggestion please use the suggestion edit command with suggestion id `{suggestion_instance.id}`.",
            ephemeral=True,
        )


class Suggestions(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def suggestion_embed(self, ctx: commands.Context):
        """Single use Command for the 'Submit Suggestion' Embed."""
        if not await permcheck(ctx, is_admin):
            return

        await ctx.send(
            embed=SersiEmbed(
                title="Submit a Suggestion",
                description="Submit a suggestion to the Community Engagement Team for review. Please ensure that your suggestion is well thought out and detailed.",
            ),
            view=SubmitASuggestionView(),
        )

        await ctx.message.delete()

    @nextcord.slash_command(
        name="suggestion",
        description="Manage suggestions.",
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def suggestion(self, interaction: nextcord.Interaction):
        pass

    @suggestion.subcommand(
        name="retrieve_control_panel",
        description="Retrieve the control panel for a suggestion.",
    )
    async def retrieve_control_panel(
        self, interaction: nextcord.Interaction, suggestion_id: str
    ):
        if not await permcheck(interaction, is_cet):
            return

        suggestion_instance: SubmittedSuggestion = get_suggestion_by_id(
            interaction, suggestion_id
        )

        if not suggestion_instance:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} The suggestion ID provided is invalid. Please provide a valid suggestion ID.",
                ephemeral=True,
            )
            return

        suggestion_embed = SersiEmbed(
            title=f"New Suggestion By {interaction.guild.get_member(suggestion_instance.suggester).display_name}",
            description=suggestion_instance.suggestion_text,
            fields={
                "Suggester": f"{interaction.guild.get_member(suggestion_instance.suggester).mention} ({suggestion_instance.suggester})",
                "Media URL": suggestion_instance.media_url,
                "Current Status": "Not Marked",
            },
        )

        if suggestion_instance.media_url:
            suggestion_embed.set_image(url=suggestion_instance.media_url)

        suggestion_embed.set_footer(text=f"Suggestion ID: {suggestion_instance.id}")

        await interaction.response.send_message(
            embed=suggestion_embed, view=SuggestionMarkView(suggestion_instance.id)
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        if not interaction.data["custom_id"].startswith("suggestion"):
            return

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])
        if action == "suggestion_vote":
            match kwargs["vote_type"]:
                case "upvote":
                    await interaction.response.defer(ephemeral=True)
                    original_embed = interaction.message.embeds[0]

                    with db_session(interaction.user) as session:
                        already_voted = (
                            session.query(SuggestionVote)
                            .filter_by(
                                voter=interaction.user.id, id=kwargs["suggestion_id"]
                            )
                            .first()
                        )

                        if already_voted:
                            if already_voted.vote is True:
                                await interaction.followup.send(
                                    f"{self.config.emotes.fail} You have already upvoted this suggestion.",
                                    ephemeral=True,
                                )

                            if already_voted.vote is False:
                                already_voted.vote = True
                                session.commit()

                                await update_embed_votes(
                                    original_embed, kwargs["suggestion_id"], session
                                )

                                await interaction.message.edit(embed=original_embed)

                                await interaction.followup.send(
                                    f"{self.config.emotes.success} Your vote has been updated to an upvote.",
                                    ephemeral=True,
                                )

                        else:
                            new_vote = SuggestionVote(
                                id=kwargs["suggestion_id"],
                                voter=interaction.user.id,
                                vote=True,
                            )
                            session.add(new_vote)
                            session.commit()

                            approval = await update_embed_votes(
                                original_embed, kwargs["suggestion_id"], session
                            )

                            await interaction.message.edit(embed=original_embed)

                            await interaction.followup.send(
                                f"{self.config.emotes.success} Your vote has been registered as an upvote.",
                                ephemeral=True,
                            )

                            self.bot.dispatch(
                                "add_xp", interaction.user, 25, "COMMUNITY"
                            )

                            if approval > 0:
                                suggestion = (
                                    session.query(SubmittedSuggestion)
                                    .filter_by(id=kwargs["suggestion_id"])
                                    .first()
                                )
                                self.bot.dispatch(
                                    "add_xp",
                                    interaction.guild.get_member(suggestion.suggester),
                                    approval,
                                    "COMMUNITY",
                                )

                case "downvote":
                    await interaction.response.defer(ephemeral=True)
                    original_embed = interaction.message.embeds[0]

                    with db_session(interaction.user) as session:
                        already_voted = (
                            session.query(SuggestionVote)
                            .filter_by(
                                voter=interaction.user.id, id=kwargs["suggestion_id"]
                            )
                            .first()
                        )

                        if already_voted:
                            if already_voted.vote is False:
                                await interaction.followup.send(
                                    f"{self.config.emotes.fail} You have already downvoted this suggestion.",
                                    ephemeral=True,
                                )

                            if already_voted.vote is True:
                                already_voted.vote = False
                                session.commit()

                                await update_embed_votes(
                                    original_embed, kwargs["suggestion_id"], session
                                )

                                await interaction.message.edit(embed=original_embed)

                                await interaction.followup.send(
                                    f"{self.config.emotes.success} Your vote has been updated to a downvote.",
                                    ephemeral=True,
                                )

                        else:
                            new_vote = SuggestionVote(
                                id=kwargs["suggestion_id"],
                                voter=interaction.user.id,
                                vote=False,
                            )
                            session.add(new_vote)
                            session.commit()

                            await update_embed_votes(
                                original_embed, kwargs["suggestion_id"], session
                            )

                            await interaction.message.edit(embed=original_embed)

                            await interaction.followup.send(
                                f"{self.config.emotes.success} Your vote has been registered as a downvote.",
                                ephemeral=True,
                            )

                            self.bot.dispatch(
                                "add_xp", interaction.user, 25, "COMMUNITY"
                            )

        elif action == "suggestion_submit":
            await interaction.response.send_modal(SuggestionSubmitModal(self.config))

        elif action == "suggestion_review":
            match kwargs["outcome"]:
                case "approve":
                    await interaction.response.send_modal(
                        SuggestionReviewModal(
                            self.config, True, kwargs["suggestion_id"]
                        )
                    )

                case "deny":
                    await interaction.response.send_modal(
                        SuggestionReviewModal(
                            self.config, False, kwargs["suggestion_id"]
                        ),
                        kwargs["suggestion_id"],
                    )

        elif action == "suggestion_mark":
            await interaction.response.send_modal(
                SuggestionMarkModal(
                    self.config, kwargs["suggestion_id"], kwargs["outcome"]
                )
            )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Suggestions(bot, kwargs["config"]))
