import sqlite3

import nextcord

from utils.config import Configuration
from utils.base import SersiEmbed, get_page, create_unique_id


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
        """INSERT INTO notes (id, noted, noter, note, timestamp) VALUES (?, ?, ?, ?, ?)""",
        (str(unique_id), noted.id, noter.id, note, timestamp),
    )

    conn.commit()
    conn.close()

    return unique_id


def get_note_by_id(
    config: Configuration,
    note_id: str,
) -> dict[str:str] | str:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes WHERE id=?", (note_id,))

    try:
        row = cursor.fetchone()

    except TypeError:
        cursor.close()
        return "No Note"

    conn.close()

    return {
        "ID": f"{row[0]}",
        "Target ID": row[1],
        "Moderator ID": row[2],
        "Note": row[3],
        "Timestamp": row[4],
    }


def get_note_by_user(
    config: Configuration,
    page: int,
    per_page: int,
    user_id: str,
) -> str | tuple[list, int, int]:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM notes WHERE noted=? ORDER BY timestamp DESC", (user_id,)
    )

    try:
        notes = cursor.fetchall()

    except TypeError:
        cursor.close()
        return "No Note"

    conn.close()

    notes_list = [list(note) for note in notes]
    return get_page(notes_list, page, per_page)


def get_note_by_moderator(
    config: Configuration,
    moderator_id: str,
    page: int,
    per_page: int,
) -> str | tuple[list, int, int]:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM notes WHERE noter=? ORDER BY timestamp DESC", (moderator_id,)
    )

    try:
        notes = cursor.fetchall()

    except TypeError:
        cursor.close()
        return "No Note"

    conn.close()

    notes_list = [list(note) for note in notes]
    return get_page(notes_list, page, per_page)


def fetch_notes_by_partial_id(config: Configuration, note_id: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if note_id == "":
        cursor.execute("SELECT * FROM notes ORDER BY timestamp DESC LIMIT 10")
    else:
        cursor.execute(
            "SELECT * FROM notes WHERE id LIKE ? LIMIT 10 ", (f"{note_id}%",)
        )

    rows = cursor.fetchall()

    conn.close()

    id_list = [row[0] for row in rows]

    return id_list


def create_note_embed(
    sersi_note: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    note_embed = SersiEmbed()
    note_embed.add_field(name="Note ID:", value=f"`{sersi_note['ID']}`", inline=True)

    moderator = interaction.guild.get_member(sersi_note["Moderator ID"])

    if not moderator:
        note_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_note['Moderator ID']}`",
            inline=True,
        )

    else:
        note_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    noted = interaction.guild.get_member(sersi_note["Target ID"])

    if not noted:
        note_embed.add_field(
            name="User:",
            value=f"`{sersi_note['Target ID']}`",
            inline=True,
        )

    else:
        note_embed.add_field(name="User:", value=f"{noted.mention}", inline=True)
        note_embed.set_thumbnail(url=noted.display_avatar.url)

    note_embed.add_field(name="Note:", value=sersi_note["Note"], inline=False)

    note_embed.add_field(
        name="Timestamp:",
        value=(f"<t:{sersi_note['Timestamp']}:R>"),
        inline=True,
    )

    note_embed.set_footer(text="Sersi Notes")

    return note_embed


def delete_note(config: Configuration, note_id: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes WHERE id=?", (note_id,))

    case = cursor.fetchone()

    if case:
        cursor.execute("DELETE FROM notes WHERE id=?", (note_id,))

        conn.commit()
        conn.close()
        return True

    else:
        conn.close()
        return False


def wipe_user_notes(config: Configuration, user: nextcord.Member):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM notes WHERE noted=?", (user.id,))

    case = cursor.fetchall()

    if case:
        cursor.execute("DELETE FROM notes WHERE noted=?", (user.id,))

        conn.commit()
        conn.close()
        return True

    else:
        conn.close()
        return False
