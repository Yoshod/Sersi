import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.perms import is_cet, permcheck
from utils.suggestions import (
    check_if_reviewed,
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


class Suggestions(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
        description="Manage suggestions",
    )
    async def suggestion(self, interaction: nextcord.Interaction):
        pass

    @suggestion.subcommand(description="Submit a suggestion!")
    async def submit(
        self,
        interaction: nextcord.Interaction,
        suggestion: str = nextcord.SlashOption(
            name="suggestion",
            description="The suggestion you wish to make",
            min_length=8,
            max_length=1240,
        ),
        media_url: str = nextcord.SlashOption(
            name="suggestion_media",
            description="This is optional. Provide the URL to any media that relates to your suggestion.",
            required=False,
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        with db_session(interaction.user) as session:
            suggestion_instance = SubmittedSuggestion(
                suggestion_text=suggestion,
                media_url=media_url,
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
                "Suggestion": suggestion,
                "Media URL": media_url,
            },
        )

        suggest_embed.set_footer(text=f"Suggestion ID: {suggestion_instance.id}")

        review_channel: nextcord.TextChannel = interaction.guild.get_channel(
            self.config.channels.suggestion_review
        )

        await review_channel.send(embed=suggest_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} Your suggestion has been submitted to the Community Engagement Team for review. If you want to edit the suggestion please use the suggestion edit command with suggestion id `{suggestion_instance.id}`."
        )
        return

    @suggestion.subcommand(description="Review a suggestion")
    async def review(
        self,
        interaction: nextcord.Interaction,
        suggestion_id: str = nextcord.SlashOption(
            name="suggestion_id",
            description="The ID of the suggestion you want to review",
            min_length=11,
            max_length=22,
        ),
        review_outcome: str = nextcord.SlashOption(
            name="outcome",
            description="The outcome of the review",
            choices={"Approve": "Approve", "Deny": "Deny"},
        ),
        review_reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason for your decision. May be shared with suggester.",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_cet):
            return

        suggestion_instance: SubmittedSuggestion | None = get_suggestion_by_id(
            interaction, suggestion_id
        )

        if not suggestion_instance:
            interaction.response.send_message(
                f"{self.config.emotes.fail} `{suggestion_id}` is not a valid suggestion!",
                ephemeral=True,
            )

        if check_if_reviewed(interaction, suggestion_instance):
            interaction.response.send_message(
                f"{self.config.emotes.fail} `{suggestion_instance.id}` has already been reviewed.",
                ephemeral=True,
            )

        if interaction.channel.id != self.config.channels.suggestion_review:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} This command can only be used in the suggestion review channel.",
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        logging_embed = SersiEmbed(
            title="Suggestion Updated",
            description="A change has been processed on a suggestion.",
            fields={
                "Suggestion ID": suggestion_instance.id,
                "Review Outcome": review_outcome,
                "Reason": review_reason,
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=logging_embed
        )

        if review_outcome == "Deny":
            deny_embed = SersiEmbed(
                title="Suggestion Denied",
                description=(
                    "Your suggestion has been denied. For more information please open a Community Engagement Team Ticket."
                ),
                fields={
                    "Suggestion ID": suggestion_instance.id,
                    "Suggestion": suggestion_instance.suggestion_text,
                    "Media URL": suggestion_instance.media_url,
                    "Reason": review_reason,
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
                    reason=review_reason,
                )
                session.add(review_instance)
                session.commit()

            return

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

        suggestion_embed.add_field(name="Yes Votes", value="`0`", inline=False)
        suggestion_embed.add_field(name="No Votes", value="`0`", inline=False)
        suggestion_embed.add_field(name="Net Approval", value="`0`", inline=False)

        upvote = Button(
            label="Upvote",
            emoji="👍",
            style=nextcord.ButtonStyle.green,
            custom_id=f"suggestion-upvote:{suggestion_instance.id}",
        )

        downvote = Button(
            label="Downvote",
            emoji="👎",
            style=nextcord.ButtonStyle.red,
            custom_id=f"suggestion-downvote:{suggestion_instance.id}",
        )

        button_view = View(timeout=None, auto_defer=False)
        button_view.add_item(upvote)
        button_view.add_item(downvote)

        suggestion_post: nextcord.WebhookMessage = await interaction.guild.get_channel(
            self.config.channels.suggestion_voting
        ).send(embed=suggestion_embed, view=button_view)

        with db_session(interaction.user) as session:
            review_instance = SuggestionReview(
                id=suggestion_instance.id,
                review=True,
                reviewer=interaction.user.id,
                reason=review_reason,
            )
            session.add(review_instance)
            session.commit()

            update_suggestion = (
                session.query(SubmittedSuggestion).filter_by(id=suggestion_instance.id)
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

    @suggestion.subcommand(description="Mark a suggestion outcome")
    async def mark(
        self,
        interaction: nextcord.Interaction,
        suggestion_id: str = nextcord.SlashOption(
            name="suggestion_id",
            description="The ID of the suggestion you want to mark",
            min_length=11,
            max_length=22,
        ),
        suggestion_outcome: str = nextcord.SlashOption(
            name="outcome",
            description="The outcome of the suggestion",
            choices={
                "Considering": "Considering",
                "Planned": "Planned",
                "In Progress": "In Progress",
                "On Hold": "On Hold",
                "Completed": "Completed",
                "Not Happening": "Not Happening",
            },
        ),
        suggestion_reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason for your decision. May be shared with suggester.",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_cet):
            return

        suggestion_instance: SubmittedSuggestion | None = get_suggestion_by_id(
            interaction, suggestion_id
        )

        if not suggestion_instance:
            interaction.response.send_message(
                f"{self.config.emotes.fail} `{suggestion_id}` is not a valid suggestion!",
                ephemeral=True,
            )

        if not check_if_reviewed(interaction, suggestion_instance):
            await interaction.response.send_message(
                f"{self.config.emotes.fail} This suggestion has not been reviewed yet. Please review it before marking an outcome.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        logging_embed = SersiEmbed(
            title="Suggestion Marked",
            description="A change has been processed on a suggestion.",
            fields={
                "Suggestion ID": suggestion_instance.id,
                "Suggestion Outcome": suggestion_outcome,
                "Reason": suggestion_reason,
                "Marked By": interaction.user.mention,
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=logging_embed
        )

        # Check if the suggestion is already marked. If already marked update the database and edit the embed. Else create a new entry in the database and edit the embed.
        if check_if_marked(interaction, suggestion_instance):
            with db_session(interaction.user) as session:
                update_suggestion = (
                    session.query(SuggestionOutcome)
                    .filter_by(id=suggestion_instance.id)
                    .first()
                )

                update_suggestion.outcome = suggestion_outcome
                update_suggestion.outcome_comment = suggestion_reason
                update_suggestion.outcome_reviewer = interaction.user.id
                session.commit()

            original_message: nextcord.WebhookMessage = (
                await interaction.guild.get_channel(
                    self.config.channels.suggestion_voting
                ).fetch_message(suggestion_instance.vote_message_id)
            )

            with db_session(interaction.user) as session:
                updated_embed = await update_embed_outcome(
                    interaction, original_message.embeds[0], suggestion_id, session
                )

            await original_message.edit(embed=updated_embed, view=None)

            await interaction.followup.send(
                f"{self.config.emotes.success} Suggestion marked as {suggestion_outcome}!",
                ephemeral=True,
            )
            return

        with db_session(interaction.user) as session:
            suggestion_outcome_instance = SuggestionOutcome(
                id=suggestion_instance.id,
                outcome=suggestion_outcome,
                outcome_comment=suggestion_reason,
                outcome_reviewer=interaction.user.id,
            )
            session.add(suggestion_outcome_instance)
            session.commit()

        original_message: nextcord.WebhookMessage = await interaction.guild.get_channel(
            self.config.channels.suggestion_voting
        ).fetch_message(suggestion_instance.vote_message_id)

        with db_session(interaction.user) as session:
            updated_embed = await update_embed_outcome(
                interaction, original_message.embeds[0], suggestion_id, session
            )

        await original_message.edit(embed=updated_embed, view=None)

        await interaction.followup.send(
            f"{self.config.emotes.success} Suggestion marked as {suggestion_outcome}!",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["suggestion-upvote", suggestion_id]:
                await interaction.response.defer(ephemeral=True)
                original_embed = interaction.message.embeds[0]

                with db_session(interaction.user) as session:
                    already_voted = (
                        session.query(SuggestionVote)
                        .filter_by(voter=interaction.user.id, id=suggestion_id)
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
                                original_embed, suggestion_id, session
                            )

                            await interaction.message.edit(embed=original_embed)

                            await interaction.followup.send(
                                f"{self.config.emotes.success} Your vote has been updated to an upvote.",
                                ephemeral=True,
                            )

                    else:
                        new_vote = SuggestionVote(
                            id=suggestion_id, voter=interaction.user.id, vote=True
                        )
                        session.add(new_vote)
                        session.commit()

                        await update_embed_votes(original_embed, suggestion_id, session)

                        await interaction.message.edit(embed=original_embed)

                        await interaction.followup.send(
                            f"{self.config.emotes.success} Your vote has been registered as an upvote.",
                            ephemeral=True,
                        )

            case ["suggestion-downvote", suggestion_id]:
                await interaction.response.defer(ephemeral=True)
                original_embed = interaction.message.embeds[0]

                with db_session(interaction.user) as session:
                    already_voted = (
                        session.query(SuggestionVote)
                        .filter_by(voter=interaction.user.id, id=suggestion_id)
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
                                original_embed, suggestion_id, session
                            )

                            await interaction.message.edit(embed=original_embed)

                            await interaction.followup.send(
                                f"{self.config.emotes.success} Your vote has been updated to a downvote.",
                                ephemeral=True,
                            )

                    else:
                        new_vote = SuggestionVote(
                            id=suggestion_id, voter=interaction.user.id, vote=False
                        )
                        session.add(new_vote)
                        session.commit()

                        await update_embed_votes(original_embed, suggestion_id, session)

                        await interaction.message.edit(embed=original_embed)

                        await interaction.followup.send(
                            f"{self.config.emotes.success} Your vote has been registered as a downvote.",
                            ephemeral=True,
                        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Suggestions(bot, kwargs["config"]))
