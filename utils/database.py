from datetime import datetime
from typing import Any
import random
import re

import nextcord
import sqlalchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.orm import Session, relationship
from sqlalchemy.ext.declarative import declarative_base


from utils.base import limit_string, encode_snowflake


def random_id() -> str:
    return encode_snowflake(random.getrandbits(64))


_engine = sqlalchemy.create_engine("sqlite:///persistent_data/sersi.db")
_Base = declarative_base()


@event.listens_for(_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


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
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __mapper_args__ = {"polymorphic_on": type}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.id is None:
            self.id = random_id()

    def __setattr__(self, __name: str, __value: Any):
        old_value = self.__dict__.get(__name)
        super().__setattr__(__name, __value)
        session: Session = Session.object_session(self)
        if session and old_value != __value:
            session.add(
                CaseAudit(
                    id=random_id(),
                    case_id=self.id,
                    field=__name,
                    old_value=old_value,
                    new_value=__value,
                    author=session.owner_id,
                )
            )

    def __getattr__(self, __name: str) -> Any:
        if __name == "list_entry_header":
            return f"__{self.id}__ <t:{int(self.created.timestamp())}:R>"
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{__name}'"
        )

    def __repr__(self):
        return f"*{self.type}* <@{self.offender}> `{self.offence or 'N/A'}`"


class CaseAudit(_Base):
    __tablename__ = "cases_audit"

    id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)

    field = Column(String, nullable=False)
    old_value = Column(String)
    new_value = Column(String)

    author = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<t:{int(self.timestamp.timestamp())}:R> {self.field}"


class BadFaithPingCase(Case):
    __tablename__ = "bad_faith_ping_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    report_url = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Ping"}


class BlacklistCase(Case):
    __tablename__ = "blacklist_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    active = Column(Boolean, default=True)
    blacklist = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    removed_by = Column(Integer)
    removal_reason = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Blacklist"}

    def __repr__(self):
        return f"*{self.type}* <@{self.offender}> `{self.blacklist}`"


class BanCase(Case):
    __tablename__ = "ban_cases"

    id = Column(String, ForeignKey("cases.id"), primary_key=True)

    active = Column(Boolean, default=None)
    details = Column(String)
    ban_type = Column(String)
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

    def __repr__(self):
        return f"*{self.type}* <@{self.offender}> ||{self.slur_used}||"


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

    id = Column(String, primary_key=True, default=random_id)
    case_id = Column(String, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)

    reviewer = Column(Integer, nullable=False)
    review_outcome = Column(String, nullable=False)
    review_comment = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class CaseApproval(_Base):
    __tablename__ = "case_approvals"

    id = Column(String, primary_key=True, default=random_id)
    case_id = Column(
        String, ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True
    )

    action = Column(String, nullable=False)
    approval_type = Column(String)
    approver = Column(Integer, nullable=False)
    comment = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class SubmittedSuggestion(_Base):
    __tablename__ = "submitted_suggestions"

    id = Column(String, primary_key=True, default=random_id)

    suggestion_text = Column(String, nullable=False)
    media_url = Column(String)
    suggester = Column(Integer, nullable=False)
    vote_message_id = Column(Integer)

    timestamp = Column(DateTime, default=datetime.utcnow)


class SuggestionReview(_Base):
    __tablename__ = "suggestion_review"

    id = Column(String, ForeignKey("submitted_suggestions.id"), primary_key=True)
    review = Column(Boolean, nullable=False)
    reviewer = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)


class SuggestionVote(_Base):
    __tablename__ = "suggestion_vote"

    id = Column(String, ForeignKey("submitted_suggestions.id"), primary_key=True)
    voter = Column(Integer, primary_key=True)

    vote = Column(Boolean, nullable=False)


class SuggestionOutcome(_Base):
    __tablename__ = "suggestion_outcome"

    id = Column(String, ForeignKey("submitted_suggestions.id"), primary_key=True)
    outcome = Column(String, nullable=False)
    outcome_comment = Column(String, nullable=False)
    outcome_reviewer = Column(Integer, nullable=False)
    outcome_timestamp = Column(DateTime, default=datetime.utcnow)


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

    id = Column(String, primary_key=True, default=random_id)
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
            session.add(
                NoteEdits(
                    note_id=self.id,
                    old_content=old_value,
                    new_content=__value,
                    author=session.owner_id,
                )
            )

    def __getattr__(self, __name: str) -> Any:
        if __name == "list_entry_header":
            return f"{self.id} <t:{int(self.created.timestamp())}:R>"
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{__name}'"
        )

    def __repr__(self):
        link: re.Match
        if link := re.match(
            r"https://discord.com/channels/[0-9]*/[0-9]*/[0-9]*", self.content
        ):
            after_link = self.content[link.end() :].lstrip(" \n")
            return f"<@{self.member}> {link.group(0)}\n```{limit_string(after_link, 224) or 'N/A'}```"

        return f"<@{self.member}>\n```{limit_string(self.content, 224) or 'N/A'}```"


class NoteEdits(_Base):
    __tablename__ = "note_edits"

    id = Column(String, primary_key=True, default=random_id)
    note_id = Column(String, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False)

    old_content = Column(String, nullable=False)
    new_content = Column(String, nullable=False)

    author = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


### Ticket Models ###


class Ticket(_Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=random_id)
    active = Column(Boolean, default=True)
    escalation_level = Column(String, nullable=False)

    creator = Column(Integer, nullable=False)
    channel = Column(Integer, nullable=False)
    category = Column(String)
    subcategory = Column(String)

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
            session.add(
                TicketAudit(
                    id=random_id(),
                    ticket_id=self.id,
                    field=__name,
                    old_value=old_value,
                    new_value=__value,
                    author=session.owner_id,
                )
            )


class TicketAudit(_Base):
    __tablename__ = "tickets_audit"

    id = Column(String, primary_key=True, default=random_id)
    ticket_id = Column(
        String, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False
    )

    field = Column(String, nullable=False)
    old_value = Column(String)
    new_value = Column(String)

    author = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<t:{int(self.timestamp.timestamp())}:R> {self.field}"


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

    id = Column(String, primary_key=True, default=random_id)

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
    slur = Column(String, ForeignKey("slurs.slur", ondelete="CASCADE"))
    added = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, nullable=False)


### Staff Records ###


class StaffBranches(_Base):
    __tablename__ = "staff_branches"

    branch = Column(String, primary_key=True)


class StaffRoles(_Base):
    __tablename__ = "staff_roles"

    role_id = Column(Integer, primary_key=True)
    role_name = Column(String, nullable=False)
    branch = Column(String, ForeignKey("staff_branches.branch"), nullable=False)
    rank = Column(Integer, nullable=False)


class StaffMembers(_Base):
    __tablename__ = "staff_members"

    member = Column(Integer, primary_key=True)
    active = Column(Boolean, default=True)


class ActiveStaff(_Base):
    __tablename__ = "active_staff"

    member = Column(Integer, ForeignKey("staff_members.member"), primary_key=True)
    branch = Column(String, ForeignKey("staff_branches.branch"))
    role = Column(String, ForeignKey("staff_roles.role_id"))
    joined = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, nullable=False)


class FormerStaff(_Base):
    __tablename__ = "former_staff"

    member = Column(Integer, ForeignKey("staff_members.member"), primary_key=True)
    branch = Column(String, ForeignKey("staff_branches.branch"))
    role = Column(String, ForeignKey("staff_roles.role_id"))
    joined = Column(DateTime, default=datetime.utcnow)
    added_by = Column(Integer, nullable=False)
    left = Column(DateTime, default=datetime.utcnow)
    removed_by = Column(Integer, nullable=False)
    discharge_type = Column(String, nullable=False)
    discharge_reason = Column(String, nullable=False)


class StaffStrikes(_Base):
    __tablename__ = "staff_strikes"

    offender = Column(Integer, ForeignKey("staff_members.member"), primary_key=True)
    strike_type = Column(String, nullable=False)
    striker = Column(Integer, foreign_key="staff_members.member", nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    active = Column(Boolean, default=True)


### Vote Models ###


class VoteDetails(_Base):
    __tablename__ = "vote_details"

    vote_id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, ForeignKey("cases.id"), nullable=False)

    vote_type = Column(String, nullable=False)
    vote_url = Column(String, nullable=False)

    started_by = Column(Integer, nullable=False)
    planned_end = Column(DateTime, nullable=False)
    actual_end = Column(DateTime)
    outcome = Column(String)

    created = Column(DateTime, default=datetime.utcnow)
    modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    case = relationship("Case", backref="votes")
    votes = relationship("VoteRecord", backref="vote_detail")


class VoteRecord(_Base):
    __tablename__ = "vote_records"

    vote_id = Column(Integer, ForeignKey("vote_details.vote_id"), primary_key=True)
    voter = Column(Integer, primary_key=True)

    vote = Column(String, nullable=False)
    comment = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class StaffBlacklist(_Base):
    # TODO: remove in 5.2.0
    __tablename__ = "staff_blacklist"

    blacklisted_user = Column(Integer, primary_key=True)
    staff_member = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)


class MemberLevel(_Base):
    __tablename__ = "member_levels"

    member = Column(Integer, primary_key=True)
    level = Column(Integer, default=0)
    xp = Column(Integer, default=0)


class ExperienceJournal(_Base):
    __tablename__ = "experience_journal"

    member = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, primary_key=True, default=datetime.utcnow)
    xp_type = Column(String, primary_key=True)
    xp = Column(Integer, nullable=False)


def create_db_tables():
    _Base.metadata.create_all(_engine)
