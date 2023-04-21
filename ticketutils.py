import json
import pickle
import re

import nextcord
import io
import sqlite3
from chat_exporter import export
from baseutils import SersiEmbed
from nextcord.ui import View, Button, Select
from configutils import Configuration


def ticket_check(
    config: Configuration, proposed_ticketer: nextcord.Member, ticket_type: str
):
    conn = sqlite3.connect(config.datafiles.sersi_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tickets WHERE ticket_creator_id = ? AND ticket_escalation_initial = ? AND ticket_active = 1",
        (proposed_ticketer.id, ticket_type),
    )

    tickets = cursor.fetchall()

    cursor.close()
    conn.close()

    if tickets:
        return True

    else:
        return False


def ticket_create(
    config: Configuration,
    interaction: nextcord.Interaction,
    ticket_creator: nextcord.Member,
    ticket_type,
    test=True,
):
    if test:
        guild = interaction.client.get_guild(config.guilds.errors)
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
