import io
import typing
from datetime import datetime

import nextcord
from nextcord.ui import View, Button, Modal, TextInput

from utils.base import get_page, make_transcript
from utils.config import Configuration
from utils.database import db_session, Ticket, TicketSurvey, TicketAudit
from utils.sersi_embed import SersiEmbed
from utils.perms import (
    permcheck,
    is_admin,
    is_mod_lead,
    is_mod,
    is_cet,
    is_cet_lead,
)


def ticket_check(proposed_ticketer: nextcord.Member | nextcord.User, **kwargs) -> bool:
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


async def ticket_permcheck(
    interaction: nextcord.Interaction, escalation_level: str
) -> bool:
    match escalation_level:
        case "Moderator":
            return await permcheck(interaction, is_mod)
        case "Moderation Lead":
            return await permcheck(interaction, is_mod_lead)
        case "Community Engagement":
            return await permcheck(interaction, is_cet)
        case "Community Engagement Lead":
            return await permcheck(interaction, is_cet_lead)
        case _:
            return await permcheck(interaction, is_admin)


def allowed_escalation_levels(member: nextcord.Member) -> list[str]:
    available_levels = []

    if is_mod(member):
        available_levels.append("Moderator")
    if is_mod_lead(member):
        available_levels.append("Moderation Lead")
    if is_cet(member):
        available_levels.append("Community Engagement")
    if is_cet_lead(member):
        available_levels.append("Community Engagement Lead")
    if is_admin(member):
        available_levels.append("Administrator")

    return available_levels


def ticket_log_channel(
    config: Configuration, escalation_level: str
) -> nextcord.TextChannel:
    match escalation_level:
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


def ticket_overwrites(
    config: Configuration,
    guild: nextcord.Guild,
    escalation_level: str,
    ticket_creator: nextcord.Member,
) -> dict:
    overwrites = {
        guild.default_role: nextcord.PermissionOverwrite(
            read_messages=False, send_messages=True
        ),
        guild.me: nextcord.PermissionOverwrite(read_messages=True),
        ticket_creator: nextcord.PermissionOverwrite(read_messages=True),
    }

    match escalation_level:
        case "Moderator":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.moderator
                    ): nextcord.PermissionOverwrite(read_messages=True),
                    guild.get_role(
                        config.permission_roles.trial_moderator
                    ): nextcord.PermissionOverwrite(read_messages=True),
                }
            )

        case "Moderation Lead":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.senior_moderator
                    ): nextcord.PermissionOverwrite(read_messages=True),
                }
            )

        case "Community Engagement":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.cet
                    ): nextcord.PermissionOverwrite(read_messages=True),
                }
            )

        case "Community Engagement Lead":
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.cet_lead
                    ): nextcord.PermissionOverwrite(read_messages=True),
                }
            )

        case _:
            overwrites.update(
                {
                    guild.get_role(
                        config.permission_roles.dark_moderator
                    ): nextcord.PermissionOverwrite(read_messages=True)
                }
            )

    return overwrites


async def ticket_create(
    config: Configuration,
    guild: nextcord.Guild,
    ticket_creator: nextcord.Member,
    ticket_type: str,
    ticket_category: str,
    opening_remarks: str,
    ticket_subcategory: str = None,
):
    match ticket_type:
        case "Moderator":
            type_name = "mod"
            ping = config.permission_roles.moderator
        case "Moderation Lead":
            type_name = "mod-lead"
            ping = config.permission_roles.moderator
        case "Community Engagement":
            type_name = "cet"
            ping = config.permission_roles.cet
        case "Community Engagement Lead":
            type_name = "cet-lead"
            ping = config.permission_roles.cet
        case "Administrator":
            type_name = "admin"
            ping = config.permission_roles.dark_moderator

    channel_category = nextcord.utils.get(guild.categories, name="STAFF SUPPORT")

    with db_session(ticket_creator) as session:
        ticket_number = (session.query(Ticket).count()) + 1

        channel = await guild.create_text_channel(
            f"{type_name}-ticket-{ticket_number:04d}",
            overwrites=ticket_overwrites(config, guild, ticket_type, ticket_creator),
            category=channel_category,
        )
        if channel is None:
            return

        ticket_name = ticket_category.lower() if ticket_category else "ticket"

        session.add(
            Ticket(
                id=f"{ticket_name}-{ticket_number:04d}",
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

    await channel.send(f"<@&{ping}>", embed=embed)

    return channel


async def ticket_close(
    config: Configuration,
    guild: nextcord.Guild,
    ticket: Ticket,
    ticket_closer: nextcord.Member,
    ticket_channel: nextcord.TextChannel = None,
) -> str | None:
    if ticket_channel is None:
        ticket_channel = guild.get_channel(ticket.channel)
    if ticket_channel is None:
        return False

    ticketer_avatar = nextcord.Embed.Empty
    ticketer = guild.get_member(ticket.creator)
    if ticketer is None:
        try:
            ticketer = await guild.fetch_member(ticket.creator)

        except nextcord.NotFound:
            ticketer = None

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

    transcript_channel = guild.get_channel(
        ticket_log_channel(config, ticket.escalation_level)
    )
    if transcript_channel is None:
        return False
    transcript = await make_transcript(ticket_channel, transcript_channel, embed)
    if transcript is None:
        return False
    await ticket_channel.delete(
        reason=f"Ticket closed by {ticket_closer.display_name} ({ticket_closer.id})"
    )

    if ticket.category is None or ticket.subcategory is None:
        await transcript_channel.send(
            f"{config.emotes.fail} Ticket {ticket.id} was closed without a category or subcategory.\n"
            f"<@{ticket_closer.id}> please set the category and subcategory for this ticket."
        )

    if ticketer is None:
        return True

    dm_embed = SersiEmbed(
        title=f"{ticket.escalation_level} Ticket Closed",
        description=f"Your {ticket.escalation_level} Ticket has been closed on {guild.name}.\n\n"
        "Here is the transcript of your ticket.",
        thumbnail_url=guild.icon.url,
        footer=guild.name,
    )

    transcript_file = nextcord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{ticket_channel.name}.html",
    )

    await ticketer.send(embed=dm_embed, file=transcript_file)

    return True


async def ticket_escalate(
    config: Configuration,
    guild: nextcord.Guild,
    ticket: Ticket,
    ticket_escalator: nextcord.Member,
    escalation_level: str,
    ticket_channel: nextcord.TextChannel = None,
):
    if ticket_channel is None:
        ticket_channel = guild.get_channel(ticket.channel)
    if ticket_channel is None:
        return False

    ticket_creator = guild.get_member(ticket.creator)
    if ticket_creator is None:
        ticket_creator = await guild.fetch_member(ticket.creator)
    if ticket_creator is None:
        return False

    overwrites = ticket_overwrites(config, guild, escalation_level, ticket_creator)

    match escalation_level:
        case "Moderator":
            type_name = "mod"
        case "Moderation Lead":
            type_name = "mod-lead"
        case "Community Engagement":
            type_name = "cet"
        case "Community Engagement Lead":
            type_name = "cet-lead"
        case "Administrator":
            type_name = "admin"

    await ticket_channel.edit(
        name=f"{type_name}-ticket-{int(ticket.id.split('-')[-1]):04d}",
        overwrites=overwrites,
        reason=f"Ticket escalated to {escalation_level} by {ticket_escalator.display_name} ({ticket_escalator.id})",
    )

    embed = SersiEmbed(
        title=f"{escalation_level} Ticket Escalated",
        description=f"{ticket_escalator.mention} ({ticket_escalator.id}) has escalated a {ticket.escalation_level} Ticket.",
        fields={
            "Ticket Opened By": f"<@{ticket.creator}> ({ticket.creator})",
            "Opening Remarks": ticket.opening_comment,
            "Ticket Escalated By": f"<@{ticket_escalator.id}> ({ticket_escalator.id})",
            "Ticket Escalated To": escalation_level,
            "Category": f"{ticket.category or '`N/A`'} - {ticket.subcategory or '`N/A`'}",
        },
        footer=ticket_escalator.display_name,
        footer_icon=ticket_escalator.avatar.url,
        thumbnail_url=ticket_creator.avatar.url,
    )

    prev_log_channel = guild.get_channel(
        ticket_log_channel(config, ticket.escalation_level)
    )
    if prev_log_channel is not None:
        await prev_log_channel.send(embed=embed)

    log_channel = guild.get_channel(ticket_log_channel(config, escalation_level))
    if log_channel is not None:
        await log_channel.send(embed=embed)

    return True


async def send_survey(
    guild: nextcord.Guild,
    ticket: Ticket,
    ticket_name: str,
) -> TicketSurvey | None:
    ticket_creator = guild.get_member(ticket.creator)
    if ticket_creator is None:
        ticket_creator = await guild.fetch_member(ticket.creator)
    if ticket_creator is None:
        return None

    embed = SersiEmbed(
        title=f"{guild.name} Ticket Survey",
        description=f"Please take a moment to fill out the following survey regarding your experience with {ticket_name}.\n\n"
        "Press a button below to select your rating. You will be prompted to provide additional feedback after selecting a rating.",
        fields={
            "Opening Remarks": ticket.opening_comment,
            "Closing Remarks": ticket.closing_comment,
            "Category": f"{ticket.category or '`N/A`'} - {ticket.subcategory or '`N/A`'}",
        },
        footer=f"{guild.name}",
        footer_icon=ticket_creator.avatar.url,
        thumbnail_url=guild.icon.url,
    )

    view = View(timeout=None, auto_defer=False)
    view.add_item(
        Button(
            style=nextcord.ButtonStyle.red,
            label="Terrible",
            custom_id=f"ticket-survey:{ticket.id}:1",
        )
    )
    view.add_item(
        Button(
            style=nextcord.ButtonStyle.red,
            label="Poor",
            custom_id=f"ticket-survey:{ticket.id}:2",
        )
    )
    view.add_item(
        Button(
            style=nextcord.ButtonStyle.gray,
            label="Satisfactory",
            custom_id=f"ticket-survey:{ticket.id}:3",
        )
    )
    view.add_item(
        Button(
            style=nextcord.ButtonStyle.blurple,
            label="Good",
            custom_id=f"ticket-survey:{ticket.id}:4",
        )
    )
    view.add_item(
        Button(
            style=nextcord.ButtonStyle.green,
            label="Great",
            custom_id=f"ticket-survey:{ticket.id}:5",
        )
    )

    await ticket_creator.send(embed=embed, view=view)

    return TicketSurvey(ticket_id=ticket.id, member=ticket.creator)


def ticket_audit_logs(
    config: Configuration, page: int, per_page: int, ticket_id: str
) -> typing.Tuple[typing.Optional[list[TicketAudit | None]], int, int]:
    with db_session() as session:
        audit_logs: list[TicketAudit] = (
            session.query(TicketAudit)
            .filter_by(ticket_id=ticket_id)
            .order_by(TicketAudit.timestamp.desc())
            .all()
        )

    if not audit_logs:
        return None, 0, 0

    return get_page(audit_logs, page, per_page)


class SurveyModal(Modal):
    def __init__(
        self, config: Configuration, guild: nextcord.Guild, ticket_id: str, rating: int
    ):
        super().__init__("Survey")
        self.config = config
        self.guild = guild
        self.ticket_id = ticket_id
        self.rating = rating

        self.comment = TextInput(
            label="Comment",
            min_length=8,
            max_length=1024,
            required=True,
            placeholder="Please provide a brief description of your experience",
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.comment)

    async def callback(self, interaction: nextcord.Interaction):
        received = datetime.utcnow()
        with db_session(interaction.user) as session:
            survey: TicketSurvey = (
                session.query(TicketSurvey)
                .filter_by(ticket_id=self.ticket_id, member=interaction.user.id)
                .first()
            )
            if survey is None:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} Could not find survey, please contact administrator.",
                    ephemeral=True,
                )
                return
            survey.rating = self.rating
            survey.comment = self.comment.value
            survey.received = received
            session.commit()

            await interaction.response.send_message(
                f"{self.config.emotes.success} Thank you for your feedback!",
            )

            await interaction.message.edit(view=None)

            ticket: Ticket = session.query(Ticket).filter_by(id=self.ticket_id).first()
            if ticket is None:
                return

        channel = self.guild.get_channel(
            ticket_log_channel(self.config, ticket.escalation_level)
        )
        if channel is None:
            return

        embed = SersiEmbed(
            title=f"{ticket.escalation_level} Ticket Survey Received",
            fields=[
                {
                    "Ticket ID": ticket.id,
                    "Category": ticket.category or "N/A",
                    "Subcategory": ticket.subcategory or "N/A",
                },
                {
                    "Creator": interaction.user.mention,
                    "Rating": self.rating,
                    "Received": f"<t:{int(received.timestamp())}:F>",
                },
                {"Comment": self.comment.value},
            ],
            footer=interaction.user.display_name,
            footer_icon=interaction.user.avatar.url,
            thumbnail_url=self.guild.get_member(ticket.creator).avatar.url,
        )
        await channel.send(embed=embed)


class ReportModal(Modal):
    def __init__(self, config: Configuration, message: nextcord.Message):
        super().__init__("Report Message")
        self.config = config
        self.message = message

        self.report_remarks = nextcord.ui.TextInput(
            label="Report Remarks",
            min_length=8,
            max_length=1024,
            required=True,
            placeholder="Please provide a brief description of the reason for the report",
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.report_remarks)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        channel = await ticket_create(
            self.config,
            interaction.guild,
            interaction.user,
            "Moderator",
            "Report",
            self.report_remarks.value,
            ticket_subcategory="Message Report",
        )
        if channel is None:
            await interaction.followup.send(
                f"{self.config.emotes.fail} An error occurred while creating your ticket. Please try again later.",
                ephemeral=True,
            )
            return

        reported_message_embed = SersiEmbed(
            title="Reported Message",
            description=self.message.content,
            fields=[
                {
                    "Author": self.message.author.mention,
                    "Channel": self.message.channel.mention,
                    "Message Link": self.message.jump_url,
                }
            ],
            footer=f"Reported by {interaction.user.display_name}",
            footer_icon=interaction.user.avatar.url,
            thumbnail_url=self.message.author.avatar.url,
        )

        await channel.send(embed=reported_message_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} Message reported! You can find your ticket at {channel.mention}.",
            ephemeral=True,
        )
