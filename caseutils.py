import sqlite3

from configutils import Configuration


def create_case(config: Configuration, unique_id: str, case_type: str, timestamp: int):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        f"""INSERT INTO cases (id, type, timestamp) VALUES ({unique_id}, {case_type}, {timestamp})"""
    )

    conn.commit()
    conn.close()


def slur_case(
    config: Configuration,
    unique_id: str,
    slur_used: str,
    report_url: str,
    offender_id: int,
    moderator_id: int,
    timestamp: int,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        f"INSERT INTO slur_cases (id, slur_used, report_url, offender, moderator, timestamp) VALUES ('{unique_id}', '{slur_used}', '{report_url}', {offender_id}, {moderator_id}, {timestamp})"
    )

    conn.commit()
    conn.close()


def reform_case(
    config: Configuration,
    unique_id: str,
    case_num: int,
    offender_id: int,
    moderator_id: int,
    cell_id: int,
    reason: str,
    timestamp: int,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        f"INSERT INTO reformation_cases (id, case_number, offender, moderator, cell_id, reason, timestamp) VALUES ('{unique_id}', {case_num}, {offender_id}, {moderator_id}, {cell_id}, '{reason}', {timestamp})"
    )

    conn.commit()
    conn.close()


def probation_case(
    config: Configuration,
    unique_id: str,
    offender_id: int,
    initial_moderator_id: int,
    approving_moderator_id: int,
    reason: str,
    timestamp: int,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        f"INSERT INTO probation_cases (id, offender, initial_moderator, approving_moderator, reason, timestamp) VALUES ('{unique_id}', {offender_id}, {initial_moderator_id}, {approving_moderator_id}, '{reason}', {timestamp})"
    )

    conn.commit()
    conn.close()


def ping_case(
    config: Configuration,
    unique_id: str,
    report_url: str,
    offender_id: int,
    moderator_id: int,
    timestamp: int,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        f"INSERT INTO bad_faith_ping_cases (id, report_url, offender, moderator, timestamp) VALUES ('{unique_id}', '{report_url}', {offender_id}, {moderator_id}, {timestamp})"
    )

    conn.commit()
    conn.close()


def get_case_by_id(
    config: Configuration,
    case_id: str,
) -> dict:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cases WHERE id=?", (case_id,))

    try:
        row = cursor.fetchone()

    except TypeError:
        cursor.close()
        return "No Case"

    case_type = row[1]

    match (case_type):
        case "Slur Usage":
            cursor.execute("SELECT * FROM slur_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Slur Used": f"{row[1]}",
                "Report URL": f"{row[2]}",
                "Offender ID": row[3],
                "Moderator ID": row[4],
                "Timestamp": row[5],
            }

    match (case_type):
        case "Reformation":
            cursor.execute("SELECT * FROM reformation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Number": row[1],
                "Offender ID": row[2],
                "Moderator ID": row[3],
                "Channel ID": row[4],
                "Reason": f"{row[5]}",
                "Timestamp": row[6],
            }

    match (case_type):
        case "Probation":
            cursor.execute("SELECT * FROM probation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Offender ID": row[1],
                "Initial Moderator ID": row[2],
                "Approving Moderator ID": row[3],
                "Reason": f"{row[4]}",
                "Timestamp": row[5],
            }

    match (case_type):
        case "Bad Faith Ping":
            cursor.execute("SELECT * FROM bad_faith_ping_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Report URL": f"{row[1]}",
                "Offender ID": row[2],
                "Moderator ID": row[3],
                "Timestamp": row[4],
            }
