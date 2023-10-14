from datetime import datetime
from typing import Any

import nextcord
from nextcord.abc import GuildChannel
import sqlalchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import shortuuid


_engine = sqlalchemy.create_engine("sqlite:///persistent_data/sersi.db", echo=True)
_Base = declarative_base()


def db_session(owner: int | nextcord.User | nextcord.Member = None):
    session = Session(_engine)

    match owner:
        case nextcord.User() | nextcord.Member():
            session.owner_id = owner.id
        case int():
            session.owner_id = owner
        case _:
            session.owner_id = 0

    return session


### Case Models ###


class Case(_Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    scrubbed = Column(Boolean, default=False)

    offender = Column(Integer, nullable=False)
    moderator = Column(Integer, nullable=False)
    offence = Column(String, ForeignKey("offences.offence"))

    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.id is None:
            self.id = shortuuid.uuid()

    def __setattr__(self, __name: str, __value: Any):
        old_value = self.__dict__.get(__name)
        super().__setattr__(__name, __value)
        session: Session = Session.object_session(self)
        if session and old_value != __value:
            self.modified = datetime.utcnow()
            session.add(
                CaseAudit(
                    id=shortuuid.uuid(),
                    case_id=self.id,
                    field=__name,
                    old_value=old_value,
                    new_value=__value,
                    author=session.owner_id,
                    timestamp=self.modified,
                )
            )

    def __repr__(self):
        return f"{self.type} <t:{int(self.created.timestamp())}:R>"


class CaseAudit(_Base):
    __tablename__ = "cases_audit"

    id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)

    field = Column(String, nullable=False)
    old_value = Column(String, nullable=False)
    new_value = Column(String, nullable=False)

    author = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.field} <t:{int(self.timestamp.timestamp())}:R>"


class BadFaithPingCase(Case):
    __tablename__ = "bad_faith_ping_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    report_url = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Ping"}


class BanCase(Case):
    __tablename__ = "ban_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    active = Column(Boolean, default=True)
    details = Column(String)
    ban_type = Column(String)
    yes_voters = Column(String)
    no_voters = Column(String)
    unbanned_by = Column(Integer)
    unban_reason = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Ban"}


class KickCase(Case):
    __tablename__ = "kick_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    details = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Kick"}


class ProbationCase(Case):
    __tablename__ = "probation_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    reason = Column(String)
    active = Column(Boolean, default=True)
    removed_by = Column(Integer)
    removal_reason = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Probation"}


class ReformationCase(Case):
    __tablename__ = "reformation_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    details = Column(String)
    case_number = Column(Integer, nullable=False)
    cell_channel = Column(Integer)
    state = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Reformation"}


class SlurUsageCase(Case):
    __tablename__ = "slur_usage_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    slur_used = Column(String)
    report_url = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Slur Usage"}


class TimeoutCase(Case):
    __tablename__ = "timeout_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    details = Column(String)
    duration = Column(Integer, nullable=False)
    planned_end = Column(DateTime, nullable=False)
    actual_end = Column(DateTime)
    removed_by = Column(Integer)
    removal_reason = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Timeout"}


class WarningCase(Case):
    __tablename__ = "warning_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    active = Column(Boolean, default=True)
    details = Column(String)
    deactivated_by = Column(Integer)
    deactivate_reason = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Warning"}


class ScrubbedCase(_Base):
    __tablename__ = "scrubbed_cases"

    case_id = Column(
        String, ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True
    )

    scrubber = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PeerReview(_Base):
    __tablename__ = "peer_reviews"

    id = Column(String, primary_key=True, default=shortuuid.uuid)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)

    reviewer = Column(Integer, nullable=False)
    review_outcome = Column(String, nullable=False)
    review_comment = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class CaseApproval(_Base):
    __tablename__ = "case_approvals"

    id = Column(String, primary_key=True, default=shortuuid.uuid)
    case_id = Column(
        String, ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True
    )

    action = Column(String, nullable=False)
    approval_type = Column(String)
    approver = Column(Integer, nullable=False)
    comment = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class Offence(_Base):
    __tablename__ = "offences"

    offence = Column(String, primary_key=True)
    punishments = Column(String)
    warn_severity = Column(Integer)
    detail = Column(String)
    group = Column(String)

    def __getattr__(self, __name: str) -> Any:
        if __name == "punishment_list":
            return self.punishments.split("|")
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{__name}'"
        )

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name == "punishments" and isinstance(__value, list):
            __value = "|".join(__value)
        return super().__setattr__(__name, __value)


### Note Models ###


class Note(_Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=shortuuid.uuid)
    author = Column(Integer, nullable=False)
    member = Column(Integer, nullable=False)
    content = Column(String, nullable=False)

    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)

    def __setattr__(self, __name: str, __value: Any) -> None:
        old_value = self.__dict__.get(__name)
        super().__setattr__(__name, __value)
        session: Session = Session.object_session(self)
        if session and old_value != __value:
            self.modified = datetime.utcnow()
            session.add(
                NoteEdits(
                    note_id=self.id,
                    old_content=old_value,
                    new_content=__value,
                    author=session.owner_id,
                    timestamp=self.modified,
                )
            )


class NoteEdits(_Base):
    __tablename__ = "note_edits"

    id = Column(String, primary_key=True, default=shortuuid.uuid)
    note_id = Column(String, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)

    old_content = Column(String, nullable=False)
    new_content = Column(String, nullable=False)

    author = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


### Ticket Models ###


class Ticket(_Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=shortuuid.uuid)
    active = Column(Boolean, default=True)
    escalation_level = Column(String, nullable=False)

    creator = Column(Integer, nullable=False)
    channel = Column(Integer, nullable=False)
    category = Column(String, ForeignKey("ticket_categories.category"))
    subcategory = Column(String, ForeignKey("ticket_categories.subcategory"))

    opening_comment = Column(String)
    closing_comment = Column(String)

    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow)
    closed = Column(DateTime)

    def __setattr__(self, __name: str, __value: Any):
        old_value = self.__dict__.get(__name)
        super().__setattr__(__name, __value)
        session: Session = Session.object_session(self)
        if session and old_value != __value:
            self.modified = datetime.utcnow()
            session.add(
                TicketAudit(
                    id=shortuuid.uuid(),
                    ticket_id=self.id,
                    field=__name,
                    old_value=old_value,
                    new_value=__value,
                    author=session.owner_id,
                    timestamp=self.modified,
                )
            )


class TicketAudit(_Base):
    __tablename__ = "tickets_audit"

    id = Column(String, primary_key=True, default=shortuuid.uuid)
    ticket_id = Column(
        String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )

    field = Column(String, nullable=False)
    old_value = Column(String, nullable=False)
    new_value = Column(String, nullable=False)

    author = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class TicketSurvey(_Base):
    __tablename__ = "ticket_surveys"

    ticket_id = Column(
        String, ForeignKey("tickets.id", ondelete="CASCADE"), primary_key=True
    )
    member = Column(Integer, primary_key=True)

    rating = Column(Integer)
    comment = Column(String)

    created = Column(DateTime, default=datetime.utcnow)
    received = Column(DateTime)


class TicketCategory(_Base):
    __tablename__ = "ticket_categories"

    category = Column(String, primary_key=True)
    subcategory = Column(String, primary_key=True)


### Alert models ###
class Alert(_Base):
    __tablename__ = "alerts"

    id = Column(String, primary_key=True, default=shortuuid.uuid)

    alert_type = Column(String, nullable=False)
    report_url = Column(String, nullable=False)

    creation_time = Column(DateTime, default=datetime.utcnow)
    response_time = Column(DateTime)


class Slur(_Base):
    __tablename__ = "slurs"

    slur = Column(String, primary_key=True)
    added = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, nullable=False)


class Goodword(_Base):
    __tablename__ = "goodwords"

    goodword = Column(String, primary_key=True)
    slur = Column(String, ForeignKey("slurs.slur"))
    added = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, nullable=False)


def create_db_tables():
    _Base.metadata.create_all(_engine)


def to_db_type(value):
    match value:
        case nextcord.User() | nextcord.Member() | nextcord.Role() | GuildChannel():
            return value.id
        case _:
            return value
