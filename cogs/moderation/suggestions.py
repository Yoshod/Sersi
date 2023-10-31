import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.perms import is_cet, permcheck
from utils.database import (
    SubmittedSuggestion,
    SuggestionVote,
    db_session,
    SuggestionReview,
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
        if interaction.channel.id == self.config.channels.suggestion_discussion:
            interaction.response.defer()

        else:
            interaction.response.defer(ephemeral=True)

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

        suggest_embed.set_footer(suggestion_instance.id)

        review_channel: nextcord.TextChannel = interaction.guild.get_channel(
            self.config.channels.suggestion_review
        )

        await review_channel.send(embed=suggest_embed)

        interaction.followup.send(
            f"{self.config.emotes.success} Your suggestion has been submitted to the Community Engagement Team for review."
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
            choices={"Approve": "approve", "Deny": "deny"},
        ),
    ):
        if not await permcheck(interaction, is_cet):
            return

        pass

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["suggestion-approve"]:
                original_embed = interaction.message.embeds[0]

                interaction.response.defer()

                with db_session(interaction.user) as session:
                    review_instance = SuggestionReview(
                        id=btn_id.split(":", 1)[1],
                        review=True,
                        reviewer=interaction.user.id,
                    )
                    session.add(review_instance)
                    session.commit()

                    suggestion_instance = (
                        session.query(SubmittedSuggestion)
                        .filter_by(id=btn_id.split(":", 1)[1])
                        .first()
                    )
                    review_instance = (
                        session.query(SuggestionReview)
                        .filter_by(id=btn_id.split(":", 1)[1])
                        .first()
                    )

                logging_embed = SersiEmbed(
                    title=f"Suggestion Approved By {interaction.user.display_name}",
                    description=("A suggestion has been approved and published."),
                    fields={
                        "Suggester": f"{interaction.guild.get_member(suggestion_instance.suggester).mention} ({suggestion_instance.suggester})",
                        "Suggestion": suggestion_instance.suggestion_text,
                        "Media URL": suggestion_instance.media_url,
                    },
                    fields={
                        "Approver": f"{interaction.guild.get_member(review_instance.reviewer).mention} ({review_instance.reviewer})",
                    },
                )

                await interaction.guild.get_channel(self.config.channels.logging).send(
                    embed=logging_embed
                )

                if suggestion_instance.media_url:
                    media_url = f"\n{suggestion_instance.media_url}"

                else:
                    media_url = " "

                suggestion_embed = SersiEmbed(
                    title=f"Suggestion from {interaction.guild.get_member(suggestion_instance.suggester).display_name}",
                    description=f"{suggestion_instance.suggestion_text}{media_url}",
                    fields={
                        "Yes Votes": "0",
                        "No Votes": "0",
                        "Approval": "0",
                    },
                )

                yes_vote = Button(
                    label="Yes",
                    emoji="👍",
                    style=nextcord.ButtonStyle.green,
                    custom_id=f"yes-suggest-vote:{suggestion_instance.id}",
                )

                no_vote = Button(
                    label="No",
                    emoji="👎",
                    style=nextcord.ButtonStyle.red,
                    custom_id=f"no-suggest-vote:{suggestion_instance.id}",
                )

                button_view = View(timeout=None)
                button_view.add_item(yes_vote)
                button_view.add_item(no_vote)

                await interaction.guild.get_channel(
                    self.config.channels.suggestion_voting
                ).send(embed=suggestion_embed, view=button_view)

                original_embed.colour = nextcord.Colour.green()

                await interaction.message.edit(embed=original_embed, view=None)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Suggestions(bot, kwargs["config"]))
