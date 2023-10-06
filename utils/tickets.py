import nextcord

from utils.base import create_unique_id
from utils.config import Configuration
from utils.database import db_session, Ticket


def ticket_check(proposed_ticketer: nextcord.Member, ticket_type: str):
    with db_session(proposed_ticketer) as session:
        tickets = (
            session.query(Ticket)
            .filter_by(
                creator=proposed_ticketer.id,
                active=True,
                escalation_level=ticket_type
            )
            .all()
        )

        return len(tickets) < 3


async def ticket_create(
    config: Configuration,
    interaction: nextcord.Interaction,
    ticket_creator: nextcord.Member,
    ticket_type,
    ticket_category,
    ticket_subcategory,
    opening_remarks,
    test=True,
):
    if test:
        guild: nextcord.Guild = interaction.client.get_guild(config.guilds.errors)
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(
                read_messages=False, send_messages=True
            ),
            guild.me: nextcord.PermissionOverwrite(read_messages=True),
        }

    else:
        guild = interaction.client.get_guild(config.guilds.main)
        overwrites = {
            guild.default_role: nextcord.PermissionOverwrite(
                read_messages=False, send_messages=True
            ),
            guild.me: nextcord.PermissionOverwrite(read_messages=True),
        }

    match ticket_type:
        case "Moderator":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.moderator
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

        case "Senior Moderator":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.senior_moderator
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

        case "Community Engagement Team":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.cet
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

        case "Mega Administrator":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.dark_moderator
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

        case "Verification Support":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.ticket_support
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

    ticket_id = create_unique_id(config)

    channel = await interaction.guild.create_text_channel(ticket_id)

    with db_session(ticket_creator) as session:
        session.add(
            Ticket(
                id=ticket_id,
                creator=ticket_creator.id,
                channel=channel.id,
                escalation_level=ticket_type,
                category=ticket_category,
                subcategory=ticket_subcategory,
                opening_comment=opening_remarks,
            )
        )
        session.commit()
