# import nextcord.slash_command
import nextcord
from nextcord.ext import commands
from configutils import Configuration


class Punish(commands.Cog):

    choices = {
        "probation": 984195306038124558,
        "gaaay": 1006369222831648988,
        "nevermod": 984106366954274886
    }

    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        # Punish.choices = {
        #     "probation": 984195306038124558,
        #     "gaaay": 1006369222831648988,
        #     "nevermod": 984106366954274886
        # }

    @nextcord.slash_command(dm_permission=False)
    async def slash_command_cog(self, interaction: nextcord.Interaction):
        """This is a slash command in a cog"""
        await interaction.response.send_message("Hello I am a slash command in a cog!")

    @nextcord.slash_command(dm_permission=False)
    async def choose_a_number(
        self,
        interaction: nextcord.Interaction,
        number: int = nextcord.SlashOption(
            name="picker",
            choices={"one": 1, "two": 2, "three": 3},
        ),
    ):
        await interaction.response.send_message(f"You chose {number}!")

    # @nextcord.slash_command(dm_permission=False)
    # async def punish(
    #     self,
    #     interaction: nextcord.Interaction,
    #     member: nextcord.Member,
    #     punishment: int = nextcord.SlashOption(
    #         name="punishment role",
    #         choices=choices
    #     )
    # ):
    #     """This is a slash command in a cog"""
    #     await interaction.response.send_message(f"We are punishing {member.name} with {punishment}")


def setup(bot, **kwargs):
    bot.add_cog(Punish(bot, kwargs["config"]))
