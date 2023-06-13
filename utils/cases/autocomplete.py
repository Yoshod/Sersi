import sqlite3

from utils.config import Configuration


def fetch_cases_by_partial_id(config: Configuration, case_id: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if case_id == "":
        cursor.execute("SELECT * FROM cases ORDER BY timestamp DESC LIMIT 10")
    else:
        cursor.execute(
            "SELECT * FROM cases WHERE id LIKE ? LIMIT 10 ", (f"{case_id}%",)
        )

    rows = cursor.fetchall()

    conn.close()

    id_list = [row[0] for row in rows]

    return id_list


def fetch_offences_by_partial_name(config: Configuration, offence: str) -> list[str]:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if offence == "":
        cursor.execute(
            """
            SELECT * FROM offences o
            ORDER BY (SELECT COUNT(*) FROM warn_cases wc WHERE wc.offence = o.offence)
            DESC LIMIT 25
        """
        )
    else:
        cursor.execute(
            "SELECT * FROM offences WHERE LOWER(offence) LIKE ? LIMIT 25 ",
            (f"%{offence.lower()}%",),
        )

    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]
