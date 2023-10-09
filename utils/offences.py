import typing

from utils.database import db_session, Offence


def fetch_offences_by_partial_name(offence: str) -> list[str]:
    with db_session() as session:
        offences: list[typing.Tuple(str)] = (
            session.query(Offence.offence)
            .filter(Offence.offence.like(f"%{offence}%"))
            .order_by(Offence.offence.asc())
            .limit(25)
            .all()
        )

    return [offence[0] for offence in offences]


def offence_validity_check(offence: str):
    with db_session() as session:
        offence_exists = session.query(Offence).filter_by(offence=offence).first()

    if offence_exists:
        return True
    else:
        return False
