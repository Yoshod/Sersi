from datetime import datetime
from typing import Any

import nextcord
from nextcord.abc import GuildChannel
import sqlalchemy
from sqlalchemy import Column, DateTime, Integer, ForeignKey, String
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_dirty
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


class CaseAudit(_Base):
    __tablename__ = "cases_audit"

    id = Column(String, primary_key=True)
    
    case_id = Column(String, ForeignKey('cases.id'), nullable=False)

    field = Column(String, nullable=False)
    old_value = Column(String, nullable=False)
    new_value = Column(String, nullable=False)

    author = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Case(_Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)

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
            

class ReformationCase(Case):
    __tablename__ = "reformation_cases"

    id = Column(String, ForeignKey('cases.id'), primary_key=True)

    offender = Column(Integer, nullable=False)
    moderator = Column(Integer, nullable=False)

    reason = Column(String, nullable=False)

    case_number = Column(Integer, nullable=False)
    cell_channel = Column(Integer)

    state = Column(String)

    __mapper_args__ = {"polymorphic_identity": "Reformation"}


def create_db_tables():
    _Base.metadata.create_all(_engine)


def to_db_type(value):
    match value:
        case nextcord.User()|nextcord.Member()|nextcord.Role()|GuildChannel():
            return value.id
        case _:
            return value
