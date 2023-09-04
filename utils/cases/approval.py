import sqlite3

from utils.config import Configuration


def update_approved(case_id_dirty, config: Configuration):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    case_id_clean = case_id_dirty[1:-1]

    case_table = determine_case_table(case_id_clean, config)

    cursor.execute(
        f"""
            UPDATE {case_table}
            SET approved = True
            WHERE id =?""",
        (case_id_clean,),
    )

    conn.commit()
    conn.close()


def update_objected(case_id_dirty, config: Configuration):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    case_id_clean = case_id_dirty[1:-1]

    case_table = determine_case_table(case_id_clean, config)

    cursor.execute(
        f"""
            UPDATE {case_table}
            SET approved = False
            WHERE id =?""",
        (case_id_clean,),
    )

    conn.commit()
    conn.close()


def determine_case_table(case_id, config: Configuration):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases WHERE id=?", (case_id,))

    try:
        row = cursor.fetchone()

    except TypeError:
        cursor.close()
        return None

    case_type: str = row[1]

    match case_type:
        case "Timeout":
            return "timeout_cases"

        case "Warn":
            return "warn_cases"

        case "Kick":
            return "kick_cases"

        case "Ban":
            return "ban_cases"
