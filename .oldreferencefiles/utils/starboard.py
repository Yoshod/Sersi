from utils.database import StarboardStars, db_session


def check_if_starred(star_id: str, user: int):
    with db_session() as session:
        already_starred = (
            session.query(StarboardStars)
            .filter_by(unique_id=star_id, user=user)
            .first()
        )
        return already_starred
