# import nextcord.slash_command
import nextcord
from nextcord.ext import commands
from configutils import Configuration
from permutils import permcheck, is_staff


class Punish(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.choices: dict[str, int] = {}

        if bot.is_ready():
            self.get_roles()

    def get_roles(self):
        guild = self.bot.get_guild(self.config.guilds.main)
        for role_id in self.config.punishment_roles:
            role = guild.get_role(self.config.punishment_roles[role_id])

            if role is not None:
                self.choices[role.name] = role.id

    @nextcord.slash_command(name="punish_user", dm_permission=False)
    async def punish(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        punishment: str = nextcord.SlashOption(name="punishment_role"),
    ):
        """Adds a punishment role to the user."""

        if not await permcheck(interaction, is_staff):
            return

        if punishment not in self.choices:
            await interaction.response.send_message(
                "That is not a valid punishment role."
            )
            return

        role = member.guild.get_role(self.choices[punishment])

        await member.add_roles(role)

        await interaction.response.send_message(
            f"Uh-oh, {member.mention} posted cringe and has been given the role {role.mention} as punishment."
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
