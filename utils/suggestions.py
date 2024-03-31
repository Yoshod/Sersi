import nextcord
import datetime
from utils.database import (
    db_session,
    SubmittedSuggestion,
    SuggestionReview,
    SuggestionVote,
    SuggestionOutcome,
)
from utils.base import get_discord_timestamp
import sqlalchemy.orm.session


def check_if_reviewed(
    interaction: nextcord.Interaction, suggestion_instance: SubmittedSuggestion
):
    """
    Check if a suggestion has been reviewed by querying the database.

    Args:
        interaction (nextcord.Interaction): The interaction object representing the user's interaction with the bot.
        suggestion_instance (SubmittedSuggestion): The suggestion instance to check.

    Returns:
        bool: True if the suggestion has been reviewed, False otherwise.
    """
    with db_session(interaction.user) as session:
        review_check = (
            session.query(SuggestionReview).filter_by(id=suggestion_instance.id).first()
        )

        if review_check:
            return True

        else:
            return False


def check_if_marked(
    interaction: nextcord.Interaction, suggestion_instance: SubmittedSuggestion
):
    """
    Check if a suggestion has been marked as implemented or rejected by querying the database.

    Args:
        interaction (nextcord.Interaction): The interaction object representing the user's interaction with the bot.
        suggestion_instance (SubmittedSuggestion): The suggestion instance to check.

    Returns:
        bool: True if the suggestion has been marked, False otherwise.
    """
    with db_session(interaction.user) as session:
        outcome_check = (
            session.query(SuggestionOutcome)
            .filter_by(id=suggestion_instance.id)
            .first()
        )

        if outcome_check:
            return True

        else:
            return False


def get_suggestion_by_id(interaction: nextcord.Interaction, suggestion_id: str):
    with db_session(interaction.user) as session:
        return session.query(SubmittedSuggestion).filter_by(id=suggestion_id).first()


async def update_embed_votes(original_embed: nextcord.Embed, suggestion_id, session):
    """
    Updates the fields of an embed with the number of yes votes, no votes, and net approval for a given suggestion ID.

    Args:
        original_embed (discord.Embed): The original embed to update.
        suggestion_id (int): The ID of the suggestion to update the fields for.
        session (sqlalchemy.orm.Session): The database session to use for querying.

    Returns:
        discord.Embed: The updated embed.
    """
    yes_votes = (
        session.query(SuggestionVote).filter_by(vote=True, id=suggestion_id).count()
    )
    no_votes = (
        session.query(SuggestionVote).filter_by(vote=False, id=suggestion_id).count()
    )
    net_approval = yes_votes - no_votes

    has_media_url = False
    if original_embed.fields[0].name == "Media URL":
        has_media_url = True

    original_embed.set_field_at(
        index=0 if not has_media_url else 1,
        name="Yes Votes",
        value=f"`{yes_votes}`",
        inline=False,
    )

    original_embed.set_field_at(
        index=1 if not has_media_url else 2,
        name="No Votes",
        value=f"`{no_votes}`",
        inline=False,
    )

    original_embed.set_field_at(
        index=2 if not has_media_url else 3,
        name="Net Approval",
        value=f"`{'+' if net_approval > 0 else ''}{net_approval}`",
        inline=False,
    )

    return original_embed


async def update_embed_outcome(
    interaction: nextcord.Interaction,
    original_embed: nextcord.Embed,
    suggestion_id: int,
    session: sqlalchemy.orm.Session,
):
    """
    Updates the fields of an embed with the outcome of a suggestion.

    Args:
        original_embed (discord.Embed): The original embed to update.
        suggestion_id (int): The ID of the suggestion to update the fields for.
        session (sqlalchemy.orm.Session): The database session to use for querying.

    Returns:
        discord.Embed: The updated embed.
    """
    outcome = session.query(SuggestionOutcome).filter_by(id=suggestion_id).first()

    original_embed.add_field(
        name=f"Marked as {outcome.outcome} by {interaction.guild.get_member(outcome.outcome_reviewer).display_name}",
        value=f"`{outcome.outcome_comment}` {get_discord_timestamp(datetime.datetime.utcnow(), relative=True)}",
        inline=False,
    )

    return original_embed
