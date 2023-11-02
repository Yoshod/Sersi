import nextcord
from utils.database import (
    db_session,
    SubmittedSuggestion,
    SuggestionReview,
    SuggestionVote,
)


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


def get_suggestion_by_id(interaction: nextcord.Interaction, suggestion_id: str):
    with db_session(interaction.user) as session:
        return session.query(SubmittedSuggestion).filter_by(id=suggestion_id).first()


async def update_embed_fields(original_embed, suggestion_id, session):
    """
    Updates the fields of an embed with the number of yes votes, no votes, and net approval for a given suggestion ID.

    Args:
        original_embed (discord.Embed): The original embed to update.
        suggestion_id (int): The ID of the suggestion to update the fields for.
        session (sqlalchemy.orm.Session): The database session to use for querying.

    Returns:
        discord.Embed: The updated embed.
    """
    original_embed.set_field_at(
        index=0,
        name="Yes Votes",
        value=f"`{session.query(SuggestionVote).filter_by(vote=True, id=suggestion_id).count()}`",
        inline=False,
    )

    original_embed.set_field_at(
        index=1,
        name="No Votes",
        value=f"`{session.query(SuggestionVote).filter_by(vote=False, id=suggestion_id).count()}`",
        inline=False,
    )

    original_embed.set_field_at(
        index=2,
        name="Net Approval",
        value=f"`{session.query(SuggestionVote).filter_by(vote=True, id=suggestion_id).count() - session.query(SuggestionVote).filter_by(vote=False, id=suggestion_id).count()}`",
        inline=False,
    )

    return original_embed
