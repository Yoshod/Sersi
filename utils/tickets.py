import nextcord
import sqlite3
from utils.base import create_unique_id
from utils.config import Configuration


def ticket_check(
    config: Configuration, proposed_ticketer: nextcord.Member, ticket_type: str
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM tickets 
        WHERE ticket_creator_id = ? 
         AND ticket_escalation_initial = ? 
         AND ticket_active = 1
        """,
        (proposed_ticketer.id, ticket_type),
    )

    tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    if len(tickets) > 2:
        return True

    else:
        return False


async def ticket_create(
    config: Configuration,
    interaction: nextcord.Interaction,
    ticket_creator: nextcord.Member,
    ticket_type,
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

    ticket_id = create_unique_id

    channel = await interaction.guild.create_text_channel(ticket_id)

    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tickets (ticket_id, ticket_escalation_initial, ticket_channel_id, ticket_creator_id, ticket_active, timestamp_opened, priority_initial, survey_sent) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            ticket_id,
            ticket_type,
        ),
    )
