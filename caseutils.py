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
