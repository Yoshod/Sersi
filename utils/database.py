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


def db_session(owner: int|nextcord.User|nextcord.Member = None):
    session = Session(_engine)

    match owner:
        case nextcord.User()|nextcord.Member():
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

    offender = Column(Integer, nullable=False)
    moderator = Column(Integer, nullable=False)
    offence = Column(String, ForeignKey('offences.offence'))

    scrubbed = Column(Boolean, default=False)
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
        if (session and old_value != __value):
            self.modified = datetime.utcnow()
            session.add(CaseAudit(
                id=shortuuid.uuid(),
                case_id=self.id,
                field=__name,
                old_value=old_value,
                new_value=__value,
                author=session.owner_id,
                timestamp=self.modified
            ))


class CaseAudit(_Base):
    __tablename__ = "cases_audit"

    id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey('cases.id'), nullable=False)

    field = Column(String, nullable=False)
    old_value = Column(String, nullable=False)
    new_value = Column(String, nullable=False)

    author = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class BadFaithPingCase(Case):
    __tablename__ = "bad_faith_ping_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    report_url = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Ping"}


class BanCase(Case):
    __tablename__ = "ban_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    active = Column(Boolean, default=True)
    details = Column(String)
    ban_type = Column(String)
    unban_reason = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Ban"}


class KickCase(Case):
    __tablename__ = "kick_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    details = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Kick"}


class ProbationCase(Case):
    __tablename__ = "probation_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    reason = Column(String)
    active = Column(Boolean, default=True)

    __mapper_args__ = {"polymorphic_identity": "Probation"}


class ReformationCase(Case):
    __tablename__ = "reformation_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    details = Column(String)
    case_number = Column(Integer, nullable=False)
    cell_channel = Column(Integer)
    state = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Reformation"}


class SlurUsageCase(Case):
    __tablename__ = "slur_usage_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    slur_used = Column(String)
    report_url = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Slur Usage"}


class TimeoutCase(Case):
    __tablename__ = "timeout_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    details = Column(String)
    duration = Column(Integer)
    planned_end = Column(DateTime)
    actual_end = Column(DateTime)

    __mapper_args__ = {"polymorphic_identity": "Timeout"}


class WarningCase(Case):
    __tablename__ = "warning_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    details = Column(String)
    active = Column(Boolean, default=True)
    deactivate_reason = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Warning"}


class PeerReview(_Base):
    __tablename__ = "peer_reviews"

    id = Column(String, primary_key=True)
    case_id = Column(String, ForeignKey('cases.id'), nullable=False)

    reviewer = Column(Integer, nullable=False)
    review_outcome = Column(String, nullable=False)
    review_comment = Column(String)

    timestamp = Column(DateTime, default=datetime.utcnow)


class DualCustody(_Base):
    __tablename__ = "dual_custody"

    case_id = Column(String, ForeignKey('cases.id'), primary_key=True)
    moderator = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Offence(_Base):
    __tablename__ = "offences"

    offence = Column(String, primary_key=True)

    first_instance = Column(String)
    second_instance = Column(String)
    third_instance = Column(String)

    detail = Column(String)


def create_db_tables():
    _Base.metadata.create_all(_engine)


def to_db_type(value):
    match value:
        case nextcord.User()|nextcord.Member()|nextcord.Role()|GuildChannel():
            return value.id
        case _:
            return value
