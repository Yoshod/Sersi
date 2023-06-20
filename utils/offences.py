import sqlite3
import time

import nextcord
from utils.config import Configuration


def add_offence_to_database(
        offence_name: str,
        offence_description: str,
        first_punishment: str,
        second_punishment: str,
        third_punishment: str):
    conn = sqlite3.connect(Configuration.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO offences (offence, first_instance, second_instance, third_instance, detail VALUES (?,?,?,?,?)",
        (offence_name, first_punishment, second_punishment, third_punishment, offence_description),
    )
    conn.commit()
    conn.close()