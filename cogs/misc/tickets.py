from datetime import datetime

import nextcord

from utils.tickets import ticket_check, ticket_create, ticket_permcheck, ticket_close
from nextcord.ext import commands
from nextcord.ui import Modal
from utils.database import db_session, Ticket, TicketCategory
from utils.config import Configuration
from utils.base import SersiEmbed


class TicketingSystem(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=True,
        description="Make a suggestion on European Urbanism",
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
            f"{self.config.emotes.success} Your ticket has been created! You can find it at {channel.jump_url}.",
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
    ):
        with db_session(interaction.user) as session:
            filter_dict = {"active": True}
            if ticket_id:
                filter_dict["id"] = ticket_id
            else:
                filter_dict["channel"] = interaction.channel.id

            ticket: Ticket = (
                session.query(Ticket)
                .filter_by(**filter_dict)
                .first()
            )
            if ticket is None:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} No open ticket with that ID exists."
                    if ticket_id else
                    f"{self.config.emotes.fail} This channel is not a ticket channel",
                    ephemeral=True,
                )
                return
            
            if not await ticket_permcheck(interaction, ticket.escalation_level):
                return
            
            await interaction.response.defer(ephemeral=True)

            channel = interaction.guild.get_channel(ticket.channel)
            if channel is None:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} could not find ticket channel, please contact administartor.",
                    ephemeral=True,
                )
                return
            
            if category:
                ticket.category = category
            if subcategory:
                ticket.subcategory = subcategory
            ticket.active = False
            ticket.closing_comment = close_reason
            ticket.closed = datetime.utcnow()

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

            session.commit()
        
    @create.on_autocomplete("category")
    @close.on_autocomplete("category")
    async def category_autocomplete(self, interaction: nextcord.Interaction, category: str):
        with db_session() as session:
            categories: list[TicketCategory] = (
                session.query(TicketCategory)
                .filter(TicketCategory.category.ilike(f"%{category}%"))
                .group_by(TicketCategory.category)
                .all()
            )
            return [category.category for category in categories]

    @close.on_autocomplete("subcategory")
    async def subcategory_autocomplete(self, interaction: nextcord.Interaction, subcategory: str, category: str):
        with db_session() as session:
            subcategories: list[TicketCategory] = (
                session.query(TicketCategory)
                .filter_by(category=category)
                .filter(TicketCategory.subcategory.ilike(f"%{subcategory}%"))
                .all()
            )
            return [subcategory.subcategory for subcategory in subcategories]
            
    @close.on_autocomplete("ticket_id")
    async def ticket_autocomplete(self, interaction: nextcord.Interaction, ticket_id: str):
        with db_session() as session:
            tickets: list[Ticket] = (
                session.query(Ticket)
                .filter_by(active=True)
                .filter(Ticket.id.ilike(f"%{ticket_id}%"))
                .group_by(Ticket.id)
                .all()
            )
            return [ticket.id for ticket in tickets]

    
    @nextcord.message_command(
        name="Report Message",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
    )
    async def report_message(self, interaction: nextcord.Interaction, message: nextcord.Message):
        await interaction.response.send_modal(ReportModal(self.config, message))
    

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
            fields=[{
                "Author": self.message.author.mention,
                "Channel": self.message.channel.mention,
                "Message Link": self.message.jump_url,
            }],
            footer=f"Reported by {interaction.user.display_name}",
            footer_icon=interaction.user.avatar.url,
            thumbnail_url=self.message.author.avatar.url,
        )

        await channel.send(embed=reported_message_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} Message reported! You can find your ticket at {channel.jump_url}.",
            ephemeral=True,
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(TicketingSystem(bot, kwargs["config"]))
