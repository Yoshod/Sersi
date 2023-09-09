import sqlite3
import time

import nextcord

from utils.config import Configuration


def scrub_case(
    config: Configuration, case_id: str, scrubber: nextcord.Member, reason: str
):
    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cases WHERE id=?", (case_id,))

    case = cursor.fetchone()

    if case:
        case_type = case[1]

        match case_type:
            case "Slur Usage":
                cursor.execute("SELECT * FROM slur_cases WHERE id=?", (case_id,))

                try:
                    row = cursor.fetchone()

                except TypeError:
                    cursor.close()
                    return False

                offender_id = row[3]

            case "Reformation":
                cursor.execute("SELECT * FROM reformation_cases WHERE id=?", (case_id,))

                try:
                    row = cursor.fetchone()

                except TypeError:
                    cursor.close()
                    return False

                offender_id = row[2]

            case "Probation":
                cursor.execute("SELECT * FROM probation_cases WHERE id=?", (case_id,))

                try:
                    row = cursor.fetchone()

                except TypeError:
                    return False

                offender_id = row[1]

            case "Bad Faith Ping":
                cursor.execute(
                    "SELECT * FROM bad_faith_ping_cases WHERE id=?", (case_id,)
                )

                try:
                    row = cursor.fetchone()

                except TypeError:
                    cursor.close()
                    return False

                offender_id = row[2]

            case "Warn":
                cursor.execute("SELECT * FROM warn_cases WHERE id=?", (case_id,))

                try:
                    row = cursor.fetchone()

                except TypeError:
                    return False

                offender_id = row[1]

            case _:
                offender_id = ""

        # print(case_id, case_type, offender_id, scrubber.id, reason, timestamp)

        cursor.execute(
            "INSERT INTO scrubbed_cases (id, type, offender, scrubber, reason, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (
                case_id,
                case_type,
                int(offender_id),
                int(scrubber.id),
                reason,
                int(timestamp),
            ),
        )

        cursor.execute("DELETE FROM cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM probation_cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM slur_cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM reformation_cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM bad_faith_ping_cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM warn_cases WHERE id=?", (case_id,))

        conn.commit()
        conn.close()
        return True

    else:
        conn.close()
        return False


def deactivate_warn(config: Configuration, case_id: str) -> (bool, int | None):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM warn_cases WHERE id=?", (case_id,))

    case = cursor.fetchone()

    if case:
        offender_id = case[1]
        cursor.execute(
            """
            UPDATE warn_cases
            SET active = False
            WHERE id =?""",
            (case_id,),
        )
        conn.commit()
        conn.close()
        return True, offender_id

    else:
        conn.close()
        return False, None
