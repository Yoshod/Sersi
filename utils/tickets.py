import nextcord

from utils.config import Configuration
from utils.database import db_session, Ticket
from utils.sersi_embed import SersiEmbed


def ticket_check(proposed_ticketer: nextcord.Member|nextcord.User, **kwargs) -> bool:
    with db_session(proposed_ticketer) as session:
        tickets = (
            session.query(Ticket)
            .filter_by(
                creator=proposed_ticketer.id,
                active=True,
                **kwargs,
            )
            .all()
        )

        return bool(tickets)


async def ticket_create(
    config: Configuration,
    guild: nextcord.Guild,
    ticket_creator: nextcord.Member,
    ticket_type: str,
    ticket_category: str,
    opening_remarks: str,
):
    overwrites = {
        guild.default_role: nextcord.PermissionOverwrite(
            read_messages=False, send_messages=True
        ),
        guild.me: nextcord.PermissionOverwrite(read_messages=True),
    }

    match ticket_type:
        case "Moderator":
            type_name = "mod"
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.moderator
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

        case "Moderation Lead":
            type_name = "mod-lead"
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.senior_moderator
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

        case "Community Engagement":
            type_name = "cet"
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.cet
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )
        
        case "Community Engagement Lead":
            type_name = "cet-lead"
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.cet_lead
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

        case "Administrator":
            type_name = "admin"
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.dark_moderator
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )
    
    channel_category = nextcord.utils.get(
            guild.categories, name="STAFF SUPPORT"
    )

    with db_session(ticket_creator) as session:
        ticket_number = (
            session.query(Ticket)
            .filter_by(escalation_level=ticket_type)
            .count()
        ) + 1

        ticket_id = f"{type_name}-ticket-{ticket_number:04d}"

        channel = await guild.create_text_channel(ticket_id, overwrites=overwrites, category=channel_category)
        if channel is None:
            return

        session.add(
            Ticket(
                id=ticket_id,
                creator=ticket_creator.id,
                channel=channel.id,
                escalation_level=ticket_type,
                category=ticket_category,
                opening_comment=opening_remarks,
            )
        )
        session.commit()

    embed = SersiEmbed(
        title=f"{ticket_type} Ticket Received",
        description=f"{ticket_creator.mention} ({ticket_creator.id}) has submitted a {ticket_type} Ticket.",
        fields={"Opening Remarks": opening_remarks},
        footer=ticket_creator.display_name,
        thumbnail_url=ticket_creator.avatar.url,
    )

    await channel.send(embed=embed)
    
    return channel
