import sqlite3

import nextcord

from utils.database import ReformationCase, db_session
from utils.config import Configuration


def slur_virgin(config: Configuration, user: nextcord.User) -> bool:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM slur_cases WHERE offender=?", (user.id,))

    cases = cursor.fetchone()

    conn.close()

    if cases:
        return False

    else:
        return True


def slur_history(config: Configuration, user: nextcord.User, slur: list):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cases = []

    for sl in slur:
        cursor.execute(
            "SELECT * FROM slur_cases WHERE slur_used=? AND offender=? ORDER BY timestamp DESC",
            (
                sl,
                user.id,
            ),
        )

        cases.extend(cursor.fetchmany(5))

    if cases:
        conn.close()
        return cases

    else:
        conn.close()
        return False


def offence_validity_check(config: Configuration, offence: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT offence FROM offences WHERE offence=?", (offence,))

    offence_exists = cursor.fetchone()

    if offence_exists:
        return True

    else:
        return False


def deletion_validity_check(config: Configuration, case_id: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM warn_cases WHERE id=?", (case_id,))

    warn_exists = cursor.fetchone()

    if warn_exists:
        return True

    else:
        return False


def get_reformation_next_case_number():
    with db_session() as session:
        last_case: ReformationCase = session                \
            .query(ReformationCase)                         \
            .order_by(ReformationCase.case_number.desc())   \
            .first()

    if last_case is None:
        return 1
    
    return last_case.case_number + 1
