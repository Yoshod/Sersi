import nextcord

from utils.config import Configuration
from utils.base import get_page, decode_snowflake
from utils.database import db_session, Note
from utils.sersi_embed import SersiEmbed


def fetch_notes(
    config: Configuration,
    page: int,
    per_page: int,
    member_id: int | None = None,
    author_id: int | None = None,
) -> str | tuple[list, int, int]:
    with db_session() as session:
        if member_id and author_id:
            notes = (
                session.query(Note)
                .filter_by(member=member_id, author=author_id)
                .order_by(Note.created.desc())
                .all()
            )

        elif member_id:
            notes = (
                session.query(Note)
                .filter_by(member=member_id)
                .order_by(Note.created.desc())
                .all()
            )

        elif author_id:
            notes = (
                session.query(Note)
                .filter_by(author=author_id)
                .order_by(Note.created.desc())
                .all()
            )

        else:
            notes = session.query(Note).order_by(Note.created.desc()).all()

        notes, page, pages = get_page(notes, page, per_page)
        for note in notes:
            repr(note)
        return notes, page, pages


def fetch_notes_by_partial_id(note_id: str) -> list[str]:
    with db_session() as session:
        return [
            note[0]
            for note in session.query(Note.id)
            .filter(Note.id.ilike(f"{note_id}%"))
            .limit(25)
            .all()
        ]


def create_note_embed(note: Note, interaction: nextcord.Interaction) -> SersiEmbed:
    note_embed = SersiEmbed()
    note_embed.add_field(name="Note ID:", value=f"`{note.id}`", inline=True)

    note_embed.add_field(
        name="Author:",
        value=f"<@{note.author}> `{note.author}`",
        inline=True,
    )

    note_embed.add_field(
        name="Member:",
        value=f"<@{note.member}> `{note.member}`",
        inline=True,
    )

    noted = interaction.guild.get_member(note.member)
    if noted:
        note_embed.set_thumbnail(url=noted.display_avatar.url)

    note_embed.add_field(name="Note:", value=note.content, inline=False)

    note_embed.add_field(
        name="Timestamp:",
        value=(f"<t:{int(note.created.timestamp())}:R>"),
        inline=True,
    )

    note_embed.set_footer(text="Sersi Notes")

    if moderator := interaction.guild.get_member(note.author):
        note_embed.set_author(
            name=moderator.display_name,
            icon_url=moderator.display_avatar.url,
        )

    return note_embed


def decode_note_kwargs(kwargs: dict[str, str]) -> dict[str, str]:
    decoded = {**kwargs}

    member_id = decoded.pop("user", None)
    author_id = decoded.pop("author", None)

    if member_id:
        decoded["member_id"] = decode_snowflake(member_id)
    if author_id:
        decoded["author_id"] = decode_snowflake(author_id)
    
    return decoded


