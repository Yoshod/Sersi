import nextcord
from nextcord.ext import commands, application_checks
from utils.database import GlobalSession, guild_db_manager, Guilds, Modules
from utils.sersi_embed import SersiEmbed


class ModuleSelection(nextcord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Select the modules you would like to enable.",
            options=[
                nextcord.SelectOption(label="Initial Testing", value="testing"),
                nextcord.SelectOption(label="Moderation", value="moderation"),
                nextcord.SelectOption(label="Miscellaneous", value="misc"),
            ],
            min_values=1,
        )

    async def callback(self, interaction: nextcord.Interaction):
        with guild_db_manager.get_session(interaction.guild.id) as session:
            for module in self.values:
                module_db = Modules(guild_id=interaction.guild.id, module_name=module)
                session.add(module_db)
            session.commit()

        await interaction.response.send_message(
            "Modules have been enabled for this server.",
            ephemeral=True,
        )

        with GlobalSession() as session:
            guild: Guilds = session.query(Guilds).get(interaction.guild.id)
            guild.finished_setup = True
            session.commit()


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup",
        description="Set up the bot for your server.",
    )
    @application_checks.has_guild_permissions(administrator=True)
    async def setup(self, interaction: nextcord.Interaction):
        with GlobalSession() as session:
            existing_guild: Guilds = session.query(Guilds).get(interaction.guild.id)

            if existing_guild.finished_setup:
                return await interaction.response.send_message(
                    "The bot has already been set up for this server.",
                    ephemeral=True,
                )

            new_guild = Guilds(guild_id=interaction.guild.id, is_testing=True)
            session.add(new_guild)
            session.commit()

        guild_db_manager.create_tables(interaction.guild.id)

        embed = SersiEmbed(
            title="Bot Setup (Module Configuration)",
            description="Welcome to the Sersi setup wizard! Firstly, select the modules from the list below that you would like to be **enabled** for your community. You can always change this later if you change your mind.",
        )

        view = nextcord.ui.View()
        view.add_item(ModuleSelection())

        await interaction.response.send_message(embed=embed, view=view)


def setup(bot: commands.Bot):
    bot.add_cog(Setup(bot))
