import nextcord
from utils.database import db_session, SubmittedSuggestion, SuggestionReview


def check_if_reviewed(
    interaction: nextcord.Interaction, suggestion_instance: SubmittedSuggestion
):
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
