import nextcord

from utils.database import db_session, ReformationCase, SlurUsageCase, Offence, WarningCase


def slur_virgin(user: nextcord.User) -> bool:
    with db_session() as session:
        slur_cases = session.query(SlurUsageCase).filter_by(offender=user.id).all()

    if slur_cases:
        return False

    else:
        return True


def slur_history(user: nextcord.User, slur: list):
    with db_session() as session:
        slur_cases: SlurUsageCase = (
            session.query(SlurUsageCase)
            .filter_by(offender=user.id, slur=slur)
            .limit(5).all()
        )

    return slur_cases


def offence_validity_check(offence: str):
    with db_session() as session:
        offence_exists = session.query(Offence).filter_by(offence=offence).first()

    if offence_exists:
        return True
    else:
        return False


def get_reformation_next_case_number():
    with db_session() as session:
        last_case: ReformationCase = (
            session.query(ReformationCase)
            .order_by(ReformationCase.case_number.desc())
            .first()
        )

    if last_case is None:
        return 1
    
    return last_case.case_number + 1
