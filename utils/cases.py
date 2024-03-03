import typing

import nextcord
from nextcord.ui import Button, View
import datetime
from sqlalchemy import or_

from utils.base import get_page, decode_snowflake, encode_button_id, encode_snowflake
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.database import (
    db_session,
    Case,
    CaseAudit,
    BanCase,
    BadFaithPingCase,
    BlacklistCase,
    KickCase,
    ProbationCase,
    ReformationCase,
    SlurUsageCase,
    TimeoutCase,
    WarningCase,
    ScrubbedCase,
    RelatedCase,
    PeerReview,
)


def fetch_cases_by_partial_id(case_id: str) -> list[str]:
    with db_session() as session:
        cases: list[typing.Tuple[str]] = (
            session.query(Case.id)
            .filter(Case.id.ilike(f"%{case_id}%"))
            .order_by(Case.created.desc())
            .limit(25)
            .all()
        )

    return [case[0] for case in cases]


def create_case_embed(
    case: typing.Type[Case],
    interaction: nextcord.Interaction,
    config: Configuration,
) -> SersiEmbed:
    fields = [
        {
            "Case ID": f"`{case.id}`",
            "Type": f"`{case.type}`",
            "Timestamp": f"<t:{int(case.created.timestamp())}:R>",
        },
        {
            "Moderator": f"<@{case.moderator}> `{case.moderator}`",
            "Offender": f"<@{case.offender}> `{case.offender}`",
            "Offence": f"{case.offence}",
        },
    ]

    match case:
        case BadFaithPingCase():
            fields[1].popitem()
            fields[1].update({"Report": case.report_url})
        case BanCase():
            fields.append({"Details": f"{case.details}"})
            fields.append(
                {
                    "Ban Type": case.ban_type,
                    "Active": config.emotes.success
                    if case.active
                    else config.emotes.fail,
                }
            )

            if case.active is False:
                fields[-1].update(
                    {
                        "Unbanned By": f"<@{case.unbanned_by}> `{case.unbanned_by}`",
                        "Unban Reason": f"{case.unban_reason}",
                    }
                )
        case BlacklistCase():
            fields[1].popitem()
            fields[1].update({"Blacklist": case.blacklist})
            fields.append({"Reason": f"{case.reason}"})
            fields.append(
                {"Active": config.emotes.success if case.active else config.emotes.fail}
            )
            if not case.active:
                fields[-1].update(
                    {
                        "Removed By": f"<@{case.removed_by}> `{case.removed_by}`",
                        "Removal Reason": f"{case.removal_reason}",
                    }
                )
        case KickCase():
            fields.append({"Details": f"{case.details}"})
        case ProbationCase():
            fields.append({"Reason": f"{case.reason}"})
            fields.append(
                {
                    "Active:": config.emotes.success
                    if case.active
                    else config.emotes.fail
                }
            )
            if not case.active:
                fields[-1].update(
                    {
                        "Removed By": f"<@{case.removed_by}> `{case.removed_by}`",
                        "Removal Reason": f"{case.removal_reason}",
                    }
                )
        case ReformationCase():
            fields.append({"Details": f"{case.details}"})
            fields.append(
                {
                    "State": f"`{case.state}`",
                    "Case Number": f"`{case.case_number}`",
                    "Cell Channel": f"<#{case.cell_channel}>",
                }
            )
        case SlurUsageCase():
            fields[1].popitem()
            fields[1].update({"Report": case.report_url})
            fields.append({"Slur(s)": f"{case.slur_used}"})
        case TimeoutCase():
            # determine if the case is active
            active = case.planned_end > datetime.datetime.utcnow()
            if case.actual_end is not None:
                active = False

            fields.append({"Details": f"{case.details}"})
            fields.append(
                {
                    "Muted Until": f"<t:{int(case.planned_end.timestamp())}:R>",
                    "Duration": f"{case.duration}",
                    "Active": config.emotes.success if active else config.emotes.fail,
                }
            )
            if case.actual_end is not None:
                fields.append(
                    {
                        "Removed At": f"<t:{int(case.actual_end.timestamp())}:R>",
                        "Removed By": f"<@{case.removed_by}> `{case.removed_by}`",
                        "Removal Reason": f"{case.removal_reason}",
                    }
                )
        case WarningCase():
            fields.append({"Details": f"{case.details}"})
            fields.append(
                {"Active": config.emotes.success if case.active else config.emotes.fail}
            )
            if not case.active:
                fields[-1].update(
                    {
                        "Deactivated By": f"<@{case.deactivated_by}> `{case.deactivated_by}`",
                        "Deactivate Reason": f"{case.deactivate_reason}",
                    }
                )

    if case.type in ["Ban", "Timeout", "Warning"]:
        with db_session() as session:
            review: PeerReview = (
                session.query(PeerReview).filter_by(case_id=case.id).first()
            )

        if review:
            fields.append(
                {
                    "Review Outcome": config.emotes.success
                    if review.review_outcome == "Approved"
                    else config.emotes.fail,
                    "Reviewer": f"<@{review.reviewer}> `{review.reviewer}`",
                }
            )

            if review.review_comment:
                fields.append({"Review Comment": review.review_comment})

    if case.scrubbed:
        with db_session() as session:
            scrub_record: ScrubbedCase = (
                session.query(ScrubbedCase).filter_by(case_id=case.id).first()
            )
        if scrub_record:
            fields.append(
                {
                    "Scrubbed At": f"<t:{int(scrub_record.timestamp.timestamp())}:R>",
                    "Scrubbed By": f"<@{scrub_record.scrubber}> `{scrub_record.scrubber}`",
                    "Scrub Reason": f"{scrub_record.reason}",
                }
            )
        else:
            fields.append(
                {
                    "Last Modified": f"<t:{int(case.modified.timestamp())}:R>",
                    "Scrubbed": config.emotes.success,
                    "Error": "*Case marked as scrubbed but no scrub record found.*",
                }
            )
    elif int(case.created.timestamp()) != int(case.modified.timestamp()):
        fields.append({"Last Modified": f"<t:{int(case.modified.timestamp())}:R>"})

    offender = interaction.guild.get_member(case.offender)

    embed = SersiEmbed(
        fields=fields,
        thumbnail_url=offender.display_avatar.url if offender else None,
        footer="Sersi Case Tracking",
    )

    if moderator := interaction.guild.get_member(case.moderator):
        embed.set_author(
            name=moderator.display_name,
            icon_url=moderator.display_avatar.url,
        )
    return embed


def get_case_by_id(case_id: str) -> typing.Type[Case] | None:
    with db_session() as session:
        case: Case = session.query(Case).filter_by(id=case_id).first()
        if not case:
            return None

        match case.type:
            case "Bad Faith Ping":
                return session.query(BadFaithPingCase).filter_by(id=case_id).first()
            case "Ban":
                return session.query(BanCase).filter_by(id=case_id).first()
            case "Blacklist":
                return session.query(BlacklistCase).filter_by(id=case_id).first()
            case "Ping":
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
    related_id: typing.Optional[str] = None,
) -> typing.Tuple[typing.Optional[list[Case | None]], int, int]:
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

        if related_id:
            _query = _query.filter(
                or_(
                    Case.id.in_(
                        session.query(RelatedCase.case_id).filter_by(
                            related_id=related_id
                        )
                    ),
                    Case.id.in_(
                        session.query(RelatedCase.related_id).filter_by(
                            case_id=related_id
                        )
                    ),
                )
            )

        cases = _query.order_by(Case.created.desc()).all()

        if not cases:
            return None, 0, 0

        page_cases, page, pages = get_page(cases, page, per_page)
        for case in page_cases:
            repr(case)  # load case type specific attributes if needed for list
        return page_cases, page, pages


def get_case_audit_logs(
    config: Configuration, page: int, per_page: int, case_id: str
) -> typing.Tuple[typing.Optional[list[CaseAudit | None]], int, int]:
    with db_session() as session:
        logs: list[CaseAudit] = (
            session.query(CaseAudit).filter_by(case_id=case_id).all()
        )

    if not logs:
        return None, 0, 0

    return get_page(logs, page, per_page)


def slur_virgin(user: nextcord.User) -> bool:
    with db_session() as session:
        slur_cases = session.query(SlurUsageCase).filter_by(offender=user.id).all()

    if slur_cases:
        return False

    else:
        return True


def slur_history(user: nextcord.User, slurs: list[str]) -> list[SlurUsageCase]:
    with db_session() as session:
        slur_cases: SlurUsageCase = (
            session.query(SlurUsageCase)
            .filter_by(offender=user.id)
            .filter(SlurUsageCase.slur_used.in_(slurs))
            .limit(5)
            .all()
        )

    return slur_cases


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


def validate_case_edit(
    interaction: nextcord.Interaction,
    config: Configuration,
    case_type: str,
    case_id: str,
    offence: str | None,
    detail: str | None,
    duration: int | None,
    timespan: str | None,
):
    if not offence and not detail and not duration and not timespan:
        return (
            False,
            f"{config.emotes.fail} You must provide at least one value you want to edit.",
        )

    if (case_type == "Warning" or case_type == "Ban") and (duration or timespan):
        return (
            False,
            f"{config.emotes.fail} You provided an invalid value for the case type {case_type}.",
        )

    if case_type == "Timeout" and (duration is None and timespan is not None):
        return (
            False,
            f"{config.emotes.fail} You provided an invalid value for the case type {case_type}.",
        )

    if case_type == "Timeout" and (duration is not None and timespan is None):
        return (
            False,
            f"{config.emotes.fail} You provided an invalid value for the case type {case_type}.",
        )

    sersi_case: Case = get_case_by_id(case_id)
    if not sersi_case:
        return False, f"{config.emotes.fail} {case_id} is not a valid case."

    if case_type == "Timeout" and (duration and timespan):
        sersi_case: TimeoutCase = get_case_by_id(case_id)

        if sersi_case.actual_end:
            return False, f"{config.emotes.fail} {case_id} has already ended."

    if sersi_case.type != case_type:
        return (
            False,
            f"{config.emotes.fail} `{sersi_case.id}` is a {sersi_case.type} not {case_type}.",
        )

    return True, None


async def check_if_banned(user_id: int, guild: nextcord.Guild) -> bool:
    with db_session() as session:
        ban_case: BanCase = (
            session.query(BanCase).filter_by(offender=user_id, active=True).first()
        )

    if ban_case:
        return True

    try:
        await guild.fetch_ban(user_id)
        return True

    except nextcord.NotFound:
        return False


async def check_if_timeout(member: nextcord.Member) -> bool:
    return bool(member.communication_disabled_until)


def decode_case_kwargs(kwargs: dict):
    decoded = {**kwargs}

    case_type = decoded.pop("type", None)
    offender_id = decoded.pop("user", None)
    moderator_id = decoded.pop("mod", None)
    related_id = decoded.pop("rel", None)

    if case_type:
        decoded["case_type"] = case_type
    if offender_id:
        decoded["offender_id"] = decode_snowflake(offender_id)
    if moderator_id:
        decoded["moderator_id"] = decode_snowflake(moderator_id)
    if related_id:
        decoded["related_id"] = related_id

    return decoded


class CaseDetailView(View):
    def __init__(self, case: Case):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(
            Button(
                style=nextcord.ButtonStyle.blurple,
                label="Related Cases",
                custom_id=encode_button_id("cases", rel=case.id),
            )
        )
