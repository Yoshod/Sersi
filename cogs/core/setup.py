import nextcord
from nextcord.ext import commands, application_checks
from utils.database import (
    GlobalSession,
    guild_db_manager,
    Guilds,
    Modules,
    Language,
    GuildDatabaseManager,
)
from utils.sersi_embed import SersiEmbed
from utils.base import encode_button_id, decode_button_id
from utils.language import lang_manager


class ModerationModuleButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Moderation",
            custom_id=encode_button_id("setup", module="moderation"),
            disabled=False,
        )


class LoggingModuleButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Logging",
            custom_id=encode_button_id("setup", module="logging"),
            disabled=False,
        )


class AutomoderationModuleButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Automoderation",
            custom_id=encode_button_id("setup", module="automoderation"),
            disabled=False,
        )


class LevellingModuleButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Levelling",
            custom_id=encode_button_id("setup", module="levelling"),
            disabled=False,
        )


class WelcomeModuleButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Welcome",
            custom_id=encode_button_id("setup", module="welcome"),
            disabled=False,
        )


class SuggestionsModuleButton(nextcord.ui.Button):
    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Suggestions",
            custom_id=encode_button_id("setup", module="suggestions"),
            disabled=False,
        )


class ModulesView(nextcord.ui.View):
    def __init__(self, guild: nextcord.Guild):
        super().__init__(timeout=None)

        with guild_db_manager.get_session(guild.id) as session:
            modules = session.query(Modules).all()
            enabled_modules = [
                module.module_name for module in modules if module.enabled
            ]

        self.add_item(ModerationModuleButton(selected="moderation" in enabled_modules))
        self.add_item(LoggingModuleButton(selected="logging" in enabled_modules))
        self.add_item(
            AutomoderationModuleButton(selected="automoderation" in enabled_modules)
        )
        self.add_item(LevellingModuleButton(selected="levelling" in enabled_modules))
        self.add_item(WelcomeModuleButton(selected="welcome" in enabled_modules))
        self.add_item(
            SuggestionsModuleButton(selected="suggestions" in enabled_modules)
        )


class LanguageSelection(nextcord.ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Select the language for the bot.",
            options=[
                nextcord.SelectOption(label="English", value="en"),
                nextcord.SelectOption(label="Français", value="fr"),
                nextcord.SelectOption(label="Pirate Speak", value="xx"),
            ],
        )

    async def callback(self, interaction: nextcord.Interaction):
        selected_language = self.values[0]
        with guild_db_manager.get_session(interaction.guild.id) as session:
            session.query(Language).delete()
            new_language = Language(language=selected_language)
            session.add(new_language)
            session.commit()

        await interaction.response.send_message(
            f"Language has been set to {selected_language}.",
            ephemeral=True,
        )


class FinishSetup(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            style=nextcord.ButtonStyle.green,
            label="Finish Setup",
            custom_id=encode_button_id("setup", state="finish"),
        )


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup",
        description="Set up the bot for your server.",
        guild_ids=[977377117895536640, 1166770860787515422, 1383162647171567626],
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
            description="Welcome to the Sersi setup wizard! Firstly, select the modules from the list below that you would like to be **enabled** for your community. Then pick which language you would prefer to use. You can always change these later if you change your mind.",
        )

        view = ModulesView(interaction.guild)
        view.add_item(LanguageSelection())
        view.add_item(FinishSetup())

        await interaction.response.send_message(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        if not interaction.data["custom_id"].startswith("setup"):
            return

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        if action == "setup" and "module" in kwargs:
            match kwargs["module"]:
                case "moderation":
                    with guild_db_manager.get_session(interaction.guild.id) as session:
                        module = (
                            session.query(Modules)
                            .filter_by(module_name="moderation")
                            .first()
                        )
                        if not module:
                            module = Modules(module_name="moderation", enabled=True)
                            session.add(module)

                        elif module.enabled:
                            module.enabled = False
                        else:
                            module.enabled = True
                        session.commit()

                case "logging":
                    with guild_db_manager.get_session(interaction.guild.id) as session:
                        module = (
                            session.query(Modules)
                            .filter_by(module_name="logging")
                            .first()
                        )
                        if not module:
                            module = Modules(module_name="logging", enabled=True)
                            session.add(module)

                        elif module.enabled:
                            module.enabled = False
                        else:
                            module.enabled = True
                        session.commit()

                case "automoderation":
                    with guild_db_manager.get_session(interaction.guild.id) as session:
                        module = (
                            session.query(Modules)
                            .filter_by(module_name="automoderation")
                            .first()
                        )
                        if not module:
                            module = Modules(module_name="automoderation", enabled=True)
                            session.add(module)

                        elif module.enabled:
                            module.enabled = False
                        else:
                            module.enabled = True
                        session.commit()

                case "levelling":
                    with guild_db_manager.get_session(interaction.guild.id) as session:
                        module = (
                            session.query(Modules)
                            .filter_by(module_name="levelling")
                            .first()
                        )
                        if not module:
                            module = Modules(module_name="levelling", enabled=True)
                            session.add(module)

                        elif module.enabled:
                            module.enabled = False
                        else:
                            module.enabled = True
                        session.commit()

                case "welcome":
                    with guild_db_manager.get_session(interaction.guild.id) as session:
                        module = (
                            session.query(Modules)
                            .filter_by(module_name="welcome")
                            .first()
                        )
                        if not module:
                            module = Modules(module_name="welcome", enabled=True)
                            session.add(module)

                        elif module.enabled:
                            module.enabled = False
                        else:
                            module.enabled = True
                        session.commit()

                case "suggestions":
                    with guild_db_manager.get_session(interaction.guild.id) as session:
                        module = (
                            session.query(Modules)
                            .filter_by(module_name="suggestions")
                            .first()
                        )
                        if not module:
                            module = Modules(module_name="suggestions", enabled=True)
                            session.add(module)

                        elif module.enabled:
                            module.enabled = False
                        else:
                            module.enabled = True
                        session.commit()

            view = ModulesView(interaction.guild)
            view.add_item(LanguageSelection())
            view.add_item(FinishSetup())

            message = interaction.message

            await message.edit(view=view)

        elif action == "setup" and "state" in kwargs:
            match kwargs["state"]:
                case "finish":

                    with guild_db_manager.get_session(interaction.guild.id) as session:
                        modules = session.query(Modules).all()

                        if not modules:
                            return await interaction.followup.send(
                                "No modules have been selected. Please select at least one module to finish setup.",
                                ephemeral=True,
                            )

                    with GlobalSession() as session:
                        existing_guild: Guilds = session.query(Guilds).get(
                            interaction.guild.id
                        )

                        if existing_guild:
                            existing_guild.finished_setup = True
                            session.commit()
                    await interaction.followup.send(
                        lang_manager.get_string(
                            interaction.guild.id, "setup.finish.success"
                        ),
                        ephemeral=True,
                    )

                    await interaction.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(Setup(bot))
