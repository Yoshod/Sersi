from utils.database import db_session, Case, WarningCase


def delete_case(case_id: str):
    with db_session() as session:
        case: Case = session.query(Case).filter(Case.id == case_id).first()
        if not case:
            return False

        session.delete(case)
        session.commit()

    return True


def delete_warn(case_id: str):
    with db_session() as session:
        case: WarningCase =\
            session.query(WarningCase).filter(WarningCase.id == case_id).first()

        if not case:
            return False

        session.delete(case)
        session.commit()
    
    return True
