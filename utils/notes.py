import nextcord

from utils.config import Configuration
from utils.base import SersiEmbed, get_page
from utils.database import db_session, Note


def fetch_notes(
    config: Configuration,
    page: int,
    per_page: int,
    member_id: int | None,
    author_id: int | None,
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
            return None, 0, 0

        return get_page(notes, page, per_page)


def fetch_notes_by_partial_id(note_id: str):
    with db_session() as session:
        return session.query(Note).filter(Note.id.like(f"{note_id}%")).limit(25).all()


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
        value=(f"<t:{note.created}:R>"),
        inline=True,
    )

    note_embed.set_footer(text="Sersi Notes")

    return note_embed
