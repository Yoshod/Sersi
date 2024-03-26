from datetime import datetime, timedelta

import nextcord
from nextcord.ext import commands
from nextcord.utils import format_dt

from utils.tickets import (
    ticket_check,
    ticket_create,
    ticket_permcheck,
    allowed_escalation_levels,
    ticket_close,
    ticket_escalate,
    send_survey,
    ticket_audit_logs,
    SurveyModal,
    ReportModal,
)

from utils.database import db_session, Ticket, TicketCategory, TicketSurvey
from utils.dialog import TextArea, modal_dialog
from utils.config import Configuration
from utils.sersi_embed import SersiEmbed
from utils.views import PageView


class TicketingSystem(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.last_message: dict[int, datetime] = {}

    @nextcord.slash_command(
        dm_permission=True,
        description="Make a suggestion on The Crossroads",
    )
    async def ticket(self, interaction: nextcord.Interaction):
        pass

    @ticket.subcommand(description="Used to create a Ticket")
    async def create(
        self,
        interaction: nextcord.Interaction,
        ticket_type: str = nextcord.SlashOption(
            name="ticket_type",
            description="The type of ticket being created",
            choices=[
                "Moderator",
                "Moderation Lead",
                "Community Engagement",
                "Community Engagement Lead",
                "Administrator",
            ],
        ),
        initial_comment: str = nextcord.SlashOption(
            name="opening_remarks",
            description="Give a brief description of the reason for the ticket",
        ),
        category: str = nextcord.SlashOption(
            name="category",
            description="The category of the ticket",
            required=False,
        ),
    ):
        filter = {"escalation_level": ticket_type}
        if category:
            filter["category"] = category

        if ticket_check(
            interaction.user,
            **filter,
        ):
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You already have an open {ticket_type} ticket of the same category."
                " You need to close that one before opening a new one.",
            )
            return

        await interaction.response.defer(ephemeral=True)

        channel = await ticket_create(
            self.config,
            interaction.guild or self.bot.get_guild(self.config.guilds.main),
            interaction.user,
            ticket_type,
            category,
            initial_comment,
        )
        if channel is None:
            await interaction.followup.send(
                f"{self.config.emotes.fail} An error occurred while creating your ticket. Please try again later.",
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            f"{self.config.emotes.success} Your ticket has been created! You can find it at {channel.mention}.",
            ephemeral=True,
        )

    @ticket.subcommand(description="Used to close a Ticket")
    async def close(
        self,
        interaction: nextcord.Interaction,
        close_reason: str = nextcord.SlashOption(
            name="closing_remarks",
            description="Give a brief description of the reason for the ticket closure",
        ),
        ticket_id: str = nextcord.SlashOption(
            name="ticket",
            description="The ticket to close",
            required=False,
        ),
        category: str = nextcord.SlashOption(
            name="category",
            description="Provide category for the ticket",
            required=False,
        ),
        subcategory: str = nextcord.SlashOption(
            name="subcategory",
            description="Provide subcategory for the ticket",
            required=False,
        ),
        do_survey: bool = nextcord.SlashOption(
            name="send_survey",
            description="Send a survey to the ticket creator",
            required=False,
            choices={
                "Yes": True,
                "No": False,
            },
            default=True,
        ),
    ):
        with db_session(interaction.user) as session:
            filter_dict = {"active": True}
            if ticket_id:
                filter_dict["id"] = ticket_id
            else:
                filter_dict["channel"] = interaction.channel.id

            ticket: Ticket = session.query(Ticket).filter_by(**filter_dict).first()
            if ticket is None:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} No open ticket with that ID exists."
                    if ticket_id
                    else f"{self.config.emotes.fail} This channel is not a ticket channel",
                    ephemeral=True,
                )
                return

            if not await ticket_permcheck(interaction, ticket.escalation_level):
                return

            if category:
                ticket.category = category
            if subcategory:
                ticket.subcategory = subcategory
            session.commit()

            await interaction.response.defer(ephemeral=True)

            channel = interaction.guild.get_channel(ticket.channel)
            if channel is None:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} could not find ticket channel, please contact administartor.",
                    ephemeral=True,
                )
                return

            if not await ticket_close(
                self.config,
                interaction.guild,
                ticket,
                interaction.user,
                channel,
            ):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} An error occurred while closing your ticket.",
                    ephemeral=True,
                )
                return

            ticket.active = False
            ticket.closing_comment = close_reason
            ticket.closed = datetime.utcnow()
            session.commit()

            if do_survey:
                survey = await send_survey(
                    interaction.guild,
                    ticket,
                    channel.name,
                )
                if survey is None:
                    await interaction.followup.send(
                        f"{self.config.emotes.fail} Could not send survey to the ticketer.",
                        ephemeral=True,
                    )
                else:
                    session.add(survey)
                    session.commit()

        if interaction.channel.id != channel.id:
            await interaction.followup.send(
                f"{self.config.emotes.success} Ticket has been closed!",
                ephemeral=True,
            )

    @ticket.subcommand(description="Used to change ticket escalation level")
    async def escalate(
        self,
        interaction: nextcord.Interaction,
        escalation_level: str = nextcord.SlashOption(
            name="escalation_level",
            description="The escalation level to change to",
            choices=[
                "Moderator",
                "Moderation Lead",
                "Community Engagement",
                "Community Engagement Lead",
                "Administrator",
            ],
        ),
        ticket_id: str = nextcord.SlashOption(
            name="ticket",
            description="The ticket to escalate",
            required=False,
        ),
    ):
        with db_session(interaction.user) as session:
            filter_dict = {"active": True}
            if ticket_id:
                filter_dict["id"] = ticket_id
            else:
                filter_dict["channel"] = interaction.channel.id

            ticket: Ticket = session.query(Ticket).filter_by(**filter_dict).first()
            if ticket is None:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} No open ticket with that ID exists."
                    if ticket_id
                    else f"{self.config.emotes.fail} This channel is not a ticket channel",
                    ephemeral=True,
                )
                return
            if ticket.escalation_level == escalation_level:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} Ticket escalation level is already {escalation_level}.",
                    ephemeral=True,
                )
                return

            if not await ticket_permcheck(interaction, ticket.escalation_level):
                return

            await interaction.response.defer(ephemeral=True)

            if not await ticket_escalate(
                self.config,
                interaction.guild,
                ticket,
                interaction.user,
                escalation_level,
            ):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} An error occurred while trying to escalate ticket.",
                    ephemeral=True,
                )
                return

            ticket.escalation_level = escalation_level
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Ticket has been escalated to {escalation_level}!",
            ephemeral=True,
        )

    @ticket.subcommand(description="Used to change ticket category")
    async def recategorize(
        self,
        interaction: nextcord.Interaction,
        category: str = nextcord.SlashOption(
            name="category",
            description="The category to change to",
        ),
        subcategory: str = nextcord.SlashOption(
            name="subcategory",
            description="The subcategory to change to",
            required=False,
        ),
        ticket_id: str = nextcord.SlashOption(
            name="ticket",
            description="The ticket to recategorize",
            required=False,
        ),
    ):
        with db_session(interaction.user) as session:
            filter_dict = {}
            if ticket_id:
                filter_dict["id"] = ticket_id
            else:
                filter_dict["channel"] = interaction.channel.id

            ticket: Ticket = session.query(Ticket).filter_by(**filter_dict).first()
            if ticket is None:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} No open ticket with that ID exists."
                    if ticket_id
                    else f"{self.config.emotes.fail} This channel is not a ticket channel",
                    ephemeral=True,
                )
                return

            if not await ticket_permcheck(interaction, ticket.escalation_level):
                return

            await interaction.response.defer(ephemeral=True)

            ticket.category = category
            if subcategory:
                ticket.subcategory = subcategory

            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Ticket has been recategorized!",
            ephemeral=True,
        )

    @ticket.subcommand(
        description="Used to get ticket information from database record",
    )
    async def info(
        self,
        interaction: nextcord.Interaction,
        ticket_id: str = nextcord.SlashOption(
            name="ticket",
            description="The ticket to get info for",
        ),
    ):
        with db_session(interaction.user) as session:
            ticket: Ticket = session.query(Ticket).filter_by(id=ticket_id).first()
            if ticket is None:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} Ticket not found.",
                    ephemeral=True,
                )
                return

            if not await ticket_permcheck(interaction, ticket.escalation_level):
                return

            await interaction.response.defer()

            ticket_creator = interaction.guild.get_member(ticket.creator)
            ticket_channel = interaction.guild.get_channel(ticket.channel)

            embed_fields = [
                {
                    "Ticket ID": ticket.id,
                    "Ticket Creator": ticket_creator.mention,
                    "Ticket Channel": ticket_channel.mention
                    if ticket_channel
                    else "`deleted channel`",
                },
                {
                    "Escalation Level": ticket.escalation_level,
                    "Category": ticket.category or "N/A",
                    "Subcategory": ticket.subcategory or "N/A",
                },
                {
                    "Open": f"{self.config.emotes.success}"
                    if ticket.active
                    else f"{self.config.emotes.fail}",
                    "Opened": f"<t:{int(ticket.created.timestamp())}:F>",
                },
                {"Opening Comment": ticket.opening_comment},
            ]

            if not ticket.active:
                embed_fields[-2].update(
                    {"Closed": f"<t:{int(ticket.closed.timestamp())}:F>"}
                )
                embed_fields.append({"Closing Comment": ticket.closing_comment})

            survey = session.query(TicketSurvey).filter_by(ticket_id=ticket.id).first()
            embed_fields.append(
                {
                    "Survey Sent": self.config.emotes.success
                    if survey
                    else self.config.emotes.fail,
                }
            )
            if survey:
                if survey.received:
                    embed_fields[-1].update(
                        {
                            "Survey Rating": survey.rating,
                            "Survey Received": f"<t:{int(survey.received.timestamp())}:F>",
                        }
                    )
                    embed_fields.append({"Survey Comment": survey.comment})

            ticket_embed = SersiEmbed(
                title=f"{ticket.escalation_level} Ticket",
                fields=embed_fields,
                footer=f"Ticket created at {ticket.created}",
                thumbnail_url=ticket_creator.avatar.url,
            )

            await interaction.followup.send(embed=ticket_embed)

    @ticket.subcommand(description="Get ticket audit log")
    async def audit(
        self,
        interaction: nextcord.Interaction,
        ticket_id: str = nextcord.SlashOption(
            name="ticket",
            description="The ticket to get info for",
        ),
    ):
        with db_session(interaction.user) as session:
            ticket: Ticket = session.query(Ticket).filter_by(id=ticket_id).first()
            if ticket is None:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} Ticket not found.",
                    ephemeral=True,
                )
                return

        if not await ticket_permcheck(interaction, ticket.escalation_level):
            return

        await interaction.response.defer()

        ticket_creator = interaction.guild.get_member(ticket.creator)

        audit_embed = SersiEmbed(
            title=f"Ticket `{ticket.id}` Audit Logs",
            thumbnail_url=ticket_creator.avatar.url,
            footer_icon=interaction.guild.icon.url,
        )

        view = PageView(
            config=self.config,
            base_embed=audit_embed,
            fetch_function=ticket_audit_logs,
            author=interaction.user,
            entry_form="<@{entry.author}>\n{entry.old_value} => {entry.new_value}",
            field_title="{entries[0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=1,
            ticket_id=ticket.id,
        )

        await view.send_followup(interaction)

    @ticket.subcommand(description="Send a message to ticket channel while timed out")
    async def send_message(
        self,
        interaction: nextcord.Interaction,
        ticket: str = nextcord.SlashOption(
            name="ticket",
            description="The ticket to send message to",
        ),
    ):
        guild = self.bot.get_guild(self.config.guilds.main)
        member = guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You are not a member of The Crossroads.",
                ephemeral=True,
            )
            return
        if member.communication_disabled_until is None and not self.config.bot.dev_mode:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You are currently not timed out, please use ticket channel instead.",
                ephemeral=True,
            )
            return

        with db_session(interaction.user) as session:
            ticket: Ticket = (
                session.query(Ticket)
                .filter_by(id=ticket, creator=interaction.user.id, active=True)
                .first()
            )
        if ticket is None:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} No such open ticket found.",
                ephemeral=True,
            )
            return

        channel = guild.get_channel(ticket.channel)
        if channel is None:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Could not find ticket channel, please contact administartor.",
                ephemeral=True,
            )
            return
        
        if channel.slowmode_delay > 0 and channel.id in self.last_message:
            slowed_until = self.last_message[channel.id] + timedelta(seconds=channel.slowmode_delay)
            if datetime.utcnow() < slowed_until:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} You have to wait until {format_dt(slowed_until, 'T')} ({format_dt(slowed_until, 'R')}) to send another message.",
                    ephemeral=True,
                )
                return
        self.last_message[channel.id] = datetime.utcnow()

        response = await modal_dialog(
            interaction,
            f"Send Message to {channel.name}",
            message=TextArea(
                "Message",
                required=True,
                placeholder="please provide a message",
                max_length=4000,
            ),
        )

        embed = SersiEmbed(
            author=member,
            description=response["message"],
            footer=f"{interaction.user} ({interaction.user.id})",
            footer_icon=interaction.user.avatar.url,
            colour=member.top_role.colour,
        )

        message = await channel.send(embed=embed)
        await interaction.followup.send(
            f"{self.config.emotes.success} Your message has been sent! {message.jump_url}",
        )

    @create.on_autocomplete("category")
    @close.on_autocomplete("category")
    @recategorize.on_autocomplete("category")
    async def category_autocomplete(
        self, interaction: nextcord.Interaction, category: str
    ):
        with db_session() as session:
            categories: list[TicketCategory] = (
                session.query(TicketCategory)
                .filter(TicketCategory.category.ilike(f"%{category}%"))
                .group_by(TicketCategory.category)
                .limit(25)
                .all()
            )
            return [category.category for category in categories]

    @close.on_autocomplete("subcategory")
    @recategorize.on_autocomplete("subcategory")
    async def subcategory_autocomplete(
        self, interaction: nextcord.Interaction, subcategory: str, category: str
    ):
        with db_session() as session:
            subcategories: list[TicketCategory] = (
                session.query(TicketCategory)
                .filter_by(category=category)
                .filter(TicketCategory.subcategory.ilike(f"%{subcategory}%"))
                .limit(25)
                .all()
            )
            return [subcategory.subcategory for subcategory in subcategories]

    @close.on_autocomplete("ticket_id")
    @escalate.on_autocomplete("ticket_id")
    async def ticket_autocomplete(
        self, interaction: nextcord.Interaction, ticket_id: str
    ):
        with db_session() as session:
            tickets: list[Ticket] = (
                session.query(Ticket)
                .filter_by(active=True)
                .filter(
                    Ticket.id.ilike(f"%{ticket_id}%"),
                    Ticket.escalation_level.in_(
                        allowed_escalation_levels(interaction.user)
                    ),
                )
                .group_by(Ticket.id)
                .limit(25)
                .all()
            )
            return [ticket.id for ticket in tickets]

    @info.on_autocomplete("ticket_id")
    @audit.on_autocomplete("ticket_id")
    @recategorize.on_autocomplete("ticket_id")
    async def ticket_all_autocomplete(
        self, interaction: nextcord.Interaction, ticket_id: str
    ):
        with db_session() as session:
            tickets: list[Ticket] = (
                session.query(Ticket)
                .filter(
                    Ticket.id.ilike(f"%{ticket_id}%"),
                    Ticket.escalation_level.in_(
                        allowed_escalation_levels(interaction.user)
                    ),
                )
                .group_by(Ticket.id)
                .limit(25)
                .all()
            )
            return [ticket.id for ticket in tickets]

    @send_message.on_autocomplete("ticket")
    async def ticket_send_message_autocomplete(
        self, interaction: nextcord.Interaction, ticket: str
    ):
        with db_session(interaction.user) as session:
            tickets: list[Ticket] = (
                session.query(Ticket)
                .filter_by(creator=interaction.user.id, active=True)
                .filter(Ticket.id.ilike(f"%{ticket}%"))
                .group_by(Ticket.id)
                .limit(25)
                .all()
            )
            return [ticket.id for ticket in tickets]

    @nextcord.message_command(
        name="Report Message",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def report_message(
        self, interaction: nextcord.Interaction, message: nextcord.Message
    ):
        await interaction.response.send_modal(ReportModal(self.config, message))

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return
        if not interaction.data["custom_id"].startswith("ticket"):
            return

        action, ticket_id, rating = interaction.data["custom_id"].split(":")

        match action:
            case "ticket-survey":
                await interaction.response.send_modal(
                    SurveyModal(
                        self.config,
                        self.bot.get_guild(self.config.guilds.main),
                        ticket_id,
                        rating,
                    )
                )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(TicketingSystem(bot, kwargs["config"]))
