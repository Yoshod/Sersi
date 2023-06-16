import sqlite3
import typing

import nextcord

from utils.base import get_page
from utils.config import Configuration


def get_case_by_id(
    config: Configuration, case_id: str, scrubbed: bool
) -> dict[str : typing.Any] | str | None:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if scrubbed:
        cursor.execute("SELECT * FROM scrubbed_cases WHERE id=?", (case_id,))
        try:
            row = cursor.fetchone()

            return {
                "ID": f"{row[0]}",
                "Case Type": f"{row[1]}",
                "Offender ID": row[2],
                "Scrubber ID": row[3],
                "Scrub Reason": f"{row[4]}",
                "Timestamp": row[5],
            }

        except TypeError:
            cursor.close()
            return None

    cursor.execute("SELECT * FROM cases WHERE id=?", (case_id,))

    try:
        row = cursor.fetchone()

    except TypeError:
        cursor.close()
        return None

    case_type: str = row[1]

    match case_type:
        case "Timeout":
            cursor.execute("SELECT * FROM timeout_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Offence": f"{row[3]}",
                "Details": f"{row[4]}",
                "Offender ID": row[1],
                "Moderator ID": row[2],
                "Planned End": row[6],
                "Actual End": row[7],
                "Timestamp": row[8],
            }

        case "Slur Usage":
            cursor.execute("SELECT * FROM slur_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Slur Used": f"{row[1]}",
                "Report URL": f"{row[2]}",
                "Offender ID": row[3],
                "Moderator ID": row[4],
                "Timestamp": row[5],
            }

        case "Reformation":
            cursor.execute("SELECT * FROM reformation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Case Number": row[1],
                "Offender ID": row[2],
                "Moderator ID": row[3],
                "Channel ID": row[4],
                "Reason": f"{row[5]}",
                "Timestamp": row[6],
            }

        case "Probation":
            cursor.execute("SELECT * FROM probation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Offender ID": row[1],
                "Initial Moderator ID": row[2],
                "Approving Moderator ID": row[3],
                "Reason": f"{row[4]}",
                "Timestamp": row[5],
            }

        case "Bad Faith Ping":
            cursor.execute("SELECT * FROM bad_faith_ping_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Report URL": f"{row[1]}",
                "Offender ID": row[2],
                "Moderator ID": row[3],
                "Timestamp": row[4],
            }

        case "Warn":
            cursor.execute("SELECT * FROM warn_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Offender ID": row[1],
                "Moderator ID": row[2],
                "Offence": row[3],
                "Offence Details": row[4],
                "Active": row[5],
                "Timestamp": row[6],
            }

        case "Kick":
            cursor.execute("SELECT * FROM kick_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Offender ID": row[1],
                "Moderator ID": row[2],
                "Reason": row[3],
                "Timestamp": row[4],
            }


def fetch_all_cases(
    config: Configuration,
    page: int,
    per_page: int,
    case_type: typing.Optional[str] = None,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if not case_type:
        cursor.execute(
            """
            SELECT id, '`Probation`' as type, timestamp FROM probation_cases
            UNION
            SELECT id, '`Reformation`' as type, timestamp FROM reformation_cases
            UNION
            SELECT id, '`Slur Usage`' as type, timestamp FROM slur_cases
            UNION
            SELECT id, '`Bad Faith Ping`' as type, timestamp FROM bad_faith_ping_cases
            UNION
            select id, '`Warn`' as type, timestamp FROM warn_cases
            UNION
            select id, '`Kick`' as type, timestamp FROM kick_cases
            UNION
            select id, '`Timeout`' as type, timestamp FROM timeout_cases
            
            ORDER BY timestamp DESC
            """
        )

    else:
        match case_type:
            case "timeout_cases":
                cursor.execute(
                    """
                    SELECT id, '`Timeout`' as type, timestamp
                    FROM timeout_cases
                    ORDER BY timestamp DESC""",
                )

            case "slur_cases":
                cursor.execute(
                    """
                    SELECT id, '`Slur Usage`' as type, timestamp
                    FROM slur_cases
                    ORDER BY timestamp DESC""",
                )

            case "reformation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Reformation`' as type, timestamp
                    FROM reformation_cases
                    ORDER BY timestamp DESC
                    """,
                )

            case "probation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Probation`' as type, timestamp
                    FROM probation_cases
                    ORDER BY timestamp DESC
                    """,
                )

            case "bad_faith_ping_cases":
                cursor.execute(
                    """
                    SELECT id, '`Bad Faith Ping`' as type, timestamp
                    FROM bad_faith_ping_cases
                    ORDER BY timestamp DESC
                    """,
                )

            case "scrubbed_cases":
                cursor.execute(
                    """
                    SELECT id, type, timestamp
                    FROM scrubbed_cases
                    ORDER BY timestamp DESC
                    """,
                )

            case "warn_cases":
                cursor.execute(
                    """
                    SELECT id, '`Warn`' as type, timestamp
                    FROM warn_cases
                    ORDER BY timestamp DESC"""
                )

            case "kick_cases":
                cursor.execute(
                    """
                    SELECT id, '`Kick`' as type, timestamp
                    FROM kick_cases
                    ORDER BY timestamp DESC"""
                )

    cases = cursor.fetchall()

    if not cases:
        return None, 0, 0

    else:
        cases_list = [list(case) for case in cases]
        return get_page(cases_list, page, per_page)


def fetch_offender_cases(
    config: Configuration,
    page: int,
    per_page: int,
    offender: nextcord.Member,
    case_type: typing.Optional[str] = None,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if not case_type:
        cursor.execute(
            """
            SELECT id, '`Probation`' as type, timestamp FROM probation_cases WHERE offender=:offender
            UNION
            SELECT id, '`Reformation`' as type, timestamp FROM reformation_cases WHERE offender=:offender
            UNION
            SELECT id, '`Slur Usage`' as type, timestamp FROM slur_cases WHERE offender=:offender
            UNION
            SELECT id, '`Bad Faith Ping`' as type, timestamp FROM bad_faith_ping_cases WHERE offender=:offender
            UNION
            select id, '`Warn`' as type, timestamp FROM warn_cases WHERE offender=:offender
            UNION
            select id, '`Kick`' as type, timestamp FROM kick_cases WHERE offender=:offender
            ORDER BY timestamp DESC
            """,
            {"offender": str(offender.id)},
        )

    else:
        match case_type:
            case "slur_cases":
                cursor.execute(
                    """
                    SELECT id, '`Slur Usage`' as type, timestamp
                    FROM slur_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "reformation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Reformation`' as type, timestamp
                    FROM reformation_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "probation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Probation`' as type, timestamp
                    FROM probation_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "bad_faith_ping_cases":
                cursor.execute(
                    """
                    SELECT id, '`Bad Faith Ping`' as type, timestamp
                    FROM bad_faith_ping_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "scrubbed_cases":
                cursor.execute(
                    """
                    SELECT id, type, timestamp
                    FROM scrubbed_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )
            case "warn_cases":
                cursor.execute(
                    """
                    SELECT id, '`Warn`' as type, timestamp
                    FROM warn_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC""",
                    {"offender": str(offender.id)},
                )
            case "warn_cases":
                cursor.execute(
                    """
                    SELECT id, '`Kick`' as type, timestamp
                    FROM kick_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC""",
                    {"offender": str(offender.id)},
                )

    cases = cursor.fetchall()

    if not cases:
        return None, 0, 0

    else:
        cases_list = [list(case) for case in cases]
        return get_page(cases_list, page, per_page)


def fetch_moderator_cases(
    config: Configuration,
    page: int,
    per_page: int,
    moderator: nextcord.Member,
    case_type: typing.Optional[str] = None,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if not case_type:
        cursor.execute(
            """
            SELECT id, '`Bad Faith Ping`' as type, timestamp
            FROM bad_faith_ping_cases
            WHERE moderator=:moderator

            UNION

            SELECT id, '`Probation`' as type, timestamp
            FROM probation_cases
            WHERE initial_moderator=:moderator OR approving_moderator=:moderator

            UNION

            SELECT id, '`Reformation`' as type, timestamp
            FROM reformation_cases
            WHERE moderator=:moderator

            UNION

            SELECT id, '`Slur Usage`' as type, timestamp
            FROM slur_cases
            WHERE moderator=:moderator

            UNION
            
            SELECT id, '`Warn`' as type, timestamp
            FROM warn_cases
            WHERE moderator=:moderator

            UNION
            
            SELECT id, '`Kick`' as type, timestamp
            FROM kick_cases
            WHERE moderator=:moderator
            ORDER BY timestamp DESC
        """,
            {"moderator": str(moderator.id)},
        )

    else:
        match case_type:
            case "slur_cases":
                cursor.execute(
                    """
                    SELECT id, '`Slur Usage`' as type, timestamp
                    FROM slur_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "reformation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Reformation`' as type, timestamp
                    FROM reformation_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "probation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Probation`' as type, timestamp
                    FROM probation_cases
                    WHERE initial_moderator=:moderator
                       OR approving_moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "bad_faith_ping_cases":
                cursor.execute(
                    """
                    SELECT id, '`Bad Faith Ping`' as type, timestamp
                    FROM bad_faith_ping_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "scrubbed_cases":
                cursor.execute(
                    """
                    SELECT id, type, timestamp
                    FROM scrubbed_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "warn_cases":
                cursor.execute(
                    """
                    SELECT id, '`Warn`' as type, timestamp
                    FROM warn_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC""",
                    {"moderator": str(moderator.id)},
                )

            case "kick_cases":
                cursor.execute(
                    """
                    SELECT id, '`Kick`' as type, timestamp
                    FROM kick_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC""",
                    {"moderator": str(moderator.id)},
                )

    cases = cursor.fetchall()

    cursor.close()

    if not cases:
        return None, 0, 0

    else:
        cases_list = [list(case) for case in cases]
        return get_page(cases_list, page, per_page)
