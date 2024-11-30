from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
import random
import json

import nextcord
import sqlalchemy
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, event
from sqlalchemy.orm import Session, scoped_session, sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from dataclass_wizard import JSONWizard

from utils.base import limit_string, encode_snowflake


def random_id() -> str:
    return encode_snowflake(random.getrandbits(64))


# Global database engine and base
global_engine = sqlalchemy.create_engine(
    "sqlite:///databases/sersi_global.db", echo=False
)
BaseGlobal = declarative_base()


@event.listens_for(global_engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    """Enable foreign key constraints for SQLite."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Scoped session for global database
GlobalSession = scoped_session(sessionmaker(bind=global_engine))

# Guild-specific database base and manager
BaseGuild = declarative_base()


def create_guild_engine(guild_id: int) -> sqlalchemy.Engine:
    """Create and configure an SQLAlchemy engine for a specific guild."""
    db_path = f"databases/sersi_{guild_id}.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}", echo=False)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        """Enable foreign key constraints for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    BaseGuild.metadata.create_all(engine)

    return engine


class GuildDatabaseManager:
    """Manages engines and sessions for guild-specific databases."""

    def __init__(self):
        self.engines = {}
        self.sessions = {}

    def get_session(self, guild_id: int) -> Session:
        """Get or create a session for a specific guild."""
        if guild_id not in self.engines:
            self.engines[guild_id] = create_guild_engine(guild_id)

        if guild_id not in self.sessions:
            SessionFactory = scoped_session(sessionmaker(bind=self.engines[guild_id]))
            self.sessions[guild_id] = SessionFactory()

        return self.sessions[guild_id]

    def create_tables(self, guild_id: int):
        """Create tables for the guild-specific database."""
        if guild_id not in self.engines:
            self.engines[guild_id] = create_guild_engine(guild_id)

        # Ensure the tables are created
        BaseGuild.metadata.create_all(self.engines[guild_id])


### Global Database Tables ###
class Guilds(BaseGlobal):
    """
    Represents a Guilds table in the database.

    Attributes:
        guild_id (int): The primary key for the guild.
        is_premium (bool): Indicates if the guild is premium. Defaults to False.
        was_premium (bool): Indicates if the guild was previously premium. Defaults to False.
        is_testing (bool): Indicates if the guild is in testing mode. Defaults to False.
        is_banned (bool): Indicates if the guild is banned. Defaults to False.
        finished_setup (bool): Indicates if the guild has finished setup. Defaults to False.
        join_date (datetime): The date the bot joined the guild. Defaults to the current time.
        leave_date (datetime): The date the bot left the guild.
    """

    __tablename__ = "guilds"

    guild_id = Column(Integer, primary_key=True)
    is_premium = Column(Boolean, default=False)
    was_premium = Column(Boolean, default=False)
    is_testing = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    finished_setup = Column(Boolean, default=False)
    join_date = Column(DateTime, default=datetime.now(timezone.utc))
    leave_date = Column(DateTime)


class Modules(BaseGuild):
    """
    Represents a Modules table in the database.

    Whether a module is enabled or not determines which commands are available to the guild.

    Attributes:
        module_name (str): The name of the module. Primary key.
        enabled (bool): Indicates if the module is enabled. Defaults to False.
    """

    __tablename__ = "modules"

    module_name = Column(String, primary_key=True)
    enabled = Column(Boolean, default=False)


class Case(BaseGuild):
    """
    Represents a Case table in the database.

    Attributes:
    case_id (str): The unique identifier for the case. Primary key.
    case_type (str): The type of case. Not nullable.
    offence (str): The offence that was committed. Not nullable.
    jump_url (str): The URL to jump to the message. Not nullable.
    state (str): The state of the case. Not nullable.
    created_at (datetime): The date and time the case was created. Not nullable.
    modified_at (datetime): The date and time the case was last modified. Not nullable.
    """

    __tablename__ = "cases"

    case_id = Column(String, primary_key=True, default=random_id)
    case_type = Column(String, nullable=False)
    offence = Column(String, nullable=False)
    jump_url = Column(String, nullable=False)
    state = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    modified_at = Column(DateTime, default=datetime.now(timezone.utc))

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
            return f"__{self.id}__ <t:{int(self.created_at.timestamp())}:R>"
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{__name}'"
        )

    def __repr__(self):
        return f"*{self.case_type}* `{self.offence or 'N/A'}`"


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


class WarningCase(Case):
    __tablename__ = "warning_cases"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    justification = Column(String, nullable=False)


class TimeoutCase(Case):
    __tablename__ = "timeout_cases"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    justification = Column(String, nullable=False)
    scheduled_end = Column(DateTime, nullable=False)
    actual_end = Column(DateTime)


class BanCase(Case):
    __tablename__ = "ban_cases"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    justification = Column(String, nullable=False)
    ban_type = Column(String, nullable=False)


class ReformationCase(Case):
    __tablename__ = "reformation_cases"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    justification = Column(String, nullable=False)
    cell_id = Column(Integer, nullable=False)


class BlacklistCase(Case):
    __tablename__ = "blacklist_cases"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    justification = Column(String, nullable=False)
    blacklist_type = Column(String, nullable=False)


class KickCase(Case):
    __tablename__ = "kick_cases"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    justification = Column(String, nullable=False)


class RaidCase(Case):
    __tablename__ = "raid_cases"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)


class CaseModerators(BaseGuild):
    """
    Represents a CaseModerators table in the database.

    Attributes:
        case_id (str): The case ID. Primary key. Foreign key to cases.
        relation_to_case (str): The relation of the moderator to the case. Primary key. Accepts:
            - creation
            - approval
            - objection
            - edit
            - deactivation
            - archival
            - deletion
        moderator_id (int): The moderator ID. Primary key.
    """

    __tablename__ = "case_moderators"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    relation_to_case = Column(String, primary_key=True)
    moderator_id = Column(Integer, primary_key=True)


class CaseReviews(BaseGuild):
    """
    Represents a CaseReviews table in the database.

    Attributes:
        case_id (str): The case ID. Primary key. Foreign key to cases.
        reviewer_id (int): The reviewer ID. Primary key.
        review (str): The review. Not nullable.
        timestamp (datetime): The date and time the review was made. Not nullable.
    """

    __tablename__ = "case_reviews"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    reviewer_id = Column(Integer, primary_key=True)
    outcome = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))


class CaseGroups(BaseGuild):
    """
    Represents a CaseGroups table in the database.

    Attributes:
        case_id (str): The case ID. Primary key. Foreign key to cases.
        group_id (int): The group ID. Primary key.
    """

    __tablename__ = "case_groups"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    group_id = Column(Integer, primary_key=True, default=random_id)


class Raiders(BaseGuild):
    """
    Represents a Raiders table in the database.

    Attributes:
        case_id (str): The case ID. Primary key. Foreign key to cases.
        raider_id (int): The raider ID. Primary key.
    """

    __tablename__ = "raiders"

    case_id = Column(String, ForeignKey("cases.id"), primary_key=True)
    raider_id = Column(Integer, primary_key=True)
    join_time = Column(DateTime, nullable=False)


class Offences(BaseGuild):
    """
    Represents an Offences table in the database.

    Attributes:
        offence_name (str): The name of the offence. Primary key.
        offence_severity (int): The severity of the offence. Not nullable. Scale of 1-10. Defaults to 1. 1 being the least severe and 10 being the most severe.
        offence_description (str): The description of the offence. Nullable.
    """

    __tablename__ = "offences"

    offence_name = Column(String, primary_key=True)
    offence_severity = Column(Integer, nullable=False, default=1)
    offence_description = Column(String)


### Guild Database Tables ###
def create_db_tables():
    BaseGlobal.metadata.create_all(global_engine)

    global guild_db_manager
    guild_db_manager = GuildDatabaseManager()


create_db_tables()
