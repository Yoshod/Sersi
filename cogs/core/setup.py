import nextcord
from nextcord.ext import commands, application_checks
from utils.database import (
    GlobalSession,
    guild_db_manager,
    Guilds,
    Modules,
    GuildDatabaseManager,
)
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
        )

    async def callback(self, interaction: nextcord.Interaction):
        with guild_db_manager.get_session(interaction.guild.id) as session:
            for module in self.values:
                already_enabled = (
                    session.query(Modules).filter_by(module_name=module).first()
                )
                if already_enabled:
                    session.query(Modules).filter_by(module_name=module).delete()
                    session.commit()
                    module_added = False
                else:
                    module_db = Modules(module_name=module, enabled=True)
                    session.add(module_db)
                    module_added = True
                    session.commit()

        if module_added:
            await interaction.response.send_message(
                "Modules have been enabled for this server.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                "Modules have been updated for this server.",
                ephemeral=True,
            )


class FinishSetup(nextcord.ui.Button):
    def __init__(self):
        super().__init__(style=nextcord.ButtonStyle.green, label="Finish Setup")

    async def callback(self, interaction: nextcord.Interaction):
        with guild_db_manager.get_session(interaction.guild.id) as session:
            modules = session.query(Modules).filter_by(enabled=True).all()

            if not modules:
                return await interaction.response.send_message(
                    "You must enable at least one module to finish setup.",
                    ephemeral=True,
                )

        with GlobalSession() as session:
            guild: Guilds = session.query(Guilds).get(interaction.guild.id)
            guild.finished_setup = True
            session.commit()

        await interaction.response.send_message(
            "Setup has been completed for this server.",
            ephemeral=True,
        )

        await interaction.message.edit(view=None)


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup",
        description="Set up the bot for your server.",
        guild_ids=[977377117895536640],
    )
    @application_checks.has_guild_permissions(administrator=True)
    async def setup(self, interaction: nextcord.Interaction):
        with GlobalSession() as session:
            existing_guild: Guilds = session.query(Guilds).get(interaction.guild.id)

            try:
                if existing_guild.finished_setup:
                    return await interaction.response.send_message(
                        "The bot has already been set up for this server.",
                        ephemeral=True,
                    )
            except AttributeError:
                pass

            try:
                new_guild = Guilds(guild_id=interaction.guild.id, is_testing=True)
                session.add(new_guild)
                session.commit()
            except Exception:
                pass

        guild_db_manager.get_session(interaction.guild.id)
        GuildDatabaseManager().create_tables(interaction.guild.id)

        embed = SersiEmbed(
            title="Bot Setup (Module Configuration)",
            description="Welcome to the Sersi setup wizard! Firstly, select the modules from the list below that you would like to be **enabled** for your community. You can always change this later if you change your mind.",
        )

        view = nextcord.ui.View()
        view.add_item(ModuleSelection())
        view.add_item(FinishSetup())

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


def setup(bot: commands.Bot):
    bot.add_cog(Setup(bot))
