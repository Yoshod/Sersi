from utils.database import db_session, Case, Offence


def fetch_cases_by_partial_id(case_id: str):
    with db_session() as session:
        cases: list[str] = (
            session.query(Case.id)
            .filter(Case.id.like(f"%{case_id}%"))
            .order_by(Case.created.desc())
            .limit(25)
            .all()
        )

    return cases

def fetch_offences_by_partial_name(offence: str) -> list[str]:
    with db_session() as session:
        offences: list[str] = (
            session.query(Offence.offence)
            .filter(Offence.offence.like(f"%{offence}%"))
            .order_by(Offence.offence.asc())
            .limit(25)
            .all()
        )

    return offences
