import sqlite3
import nextcord
import time
import typing

from utils.config import Configuration
from utils.base import SersiEmbed, get_page, create_unique_id


def create_case(config: Configuration, unique_id: str, case_type: str, timestamp: int):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        f"""
        INSERT INTO cases (id, type, timestamp)
        VALUES ({unique_id}, {case_type}, {timestamp})"""
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
        f"""
        INSERT INTO slur_cases (id, slur_used, report_url, offender, moderator, timestamp)
        VALUES ('{unique_id}', '{slur_used}', '{report_url}', {offender_id}, {moderator_id}, {timestamp})
        """
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
        f"""
        INSERT INTO reformation_cases (id, case_number, offender, moderator, cell_id, reason, timestamp)
        VALUES ('{unique_id}', {case_num}, {offender_id}, {moderator_id}, {cell_id}, '{reason}', {timestamp})
        """
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
        f"""
        INSERT INTO probation_cases (id, offender, initial_moderator, approving_moderator, reason, timestamp)
        VALUES ('{unique_id}', {offender_id}, {initial_moderator_id}, {approving_moderator_id}, '{reason}', {timestamp})
        """
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
        f"""
        INSERT INTO bad_faith_ping_cases (id, report_url, offender, moderator, timestamp)
        VALUES ('{unique_id}', '{report_url}', {offender_id}, {moderator_id}, {timestamp})
        """
    )

    conn.commit()
    conn.close()


def get_case_by_id(
    config: Configuration, case_id: str, scrubbed: bool
) -> dict[str:str] | str | None:
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if scrubbed:
        cursor.execute("SELECT * FROM scrubbed_cases WHERE id=?", (case_id,))
        try:
            row = cursor.fetchone()

            return {
                "ID": f"{row[0]}",
                "Case Type": f"{row[1]}",
                "Offender ID": row[2],
                "Scrubber ID": row[3],
                "Scrub Reason": f"{row[4]}",
                "Timestamp": row[5],
            }

        except TypeError:
            cursor.close()
            return None

    cursor.execute("SELECT * FROM cases WHERE id=?", (case_id,))

    try:
        row = cursor.fetchone()

    except TypeError:
        cursor.close()
        return None

    case_type: str = row[1]

    match case_type:
        case "Slur Usage":
            cursor.execute("SELECT * FROM slur_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

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

        case "Reformation":
            cursor.execute("SELECT * FROM reformation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

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

        case "Probation":
            cursor.execute("SELECT * FROM probation_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

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

        case "Bad Faith Ping":
            cursor.execute("SELECT * FROM bad_faith_ping_cases WHERE id=?", (case_id,))

            try:
                row = cursor.fetchone()
                cursor.close()

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


def fetch_cases_by_partial_id(config: Configuration, case_id: str):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if case_id == "":
        cursor.execute("SELECT * FROM cases ORDER BY timestamp DESC LIMIT 10")
    else:
        cursor.execute(
            "SELECT * FROM cases WHERE id LIKE ? LIMIT 10 ", (f"{case_id}%",)
        )

    rows = cursor.fetchall()

    conn.close()

    id_list = [row[0] for row in rows]

    return id_list


def create_scrubbed_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(
        name="Type:", value=f"`{sersi_case['Case Type']}`", inline=True
    )

    scrubber = interaction.guild.get_member(sersi_case["Scrubber ID"])

    if not scrubber:
        case_embed.add_field(
            name="Scrubber:",
            value=f"`{sersi_case['Scrubber ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Scrubber ID:",
            value=f"{scrubber.mention}",
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

    case_embed.add_field(name="Reason:", value=sersi_case["Scrub Reason"], inline=False)

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


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
        value=f"<t:{sersi_case['Timestamp']}:R>",
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
        value=f"<t:{sersi_case['Timestamp']}:R>",
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
        value=f"<t:{sersi_case['Timestamp']}:R>",
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
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def fetch_all_cases(
    config: Configuration,
    page: int,
    per_page: int,
    case_type: typing.Optional[str] = None,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if not case_type:
        cursor.execute(
            """
            SELECT id, '`Probation`' as type, timestamp FROM probation_cases
            UNION
            SELECT id, '`Reformation`' as type, timestamp FROM reformation_cases
            UNION
            SELECT id, '`Slur Usage`' as type, timestamp FROM slur_cases
            UNION
            SELECT id, '`Bad Faith Ping`' as type, timestamp FROM bad_faith_ping_cases
            ORDER BY timestamp DESC
            """
        )

    else:
        match case_type:
            case "slur_cases":
                cursor.execute(
                    """SELECT id, '`Slur Usage`' as type, timestamp
                    FROM slur_cases
                    ORDER BY timestamp DESC""",
                )

            case "reformation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Reformation`' as type, timestamp
                    FROM reformation_cases
                    ORDER BY timestamp DESC
                    """,
                )

            case "probation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Probation`' as type, timestamp
                    FROM probation_cases
                    ORDER BY timestamp DESC
                    """,
                )

            case "bad_faith_ping_cases":
                cursor.execute(
                    """
                    SELECT id, '`Bad Faith Ping`' as type, timestamp
                    FROM bad_faith_ping_cases
                    ORDER BY timestamp DESC
                    """,
                )

            case "scrubbed_cases":
                cursor.execute(
                    """
                    SELECT id, type, timestamp
                    FROM scrubbed_cases
                    ORDER BY timestamp DESC
                    """,
                )

    cases = cursor.fetchall()

    if not cases:
        return None, 0, 0

    else:
        cases_list = [list(case) for case in cases]
        return get_page(cases_list, page, per_page)


def fetch_offender_cases(
    config: Configuration,
    page: int,
    per_page: int,
    offender: nextcord.Member,
    case_type: typing.Optional[str] = None,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if not case_type:
        cursor.execute(
            """
            SELECT id, '`Probation`' as type, timestamp FROM probation_cases WHERE offender=:offender
            UNION
            SELECT id, '`Reformation`' as type, timestamp FROM reformation_cases WHERE offender=:offender
            UNION
            SELECT id, '`Slur Usage`' as type, timestamp FROM slur_cases WHERE offender=:offender
            UNION
            SELECT id, '`Bad Faith Ping`' as type, timestamp FROM bad_faith_ping_cases WHERE offender=:offender
            ORDER BY timestamp DESC
            """,
            {"offender": str(offender.id)},
        )

    else:
        match case_type:
            case "slur_cases":
                cursor.execute(
                    """
                    SELECT id, '`Slur Usage`' as type, timestamp
                    FROM slur_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "reformation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Reformation`' as type, timestamp
                    FROM reformation_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "probation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Probation`' as type, timestamp
                    FROM probation_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "bad_faith_ping_cases":
                cursor.execute(
                    """
                    SELECT id, '`Bad Faith Ping`' as type, timestamp
                    FROM bad_faith_ping_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

            case "scrubbed_cases":
                cursor.execute(
                    """
                    SELECT id, type, timestamp
                    FROM scrubbed_cases
                    WHERE offender=:offender
                    ORDER BY timestamp DESC
                    """,
                    {"offender": str(offender.id)},
                )

    cases = cursor.fetchall()

    if not cases:
        return None, 0, 0

    else:
        cases_list = [list(case) for case in cases]
        return get_page(cases_list, page, per_page)


def fetch_moderator_cases(
    config: Configuration,
    page: int,
    per_page: int,
    moderator: nextcord.Member,
    case_type: typing.Optional[str] = None,
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    if not case_type:
        cursor.execute(
            """
            SELECT id, '`Bad Faith Ping`' as type, timestamp
            FROM bad_faith_ping_cases
            WHERE moderator=:moderator

            UNION

            SELECT id, '`Probation`' as type, timestamp
            FROM probation_cases
            WHERE initial_moderator=:moderator OR approving_moderator=:moderator

            UNION

            SELECT id, '`Reformation`' as type, timestamp
            FROM reformation_cases
            WHERE moderator=:moderator

            UNION

            SELECT id, '`Slur Usage`' as type, timestamp
            FROM slur_cases
            WHERE moderator=:moderator
            ORDER BY timestamp DESC
        """,
            {"moderator": str(moderator.id)},
        )

    else:
        match case_type:
            case "slur_cases":
                cursor.execute(
                    """
                    SELECT id, '`Slur Usage`' as type, timestamp
                    FROM slur_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "reformation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Reformation`' as type, timestamp
                    FROM reformation_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "probation_cases":
                cursor.execute(
                    """
                    SELECT id, '`Probation`' as type, timestamp
                    FROM probation_cases
                    WHERE initial_moderator=:moderator
                       OR approving_moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "bad_faith_ping_cases":
                cursor.execute(
                    """
                    SELECT id, '`Bad Faith Ping`' as type, timestamp
                    FROM bad_faith_ping_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

            case "scrubbed_cases":
                cursor.execute(
                    """
                    SELECT id, type, timestamp
                    FROM scrubbed_cases
                    WHERE moderator=:moderator
                    ORDER BY timestamp DESC
                    """,
                    {"moderator": str(moderator.id)},
                )

    cases = cursor.fetchall()

    cursor.close()

    if not cases:
        return None, 0, 0

    else:
        cases_list = [list(case) for case in cases]
        return get_page(cases_list, page, per_page)


def create_slur_case(
    config: Configuration,
    slur_used: str,
    report_url: str,
    offender: nextcord.Member,
    moderator: nextcord.Member,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO slur_cases (id, slur_used, report_url, offender, moderator, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
        (uuid, slur_used, report_url, offender.id, moderator.id, timestamp),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Slur Usage", timestamp),
    )

    conn.commit()
    conn.close()


def create_probation_case(
    config: Configuration,
    offender: nextcord.Member,
    initial_moderator: nextcord.Member,
    approving_moderator: nextcord.Member,
    reason: str,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO probation_cases (id, offender, initial_moderator, approving_moderator, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            uuid,
            offender.id,
            initial_moderator.id,
            approving_moderator.id,
            reason,
            timestamp,
        ),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Probation", timestamp),
    )

    conn.commit()
    conn.close()


def create_reformation_case(
    config: Configuration,
    case_number: int,
    offender: nextcord.Member,
    moderator: nextcord.Member,
    reformation_cell: nextcord.TextChannel,
    reason: str,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reformation_cases (id, case_number, offender, moderator, cell_id, reason, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            uuid,
            case_number,
            offender.id,
            moderator.id,
            reformation_cell.id,
            reason,
            timestamp,
        ),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Reformation", timestamp),
    )

    conn.commit()
    conn.close()


def create_bad_faith_ping_case(
    config: Configuration,
    report_url: str,
    offender: nextcord.Member,
    moderator: nextcord.Member,
):
    uuid = create_unique_id(config)

    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO bad_faith_ping_cases (id, report_url, offender, moderator, timestamp) VALUES (?, ?, ?, ?, ?)",
        (uuid, report_url, offender.id, moderator.id, timestamp),
    )
    cursor.execute(
        "INSERT INTO cases (id, type, timestamp) VALUES (?, ?, ?)",
        (uuid, "Bad Faith Ping", timestamp),
    )

    conn.commit()
    conn.close()


def scrub_case(
    config: Configuration, case_id: str, scrubber: nextcord.Member, reason: str
):
    timestamp = int(time.time())

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cases WHERE id=?", (case_id,))

    case = cursor.fetchone()

    if case:
        case_type = case[1]

        match case_type:
            case "Slur Usage":
                cursor.execute("SELECT * FROM slur_cases WHERE id=?", (case_id,))

                try:
                    row = cursor.fetchone()

                except TypeError:
                    cursor.close()
                    return False

                offender_id = row[3]

            case "Reformation":
                cursor.execute("SELECT * FROM reformation_cases WHERE id=?", (case_id,))

                try:
                    row = cursor.fetchone()

                except TypeError:
                    cursor.close()
                    return False

                offender_id = row[2]

            case "Probation":
                cursor.execute("SELECT * FROM probation_cases WHERE id=?", (case_id,))

                try:
                    row = cursor.fetchone()

                except TypeError:
                    return False

                offender_id = row[1]

            case "Bad Faith Ping":
                cursor.execute(
                    "SELECT * FROM bad_faith_ping_cases WHERE id=?", (case_id,)
                )

                try:
                    row = cursor.fetchone()

                except TypeError:
                    cursor.close()
                    return False

                offender_id = row[2]

            case _:
                offender_id = ""

        # print(case_id, case_type, offender_id, scrubber.id, reason, timestamp)

        cursor.execute(
            "INSERT INTO scrubbed_cases (id, type, offender, scrubber, reason, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (
                case_id,
                case_type,
                int(offender_id),
                int(scrubber.id),
                reason,
                int(timestamp),
            ),
        )

        cursor.execute("DELETE FROM cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM probation_cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM slur_cases WHERE id=?", (case_id,))
        cursor.execute("DELETE FROM reformation_cases WHERE id=?", (case_id,))

        conn.commit()
        conn.close()
        return True

    else:
        conn.close()
        return False


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


def slur_virgin(config: Configuration, user: nextcord.User):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM slur_cases WHERE offender=?", (user.id,))

    cases = cursor.fetchone()

    print(cases)

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
