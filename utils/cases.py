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


def fetch_cases_by_partial_id(case_id: str) -> list[str]:
    with db_session() as session:
        cases: list[typing.Tuple(str)] = (
            session.query(Case.id)
            .filter(Case.id.like(f"%{case_id}%"))
            .order_by(Case.created.desc())
            .limit(25)
            .all()
        )

    return [case[0] for case in cases]


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


def create_case_embed(
        case: typing.Type[Case],
        interaction: nextcord.Interaction,
        config: Configuration,
) -> SersiEmbed:
    fields = [{
        "Case": f"`{case.id}`",
        "Type": f"`{case.type}`",
    },{
        "Moderator": f"<@{case.moderator}> `{case.moderator}`",
        "Offender": f"<@{case.offender}> `{case.offender}`",
    }]

    match case:
        case BanCase():
            fields[0]["Active"] = config.emotes.success if case.active else config.emotes.fail
            fields[1]["Ban Type"] = f"`{case.ban_type}`"
            fields.append({"Offence": f"`{case.offence}`"})
            fields.append({"Details": f"{case.details}"})
            if not case.active:
                fields.append({
                    "Unbanned By": f"<@{case.unbanned_by}> `{case.unbanned_by}`",
                    "Unban Reason": f"{case.unban_reason}",
                })
        case BadFaithPingCase():
            fields.append({"Report URL": case.report_url})
        case KickCase():
            fields.append({"Offence": f"`{case.offence}`"})
            fields.append({"Details": f"{case.details}"})
        case ProbationCase():
            fields[0]["Active"] = config.emotes.success if case.active else config.emotes.fail
            fields.append({"Reason": f"{case.reason}"})
            if not case.active:
                fields.append({
                    "Removed By": f"<@{case.removed_by}> `{case.removed_by}`",
                    "Removal Reason": f"{case.removal_reason}"
                })
        case ReformationCase():
            fields[0]["State"] = f"`{case.state}`"
            fields.append({
                "Case Number": f"`{case.case_number}`",
                "Cell Channel": f"<#{case.cell_channel}>"
            })
            fields.append({"Offence": f"`{case.offence}`"})
            fields.append({"Details": f"{case.details}"})
        case SlurUsageCase():
            fields.append({
                "Slur Used": f"`{case.slur_used}`",
                "Report URL": case.report_url
            })
        case TimeoutCase():
            fields.append({"Offence": f"`{case.offence}`"})
            fields.append({"Details": f"{case.details}"})
            fields.append({"Muted Until": f"<t:{int(case.planned_end.timestamp())}:R>"})
        case WarningCase():
            fields.append({"Offence": f"`{case.offence}`"})
            fields.append({"Details": f"{case.details}"})
            fields[0]["Active"] = config.emotes.success if case.active else config.emotes.fail
            if not case.active:
                fields.append({
                    "Deactivated By": f"<@{case.deactivated_by}> `{case.deactivated_by}`",
                    "Deactivate Reason": f"{case.deactivate_reason}",
                })
    
    fields.append({"Timestamp": f"<t:{int(case.created.timestamp())}:R>"})
    if int(case.created.timestamp()) != int(case.modified.timestamp()):
        fields[-1]["Last Modified"] = f"<t:{int(case.modified.timestamp())}:R>"

    offender = interaction.guild.get_member(case.offender)

    return SersiEmbed(
        fields=fields,
        thumbnail_url=offender.display_avatar.url if offender else None,
        footer="Sersi Case Tracking"
    )


def get_case_by_id(case_id: str) -> typing.Type[Case] | None:
    with db_session() as session:
        case: Case = session.query(Case).filter_by(id=case_id).first()
        if not case:
            return None

        match case.type:
            case "Ban":
                return session.query(BanCase).filter_by(id=case_id).first()
            case "Bad Faith Ping":
                return session.query(BadFaithPingCase).filter_by(id=case_id).first()
            case "Kick":
                return session.query(KickCase).filter_by(id=case_id).first()
            case "Probation":
                return session.query(ProbationCase).filter_by(id=case_id).first()
            case "Reformation":
                return session.query(ReformationCase).filter_by(id=case_id).first()
            case "Slur Usage":
                return session.query(SlurUsageCase).filter_by(id=case_id).first()
            case "Timeout":
                return session.query(TimeoutCase).filter_by(id=case_id).first()
            case "Warning":
                return session.query(WarningCase).filter_by(id=case_id).first()
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
            _query = _query.filter_by(type=case_type)
        if moderator_id:
            _query = _query.filter_by(moderator=moderator_id)
        if offender_id:
            _query = _query.filter_by(offender=offender_id)
        if offence:
            _query = _query.filter_by(offence=offence)

        if not scrubbed:
            _query = _query.filter_by(scrubbed=False)
        
        cases = _query.order_by(Case.created.desc()).all()

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
