import sqlite3
import nextcord

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
        """INSERT INTO notes (id, noted, noter, note, timestamp) VALUES (?, ?, ?, ?, ?)""",
        (str(unique_id), noted.id, noter.id, note, timestamp),
    )

    conn.commit()
    conn.close()


def get_note_by_id(
    config: Configuration,
    note_id: str,
) -> dict:
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
        "Noted ID": row[1],
        "Noter ID": row[2],
        "Note": row[3],
        "Timestamp": row[4],
    }


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

    moderator = interaction.guild.get_member(sersi_note["Noter ID"])

    if not moderator:
        note_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_note['Noter ID']}`",
            inline=True,
        )

    else:
        note_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    noted = interaction.guild.get_member(sersi_note["Noted ID"])

    if not noted:
        note_embed.add_field(
            name="User:",
            value=f"`{sersi_note['Noted ID']}`",
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