import sqlite3
import time

import nextcord

from utils.base import create_unique_id
from utils.config import Configuration


def create_case(config: Configuration, unique_id: str, case_type: str, timestamp: int):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        INSERT INTO cases (id, type, timestamp)
        VALUES ({unique_id}, {case_type}, {timestamp})"""
    )

    conn.commit()
    conn.close()


def create_slur_case(
    config: Configuration,
    slur_used: str,
    report_url: str,
    offender: nextcord.Member,
    moderator: nextcord.Member,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO slur_cases (id, slur_used, report_url, offender, moderator, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (uuid, slur_used, report_url, offender.id, moderator.id, timestamp),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Slur Usage", timestamp),
    )

    conn.commit()
    conn.close()


def create_probation_case(
    config: Configuration,
    offender: nextcord.Member,
    initial_moderator: nextcord.Member,
    approving_moderator: nextcord.Member,
    reason: str,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO probation_cases (id, offender, initial_moderator, approving_moderator, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            uuid,
            offender.id,
            initial_moderator.id,
            approving_moderator.id,
            reason,
            timestamp,
        ),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Probation", timestamp),
    )

    conn.commit()
    conn.close()


def create_reformation_case(
    config: Configuration,
    case_number: int,
    offender: nextcord.Member,
    moderator: nextcord.Member,
    reformation_cell: nextcord.TextChannel,
    reason: str,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reformation_cases (id, case_number, offender, moderator, cell_id, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uuid,
            case_number,
            offender.id,
            moderator.id,
            reformation_cell.id,
            reason,
            timestamp,
        ),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Reformation", timestamp),
    )

    conn.commit()
    conn.close()


def create_bad_faith_ping_case(
    config: Configuration,
    report_url: str,
    offender: nextcord.Member,
    moderator: nextcord.Member,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO bad_faith_ping_cases (id, report_url, offender, moderator, timestamp) VALUES (?, ?, ?, ?, ?)",
        (uuid, report_url, offender.id, moderator.id, timestamp),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Bad Faith Ping", timestamp),
    )

    conn.commit()
    conn.close()


def create_warn_case(
    config: Configuration,
    offender: nextcord.Member,
    moderator: nextcord.Member,
    offence: str,
    detail: str,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO warn_cases (id, offender, moderator, offence, details, active, timestamp, deactive_reason) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (uuid, offender.id, moderator.id, offence, detail, True, timestamp, None),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Warn", timestamp),
    )

    conn.commit()
    conn.close()

    return uuid


def create_kick_case(
    config: Configuration,
    offender: nextcord.Member,
    moderator: nextcord.Member,
    reason: str,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO kick_cases (id, offender, moderator, reason, timestamp) VALUES (?, ?, ?, ?, ?)",
        (uuid, offender.id, moderator.id, reason, timestamp),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Kick", timestamp),
    )

    conn.commit()
    conn.close()

    return uuid
