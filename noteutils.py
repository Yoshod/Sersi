import sqlite3
import nextcord
import shortuuid
import time

from configutils import Configuration
from baseutils import SersiEmbed, get_page
from caseutils import create_unique_id


def create_note(
    config: Configuration,
    noted: nextcord.Member,
    noter: nextcord.Member,
    note: str,
    timestamp: int,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    unique_id = create_unique_id(config)

    cursor.execute(
        """INSERT INTO notes (id, noted, noter, note, timestamp) VALUES (?, ?, ?, ?, ?) VALUES """,
        (unique_id, noted.id, noter.id, note, timestamp),
    )

    conn.commit()
    conn.close()
