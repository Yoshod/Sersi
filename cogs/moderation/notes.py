import nextcord
import time
from nextcord.ext import commands

from baseutils import SersiEmbed, PageView
from noteutils import (
    create_note,
    get_note_by_id,
    fetch_notes_by_partial_id,
    create_note_embed,
    get_note_by_user,
    get_note_by_moderator,
    delete_note,
    wipe_user_notes,
)
from configutils import Configuration
from permutils import permcheck, is_mod, is_senior_mod, is_dark_mod


def format_entry(entry):
    if len(entry[3]) >= 16:
        return "`{}`... <t:{}:R>".format(entry[3][:15], entry[4])
    else:
        return "`{}` <t:{}:R>".format(entry[3], entry[4])


class Notes(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Note base command",
    )
    async def notes(self, interaction: nextcord.Interaction):
        pass

    @notes.subcommand(description="Add a note to a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        noted: nextcord.Member,
        note: str = nextcord.SlashOption(
            name="note",
            description="The thing you wish to note",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        note_id = create_note(
            self.config, noted, interaction.user, note, int(time.time())
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} The note on {noted.mention} has been successfully created."
        )

        sersi_note = get_note_by_id(self.config, note_id)

        note_embed = create_note_embed(sersi_note, interaction)

        logging_channel = interaction.guild.get_channel(self.config.channels.mod_logs)

        await logging_channel.send(embed=note_embed)

    @notes.subcommand(description="Used to get a note by its ID")
    async def by_id(
        self,
        interaction: nextcord.Interaction,
        note_id: str = nextcord.SlashOption(
            name="note_id",
            description="Note ID",
            min_length=22,
            max_length=22,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        sersi_note = get_note_by_id(self.config, note_id)

        note_embed = create_note_embed(sersi_note, interaction)

        await interaction.followup.send(embed=note_embed)

    @by_id.on_autocomplete("note_id")
    async def notes_by_id(self, interaction: nextcord.Interaction, note: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        notes = fetch_notes_by_partial_id(self.config, note)
        await interaction.response.send_autocomplete(notes)

    @notes.subcommand(description="Used to get a note by its user")
    async def by_user(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption,
        page: int = nextcord.SlashOption(
            name="page",
            description="The page you want to view",
            min_value=1,
            default=1,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        note_embed = SersiEmbed(title=f"{user.name}'s Notes")
        note_embed.set_thumbnail(user.display_avatar.url)

        view = PageView(
            config=self.config,
            base_embed=note_embed,
            fetch_function=get_note_by_user,
            author=interaction.user,
            entry_form=format_entry,
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            user_id=str(user.id),
        )

        await view.send_followup(interaction)

    @notes.subcommand(description="Used to get a note by its user")
    async def by_moderator(
        self,
        interaction: nextcord.Interaction,
        moderator: nextcord.Member = nextcord.SlashOption,
        page: int = nextcord.SlashOption(
            name="page",
            description="The page you want to view",
            min_value=1,
            default=1,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        note_embed = SersiEmbed(title=f"{moderator.name}'s Moderator Notes")
        note_embed.set_thumbnail(moderator.display_avatar.url)

        view = PageView(
            config=self.config,
            base_embed=note_embed,
            fetch_function=get_note_by_moderator,
            author=interaction.user,
            entry_form=format_entry,
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            moderator_id=str(moderator.id),
        )

        await view.send_followup(interaction)

    @notes.subcommand(description="Used to delete a note on a user")
    async def delete(
        self,
        interaction: nextcord.Interaction,
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason you are deleting the case",
            min_length=8,
            max_length=1024,
        ),
        note_id: str = nextcord.SlashOption(
            name="note_id",
            description="Note ID",
            min_length=22,
            max_length=22,
            required=False,
        ),
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="Specify a user if you wish to delete all notes on them",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return

        if note_id and user:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You cannot provide a user and case ID. Please only provide one.",
                ephemeral=True,
            )
            return

        elif not note_id and not user:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You must either provide a note ID to delete, or a user to delete all notes on.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=False)

        if user:
            if not await permcheck(interaction, is_dark_mod):
                return

            outcome = wipe_user_notes(self.config, user)

            if outcome:
                logging_embed = SersiEmbed(
                    title="Notes Wiped",
                )

                logging_embed.add_field(name="User", value=user.mention, inline=True)
                logging_embed.add_field(
                    name="Mega Administrator",
                    value=f"{interaction.user.mention}",
                    inline=True,
                )
                logging_embed.add_field(
                    name="Reason", value=f"`{reason}`", inline=False
                )

                logging_embed.set_thumbnail(user.display_avatar.url)

                logging_channel = interaction.guild.get_channel(
                    self.config.channels.logging
                )

                await logging_channel.send(embed=logging_embed)

                await interaction.followup.send(
                    f"{self.config.emotes.success} All notes on user {user.mention} successfully deleted."
                )

            else:
                logging_embed = SersiEmbed(
                    title="User Notes Deletion Attempted",
                )

                logging_embed.add_field(name="User", value=user.mention, inline=True)
                logging_embed.add_field(
                    name="Mega Administrator",
                    value=f"{interaction.user.mention}",
                    inline=True,
                )
                logging_embed.add_field(
                    name="Reason", value=f"`{reason}`", inline=False
                )

                logging_embed.set_thumbnail(user.display_avatar.url)

                logging_channel = interaction.guild.get_channel(
                    self.config.channels.logging
                )

                await logging_channel.send(embed=logging_embed)

                await interaction.followup.send(
                    f"{self.config.emotes.fail} All notes on user {user.mention} has not been deleted."
                )

        else:
            outcome = delete_note(self.config, note_id)

            if outcome:
                logging_embed = SersiEmbed(
                    title="Note Deleted",
                )

                logging_embed.add_field(
                    name="Note ID", value=f"`{note_id}`", inline=True
                )
                logging_embed.add_field(
                    name="Moderator",
                    value=f"{interaction.user.mention}",
                    inline=True,
                )
                logging_embed.add_field(
                    name="Reason", value=f"`{reason}`", inline=False
                )

                logging_embed.set_thumbnail(interaction.user.display_avatar.url)

                logging_channel = interaction.guild.get_channel(
                    self.config.channels.logging
                )

                await logging_channel.send(embed=logging_embed)

                await interaction.followup.send(
                    f"{self.config.emotes.success} Note {note_id} successfully deleted."
                )

            else:
                logging_embed = SersiEmbed(
                    title="Note Deletion Attempted",
                )

                logging_embed.add_field(
                    name="Note ID", value=f"`{note_id}`", inline=True
                )
                logging_embed.add_field(
                    name="Moderator",
                    value=f"{interaction.user.mention}",
                    inline=True,
                )
                logging_embed.add_field(
                    name="Reason", value=f"`{reason}`", inline=False
                )

                logging_embed.set_thumbnail(interaction.user.display_avatar.url)

                logging_channel = interaction.guild.get_channel(
                    self.config.channels.logging
                )

                await logging_channel.send(embed=logging_embed)

                await interaction.followup.send(
                    f"{self.config.emotes.fail} Note {note_id} has not been deleted."
                )


def setup(bot, **kwargs):
    bot.add_cog(Notes(bot, kwargs["config"]))
