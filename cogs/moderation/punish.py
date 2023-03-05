# import nextcord.slash_command
import nextcord
from nextcord.ext import commands
from configutils import Configuration


class Punish(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.choices = {}

        if bot.is_ready():
            self.get_roles()

    def get_roles(self):
        guild = self.bot.get_guild(self.config.guilds.main)
        for role in vars(self.config.punishment_roles):
            roleobj = guild.get_role(vars(self.config.punishment_roles)[role])
            if roleobj is None:
                continue

            role_name = roleobj.name
            role_id = roleobj.id

            self.choices[role_name] = role_id

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
        punishment: str = nextcord.SlashOption(name="punishment_role"),
    ):
        """This is a slash command in a cog"""
        await interaction.response.send_message(
            f"We are punishing {member.name} with {punishment}\nKeylist says: {self.choices[punishment]}."
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.get_roles()

    @punish.on_autocomplete("punishment")
    async def punishment_roles(
        self, interaction: nextcord.Interaction, punishment: str
    ):
        if not punishment:
            await interaction.response.send_autocomplete(self.choices.keys())
            return

        punish_roles = [
            role for role in self.choices if role.lower().startswith(punishment.lower())
        ]
        await interaction.response.send_autocomplete(punish_roles)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Punish(bot, kwargs["config"]))
