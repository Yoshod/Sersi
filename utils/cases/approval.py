import sqlite3

from utils.config import Configuration


def update_approved(case_id, config: Configuration):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("UPDATE warn_cases SET approved = ? WHERE id = ?", (True, case_id))

    conn.commit()
    conn.close()


def update_objected(case_id, config: Configuration):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("UPDATE warn_cases SET approved = ? WHERE id = ?", (False, case_id))

    conn.commit()
    conn.close()


def update_approval(approval_status, case_id, config: Configuration):
    if approval_status:
        update_approved(case_id, config)
    else:
        update_objected(case_id, config)
