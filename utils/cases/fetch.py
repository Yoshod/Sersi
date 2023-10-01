import typing

from utils.base import get_page
from utils.config import Configuration
from utils.database import (
    db_session,
    Case,
    BanCase,
    BadFaithPingCase,
    KickCase,
    ProbationCase,
    ReformationCase,
    SlurUsageCase,
    TimeoutCase,
    WarningCase,
)


def get_case_by_id(case_id: str) -> dict[str : typing.Any] | str | None:

    with db_session() as session:
        case: Case = session.query(Case).filter(Case.id == case_id).first()
        if not case:
            return None
        
        match case.type:
            case "Ban":
                return session.query(BanCase).filter(id=case_id).first()
            case "Bad Faith Ping":
                return session.query(BadFaithPingCase).filter(id=case_id).first()
            case "Kick":
                return session.query(KickCase).filter(id=case_id).first()
            case "Probation":
                return session.query(ProbationCase).filter(id=case_id).first()
            case "Reformation":
                return session.query(ReformationCase).filter(id=case_id).first()
            case "Slur Usage":
                return session.query(SlurUsageCase).filter(id=case_id).first()
            case "Timeout":
                return session.query(TimeoutCase).filter(id=case_id).first()
            case "Warn":
                return session.query(WarningCase).filter(id=case_id).first()
            case _:
                return None


def fetch_all_cases(
    config: Configuration,
    page: int,
    per_page: int,
    case_type: typing.Optional[str] = None,
    moderator_id: typing.Optional[int] = None,
    offender_id: typing.Optional[int] = None,
    offence: typing.Optional[str] = None,
    scrubbed: bool = False,
) -> typing.Tuple[typing.Optional[list[Case|None]], int, int]:
    with db_session() as session:
        _query = session.query(Case)
        if case_type:
            _query = _query.filter(type=case_type)
        if moderator_id:
            _query = _query.filter(moderator=moderator_id)
        if offender_id:
            _query = _query.filter(offender=offender_id)
        if offence:
            _query = _query.filter(offence=offence)

        if not scrubbed:
            _query = _query.filter(scrubbed=False)
        
        cases = _query.all()

    if not cases:
        return None, 0, 0

    else:
        return get_page(cases, page, per_page)
