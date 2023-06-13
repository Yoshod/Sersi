import sqlite3

from utils.config import Configuration


def delete_case(config: Configuration, case_id: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM scrubbed_cases WHERE id=?", (case_id,))

    case = cursor.fetchone()

    if case:
        cursor.execute("DELETE FROM scrubbed_cases WHERE id=?", (case_id,))

        conn.commit()
        conn.close()
        return True

    else:
        conn.close()
        return False


def delete_warn(config: Configuration, case_id: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM warn_cases WHERE id=?", (case_id,))

    case = cursor.fetchone()

    if case:
        cursor.execute("DELETE FROM warn_cases WHERE id=?", (case_id,))

        cursor.execute("DELETE FROM cases WHERE id=?", (case_id,))

        conn.commit()
        conn.close()
        return True

    else:
        conn.close()
        return False
