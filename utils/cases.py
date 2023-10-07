import typing

import nextcord
from sqlalchemy.orm import Session

from utils.base import get_page
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.database import (
    db_session,
    Case,
    CaseAudit,
    BanCase,
    BadFaithPingCase,
    KickCase,
    ProbationCase,
    ReformationCase,
    SlurUsageCase,
    TimeoutCase,
    WarningCase,
    Offence,
)

def get_case_audit_logs(session: Session, case_id: str):
    return session.query(CaseAudit).filter_by(case_id=case_id).all()


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


def create_case_embed(
        case: typing.Type[Case],
        interaction: nextcord.Interaction,
        config: Configuration,
) -> SersiEmbed:
    fields = {
        "Case": f"`{case.id}`",
        "Type": f"`{case.type}`",
        "Moderator": f"<@{case.moderator}> `{case.moderator}`",
        "Offender": f"<@{case.offender}> `{case.offender}`",
    }

    match case:
        case BanCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Ban Type": f"`{case.ban_type}`",
                "Active": config.emotes.success if case.active else config.emotes.fail
            })
            if not case.active:
                fields["Unban Reason"] = f"`{case.unban_reason}`"
        case BadFaithPingCase():
            fields["Report URL"] = case.report_url
        case KickCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
            })
        case ProbationCase():
            fields.update({
                "Reason": f"`{case.reason}`",
                "Active": config.emotes.success if case.active else config.emotes.fail
            })
        case ReformationCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Case Number": f"`{case.case_number}`",
                "Cell Channel": f"<#{case.cell_channel}>",
                "State": f"`{case.state}`"
            })
        case SlurUsageCase():
            fields.update({
                "Slur Used": f"`{case.slur_used}`",
                "Report URL": case.report_url
            })
        case TimeoutCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Muted Until": f"<t:{case.planned_end}:R>"
            })
        case WarningCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Active": config.emotes.success if case.active else config.emotes.fail,
                "Deactivate Reason": f"`{case.deactivate_reason}`",
            })
        
    
    fields["Timestamp"] = f"<t:{case.created}:R>"

    offender = interaction.guild.get_member(case.offender)

    return SersiEmbed(
        fields=fields,
        thumbnail_url=offender.display_avatar.url if offender else None,
        footer_text="Sersi Case Tracking"
    )


def get_case_by_id(case_id: str) -> typing.Type[Case] | None:

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
