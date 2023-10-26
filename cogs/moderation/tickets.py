import nextcord

from utils.tickets import ticket_check
from nextcord.ext import commands
from nextcord.ui import Button, View, Select
from utils.perms import permcheck, is_dark_mod, is_senior_mod, is_mod
from utils.config import Configuration
from utils.base import SersiEmbed


class TicketingSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=True,
        guild_ids=[1166770860787515422, 977377117895536640],
        description="Make a suggestion on European Urbanism",
    )
    async def ticket(self, interaction: nextcord.Interaction):
        pass

    @ticket.subcommand(description="Used to create a ModMail Ticket")
    async def create(
        self,
        interaction: nextcord.Interaction,
        ticket_type: nextcord.Member = nextcord.SlashOption(
            name="ticket_type",
            description="The type of ticket being created",
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
                f"{self.config.emotes.fail} You already have an open {ticket_type} ticket. That one must be closed before another is opened."
            )
            return


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(TicketingSystem(bot, kwargs["config"]))
