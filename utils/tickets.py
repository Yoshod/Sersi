import nextcord

from utils.channels import make_transcript
from utils.config import Configuration
from utils.database import db_session, Ticket
from utils.sersi_embed import SersiEmbed
from utils.perms import permcheck, is_dark_mod, is_senior_mod, is_mod, is_cet, is_cet_lead


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


async def ticket_permcheck(interaction: nextcord.Interaction, escalation_level: str) -> bool:
    match(escalation_level):
        case "Moderator":
            return permcheck(interaction, is_mod)
        case "Moderation Lead":
            return permcheck(interaction, is_senior_mod)
        case "Community Engagement":
            return permcheck(interaction, is_cet)
        case "Community Engagement Lead":
            return permcheck(interaction, is_cet_lead)
        case _:
            return permcheck(interaction, is_dark_mod)


def ticket_log_channel(config: Configuration, escalation_level: str) -> nextcord.TextChannel:
    match(escalation_level):
        case "Moderator":
            return config.channels.mod_ticket_logs
        case "Moderation Lead":
            return config.channels.senior_ticket_logs
        case "Community Engagement":
            return config.channels.cet_ticket_logs
        case "Community Engagement Lead":
            return config.channels.cet_lead_ticket_logs
        case _:
            return config.channels.admin_ticket_logs


async def ticket_create(
    config: Configuration,
    guild: nextcord.Guild,
    ticket_creator: nextcord.Member,
    ticket_type: str,
    ticket_category: str,
    opening_remarks: str,
    ticket_subcategory: str = None,
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
                subcategory=ticket_subcategory,
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


async def ticket_close(
    config: Configuration,
    guild: nextcord.Guild,
    ticket: Ticket,
    ticket_closer: nextcord.Member,
    ticket_channel: nextcord.TextChannel = None,
) -> str|None:
    if ticket_channel is None:
        ticket_channel = guild.get_channel(ticket.channel)
    if ticket_channel is None:
        return False

    ticketer_avatar = nextcord.Embed.Empty
    ticketer = guild.get_member(ticket.creator)
    if ticketer is None:
        ticketer = await guild.fetch_member(ticket.creator)
    if ticketer is not None:
        ticketer_avatar = ticketer.avatar.url

    embed = SersiEmbed(
        title=f"{ticket.escalation_level} Ticket Closed",
        description=f"{ticket_closer.mention} ({ticket_closer.id}) has closed a {ticket.escalation_level} Ticket.",
        fields={
            "Ticket Opened By": f"<@{ticket.creator}> ({ticket.creator})",
            "Opening Remarks": ticket.opening_comment,
            "Ticket Closed By": f"<@{ticket_closer.id}> ({ticket_closer.id})",
            "Closing Remarks": ticket.closing_comment,
            "Category": f"{ticket.category or '`N/A`'} - {ticket.subcategory or '`N/A`'}",
        },
        footer=ticket_closer.display_name,
        footer_icon=ticket_closer.avatar.url,
        thumbnail_url=ticketer_avatar,
    )

    transcript_channel = guild.get_channel(ticket_log_channel(config, ticket.escalation_level))
    if transcript_channel is None:
        return False
    transcript = await make_transcript(ticket_channel, transcript_channel, embed)
    if transcript is None:
        return False
    await ticket_channel.delete(reason=f"Ticket closed by {ticket_closer.display_name} ({ticket_closer.id})")

    if ticket.category is None or ticket.subcategory is None:
        await transcript_channel.send(
            f"{config.emotes.fail} Ticket {ticket.id} was closed without a category or subcategory.\n"
            f"<@{ticket_closer.id}> please set the category and subcategory for this ticket."
        )

    return True
