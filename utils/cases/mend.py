import nextcord

from utils.database import db_session, Case, WarningCase, ScrubbedCase


def scrub_case(case_id: str, scrubber: nextcord.Member, reason: str) -> Case|False|None:
    with db_session(scrubber) as session:
        case: Case = session.query(Case).filter(Case.id == case_id).first()
        if not case:
            return None

        if case.scrubbed:
            return False

        case.scrubbed = True
        session.add(
            ScrubbedCase(
                case_id=case_id,
                scrubber=scrubber.id,
                reason=reason
            )
        )

        session.commit()

    return case


def deactivate_warn(case_id: str, user: nextcord.Member, reason: str) -> WarningCase|False|None:
    with db_session(user) as session:
        case: WarningCase =\
            session.query(WarningCase).filter(WarningCase.id == case_id).first()

        if not case:
            return None

        if not case.active:
            return False

        case.active = False
        case.deactivate_reason = reason
        session.commit()
    
    return case
