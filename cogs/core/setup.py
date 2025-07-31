import nextcord
from nextcord.ext import commands, application_checks

from utils.database import (
    SessionLocal,
    Guilds,
    Modules,
    Language,
    LoggingChannels,
    ModeratorRoles,
    Offences,
)
from utils.sersi_embed import SersiEmbed
from utils.base import encode_button_id, decode_button_id


# --- UI Components for Setup ---


class ModerationModuleButton(nextcord.ui.Button):
    """A button to toggle the Moderation module."""

    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Moderation",
            custom_id=encode_button_id("setup", module="moderation"),
        )


class LoggingModuleButton(nextcord.ui.Button):
    """A button to toggle the Logging module."""

    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Logging",
            custom_id=encode_button_id("setup", module="logging"),
        )


class AutomoderationModuleButton(nextcord.ui.Button):
    """A button to toggle the Automoderation module."""

    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Automoderation",
            custom_id=encode_button_id("setup", module="automoderation"),
        )


class LevellingModuleButton(nextcord.ui.Button):
    """A button to toggle the Levelling module."""

    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Levelling",
            custom_id=encode_button_id("setup", module="levelling"),
        )


class WelcomeModuleButton(nextcord.ui.Button):
    """A button to toggle the Welcome module."""

    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Welcome",
            custom_id=encode_button_id("setup", module="welcome"),
        )


class SuggestionsModuleButton(nextcord.ui.Button):
    """A button to toggle the Suggestions module."""

    def __init__(self, selected: bool = False):
        super().__init__(
            style=(
                nextcord.ButtonStyle.red if not selected else nextcord.ButtonStyle.green
            ),
            label="Suggestions",
            custom_id=encode_button_id("setup", module="suggestions"),
        )


class ModulesView(nextcord.ui.View):
    """The view that displays all the module toggle buttons."""

    def __init__(self, guild: nextcord.Guild):
        super().__init__(timeout=None)

        with SessionLocal() as session:
            # Query the database for the modules enabled for this specific guild.
            modules = session.query(Modules).filter_by(guild_id=guild.id).all()
            enabled_modules = [
                module.module_name for module in modules if module.enabled
            ]

        # Add buttons with the correct selected state.
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
    """The dropdown for selecting the bot's language."""

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
        with SessionLocal() as session:
            # Find the language setting for this specific guild.
            guild_language = (
                session.query(Language).filter_by(guild_id=interaction.guild.id).first()
            )

            # Update the setting if it exists, otherwise create a new one.
            if guild_language:
                guild_language.language = selected_language
            else:
                new_language = Language(
                    guild_id=interaction.guild.id, language=selected_language
                )
                session.add(new_language)
            session.commit()

        await interaction.response.send_message(
            f"Language has been set to {selected_language}.",
            ephemeral=True,
        )


class FinishSetup(nextcord.ui.Button):
    """The button to finalize the setup process."""

    def __init__(self):
        super().__init__(
            style=nextcord.ButtonStyle.green,
            label="Finish Setup",
            custom_id=encode_button_id("setup", state="finish"),
        )


class Setup(commands.Cog):
    """The main cog for handling the bot's setup process."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="setup",
        description="Set up the bot for your server.",
    )
    @application_checks.has_guild_permissions(administrator=True)
    async def setup(self, interaction: nextcord.Interaction):
        """Starts the initial setup process for a new server."""
        with SessionLocal() as session:
            # Check if the guild is already in the database.
            existing_guild: Guilds = session.query(Guilds).get(interaction.guild.id)

            # If setup is already finished, inform the user.
            if existing_guild and existing_guild.finished_setup:
                return await interaction.response.send_message(
                    "The bot has already been set up for this server.",
                    ephemeral=True,
                )

            # If the guild is not in the database, add it.
            if not existing_guild:
                new_guild = Guilds(guild_id=interaction.guild.id, is_testing=True)
                session.add(new_guild)
                session.commit()

        # Create the initial setup message with instructions.
        embed = SersiEmbed(
            title="Bot Setup (Module Configuration)",
            description="Welcome to the Sersi setup wizard! Firstly, select the modules from the list below that you would like to be **enabled** for your community. Then pick which language you would prefer to use. You can always change these later if you change your mind.",
        )

        # Build the view with all the UI components.
        view = ModulesView(interaction.guild)
        view.add_item(LanguageSelection())
        view.add_item(FinishSetup())

        await interaction.response.send_message(embed=embed, view=view)

    @nextcord.slash_command(
        name="dev_wipe",
        description="Wipes the bot's database for development purposes.",
        guild_ids=[977377117895536640, 1166770860787515422, 1383162647171567626],
    )
    @application_checks.is_owner()
    async def dev_wipe(self, interaction: nextcord.Interaction):
        """Wipe all rows from every table in the database."""
        with SessionLocal() as session:
            # Delete all entries from the Modules table.
            session.query(Modules).delete()
            # Delete all entries from the Language table.
            session.query(Language).delete()
            # Delete all entries from the LoggingChannels table.
            session.query(LoggingChannels).delete()
            # Delete all entries from the ModeratorRoles table.
            session.query(ModeratorRoles).delete()
            # Delete all entries from the Offences table.
            session.query(Offences).delete()
            # Delete all entries from the Guilds table.
            session.query(Guilds).delete()
            # Commit the changes to the database.
            session.commit()

        await interaction.response.send_message(
            "The bot's database has been wiped for development purposes.",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        """Listens for button clicks and dropdown selections from the setup message."""
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        if not interaction.data["custom_id"].startswith("setup"):
            return

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        # --- Logic for Module Button Clicks ---
        if action == "setup" and "module" in kwargs:
            module_name = kwargs["module"]
            with SessionLocal() as session:
                # Find the module setting for this specific guild and module name.
                module = (
                    session.query(Modules)
                    .filter_by(guild_id=interaction.guild.id, module_name=module_name)
                    .first()
                )
                # If it doesn't exist, create it as enabled.
                if not module:
                    module = Modules(
                        guild_id=interaction.guild.id,
                        module_name=module_name,
                        enabled=True,
                    )
                    session.add(module)
                # Otherwise, toggle its enabled state.
                else:
                    module.enabled = not module.enabled
                session.commit()

            # Re-create and send the view to reflect the updated button colors.
            view = ModulesView(interaction.guild)
            view.add_item(LanguageSelection())
            view.add_item(FinishSetup())
            await interaction.message.edit(view=view)

        # --- Logic for Finish Button Click ---
        elif action == "setup" and "state" in kwargs and kwargs["state"] == "finish":
            with SessionLocal() as session:
                # Check if at least one module has been enabled for this guild.
                enabled_modules = (
                    session.query(Modules)
                    .filter_by(guild_id=interaction.guild.id, enabled=True)
                    .first()
                )

                if not enabled_modules:
                    return await interaction.followup.send(
                        "No modules have been selected. Please select at least one module to finish setup.",
                        ephemeral=True,
                    )

                # Mark the setup as complete in the global guilds table.
                existing_guild: Guilds = session.query(Guilds).get(interaction.guild.id)
                if existing_guild:
                    existing_guild.finished_setup = True
                    session.commit()

            # Send a final confirmation message.
            await interaction.followup.send(
                "Setup has been completed for this server!",
                ephemeral=True,
            )
            # Delete the original setup message to clean up the channel.
            await interaction.message.delete()


def setup(bot: commands.Bot):
    """Adds the cog to the bot."""
    bot.add_cog(Setup(bot))
