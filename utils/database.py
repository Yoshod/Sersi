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
    db_path = f"persistent_data/sersi_{guild_id}.db"
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}", echo=False)

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        """Enable foreign key constraints for SQLite."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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
        join_date (datetime): The date the bot joined the guild. Defaults to the current time.
        leave_date (datetime): The date the bot left the guild.
    """

    __tablename__ = "guilds"

    guild_id = Column(Integer, primary_key=True)
    is_premium = Column(Boolean, default=False)
    was_premium = Column(Boolean, default=False)
    is_testing = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    join_date = Column(DateTime, default=datetime.now(timezone.utc))
    leave_date = Column(DateTime)


### Guild Database Tables ###
def create_db_tables():
    BaseGlobal.metadata.create_all(global_engine)

    global guild_db_manager
    guild_db_manager = GuildDatabaseManager()
