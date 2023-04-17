import sqlite3
import nextcord

from configutils import Configuration
from baseutils import SersiEmbed


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


def get_case_by_id(
    config: Configuration,
    case_id: str,
) -> dict:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cases WHERE id=?", (case_id,))

    try:
        row = cursor.fetchone()

    except TypeError:
        cursor.close()
        return "No Case"

    case_type = row[1]

    match (case_type):
        case "Slur Usage":
            cursor.execute("SELECT * FROM slur_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Slur Used": f"{row[1]}",
                "Report URL": f"{row[2]}",
                "Offender ID": row[3],
                "Moderator ID": row[4],
                "Timestamp": row[5],
            }

    match (case_type):
        case "Reformation":
            cursor.execute("SELECT * FROM reformation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Case Number": row[1],
                "Offender ID": row[2],
                "Moderator ID": row[3],
                "Channel ID": row[4],
                "Reason": f"{row[5]}",
                "Timestamp": row[6],
            }

    match (case_type):
        case "Probation":
            cursor.execute("SELECT * FROM probation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Offender ID": row[1],
                "Initial Moderator ID": row[2],
                "Approving Moderator ID": row[3],
                "Reason": f"{row[4]}",
                "Timestamp": row[5],
            }

    match (case_type):
        case "Bad Faith Ping":
            cursor.execute("SELECT * FROM bad_faith_ping_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()

            except TypeError:
                cursor.close()
                return "Exists Not Found"

            return {
                "ID": f"{row[0]}",
                "Case Type": case_type,
                "Report URL": f"{row[1]}",
                "Offender ID": row[2],
                "Moderator ID": row[3],
                "Timestamp": row[4],
            }


def create_slur_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Slur Usage`", inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Slur Used:", value=sersi_case["Slur Used"], inline=False)

    case_embed.add_field(
        name="Report URL:", value=sersi_case["Report URL"], inline=False
    )

    case_embed.add_field(
        name="Timestamp:",
        value=(f"<t:{sersi_case['Timestamp']}:R>"),
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_reformation_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Reformation`", inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Reason:", value=sersi_case["Reason"], inline=False)
    reformation_channel = interaction.client.get_channel(sersi_case["Channel ID"])

    if not reformation_channel:
        case_embed.add_field(
            name="Reformation Channel:",
            value="Channel No Longer Exists",
            inline=False,
        )
    else:
        case_embed.add_field(
            name="Reformation Channel:",
            value=reformation_channel.mention,
            inline=False,
        )

    case_embed.add_field(
        name="Timestamp:",
        value=(f"<t:{sersi_case['Timestamp']}:R>"),
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_probation_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Probation`", inline=True)

    initial_moderator = interaction.guild.get_member(sersi_case["Initial Moderator ID"])

    if not initial_moderator:
        case_embed.add_field(
            name="Initial Moderator:",
            value=f"`{sersi_case['Initial Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Initial Moderator:",
            value=f"{initial_moderator.mention}",
            inline=True,
        )

    approving_moderator = interaction.guild.get_member(
        sersi_case["Approving Moderator ID"]
    )

    if not approving_moderator:
        case_embed.add_field(
            name="Approving Moderator:",
            value=f"`{sersi_case['Approving Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Approving Moderator:",
            value=f"{approving_moderator.mention}",
            inline=True,
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=False,
        )

    else:
        case_embed.add_field(
            name="Offender:", value=f"{offender.mention}", inline=False
        )
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Reason:", value=sersi_case["Reason"], inline=False)

    case_embed.add_field(
        name="Timestamp:",
        value=(f"<t:{sersi_case['Timestamp']}:R>"),
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_bad_faith_ping_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Bad Faith Ping`", inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(
        name="Report URL:", value=sersi_case["Report URL"], inline=False
    )

    case_embed.add_field(
        name="Timestamp:",
        value=(f"<t:{sersi_case['Timestamp']}:R>"),
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed
