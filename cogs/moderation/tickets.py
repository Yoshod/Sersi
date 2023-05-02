import nextcord

from utils.tickets import ticket_check
from nextcord.ext import commands
from utils.config import Configuration


class TicketingSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=True,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Submit a modmail on Adam Something Central",
    )
    async def ticket(self, interaction: nextcord.Interaction):
        pass

    @ticket.subcommand(description="Used to create a Sersi ModMail Ticket")
    async def create(
        self,
        interaction: nextcord.Interaction,
        ticket_type: str = nextcord.SlashOption(
            name="ticket_type",
            description="The type of ticket being created",
            choices={
                "Community Engagement Ticket": "Community Engagement Team",
                "Moderator Ticket": "Moderator",
                "Senior Moderator Ticket": "Senior Moderator",
                "Mega Administrator Ticket": "Mega Administrator",
            },
        ),
        initial_comment: str = nextcord.SlashOption(
            name="initial_comment",
            description="Give a brief description of the reason for the ticket",
        ),
    ):
        if interaction.guild:
            interaction.response.send_message(
                f"{self.config.emotes.fail} This command must be ran in my Direct Messages!",
                ephemeral=True,
            )
            return

        if ticket_check(self.config, interaction.user, ticket_type):
            interaction.response.send_message(
                f"{self.config.emotes.fail} You already have the maximum amount of {ticket_type} tickets. One must be closed before another can be opened."
            )
            return


def setup(bot, **kwargs):
    bot.add_cog(TicketingSystem(bot, kwargs["config"]))
