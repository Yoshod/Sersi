import utils.database as db
from utils.cases import get_reformation_next_case_number


db.create_db_tables()


with db.db_session() as session:
    session.add(db.ReformationCase(
        case_number=get_reformation_next_case_number(),
        offender=1,
        moderator=1,
        offence="test",
        details="test",
        cell_channel=2346556,
        state="open"))
    session.commit()

    case: db.Case = session.query(db.Case).first()
    session.add(db.PeerReview(
        case_id=case.id,
        reviewer=1,
        review_outcome="test",
    ))

    session.commit()
