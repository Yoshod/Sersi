import sqlite3

from utils.config import Configuration


def update_approved(case_id_dirty, config: Configuration):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    case_id_clean = case_id_dirty[1:-1]

    cursor.execute(
        """
            UPDATE warn_cases
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

    cursor.execute(
        """
            UPDATE warn_cases
            SET approved = False
            WHERE id =?""",
        (case_id_clean,),
    )

    conn.commit()
    conn.close()
