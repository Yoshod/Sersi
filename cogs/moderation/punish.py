# import nextcord.slash_command
import nextcord
from nextcord.ext import commands
from configutils import Configuration


class Punish(commands.Cog):

    choices = {}

    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

        self.keylist = {}
        self.guild = self.bot.get_guild(config.guilds.main)
        for role in vars(config.punishment_roles):
            roleobj = self.guild.get_role(vars(config.punishment_roles)[role])

            role_name = roleobj.name
            role_id = roleobj.id

            self.keylist[role] = role_id
            Punish.choices[role] = role_name

            print(Punish.choices)
            print(self.keylist)

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

    @nextcord.slash_command(name="punish_user", dm_permission=False)
    async def punish(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        punishment: str = nextcord.SlashOption(name="punishment_role", choices=choices),
    ):
        """This is a slash command in a cog"""
        await interaction.response.send_message(
            f"We are punishing {member.name} with {punishment}\nKeylist says: {self.keylist[punishment]}."
        )


def setup(bot, **kwargs):
    bot.add_cog(Punish(bot, kwargs["config"]))
