import datetime
import nextcord
from nextcord.ext import commands, tasks

from utils.config import Configuration
from utils.database import db_session, Slowmode
from utils.perms import (
    permcheck,
    is_staff,
)
from utils.sersi_embed import SersiEmbed
from utils.slowmode import fetch_all_slowmodes
from utils.views import PageView
from utils.embeds import determine_embed_type
from utils.staff import Branch, get_staff_record


class SlowmodeCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        if self.bot.is_ready():
            self.slowmode_loop.start()

    def cog_unload(self):
        self.slowmode_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.slowmode_loop.start()

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Set the slowmode for a channel.",
    )
    async def slowmode(
        self,
        interaction: nextcord.Interaction,
    ):
        pass

    @slowmode.subcommand(
        description="Set a slowmode for a channel.",
    )
    async def set(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="The channel to add slowmode to."
        ),
        duration_slowmode: int = nextcord.SlashOption(
            name="duration",
            description="The length of time slowmode",
            min_value=1,
            max_value=21600,
        ),
        timespan_slowmode: str = nextcord.SlashOption(
            name="timespan",
            description="The unit of time being used",
            choices={
                "Seconds": "s",
                "Minutes": "m",
                "Hours": "h",
                "Days": "d",
                "Weeks": "w",
            },
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason for the slowmode",
            min_length=8,
            max_length=1024,
        ),
        duration_active: int = nextcord.SlashOption(
            name="duration_active",
            description="The length of time the slowmode will be active",
            min_value=5,
            required=False,
        ),
        timespan_active: str = nextcord.SlashOption(
            name="timespan_active",
            description="The unit of time being used",
            choices={
                "Minutes": "m",
                "Hours": "h",
                "Days": "d",
                "Weeks": "w",
            },
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        match timespan_slowmode:
            case "m":
                duration_slowmode *= 60
            case "h":
                duration_slowmode *= 3600
            case "d":
                duration_slowmode *= 86400
            case "w":
                duration_slowmode *= 604800
            case _:
                pass

        if duration_slowmode > 21600:
            await interaction.followup.send(
                "The slowmode duration cannot exceed 6 hours.", ephemeral=True
            )
            return

        if duration_slowmode < 5:
            await interaction.followup.send(
                "The slowmode duration cannot be less than 5 seconds.", ephemeral=True
            )
            return

        slowmode_end = None

        if (
            not duration_active
            and timespan_active
            or duration_active
            and not timespan_active
        ):
            await interaction.followup.send(
                f"{self.config.emotes.fail }Both duration_active and timespan_active must be provided.",
                ephemeral=True,
            )
            return

        elif duration_active and timespan_active:
            match timespan_active:
                case "m":
                    duration_active *= 60
                case "h":
                    duration_active *= 3600
                case "d":
                    duration_active *= 86400
                case "w":
                    duration_active *= 604800
                case _:
                    raise ValueError("Invalid timespan_active")

            if duration_active > 1_209_600:
                await interaction.followup.send(
                    "The active duration cannot exceed 14 days.", ephemeral=True
                )
                return

            slowmode_end = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=duration_active
            )

        user_record = get_staff_record(interaction.user.id)

        with db_session() as session:
            existing_slowmode: Slowmode = (
                session.query(Slowmode).filter_by(channel=channel.id).first()
            )

            if existing_slowmode:
                if (
                    existing_slowmode.origin != user_record.branch
                    and user_record.branch != Branch.ADMIN.value
                ):
                    await interaction.followup.send(
                        f"{self.config.emotes.fail} You cannot modify slowmode set by another branch. Please contact a member of the {existing_slowmode.origin} branch or an Administrator.",
                        ephemeral=True,
                    )
                    return

                session.delete(existing_slowmode)
                session.commit()

            new_slowmode = Slowmode(
                channel=channel.id,
                slowmode=duration_slowmode,
                added_by=interaction.user.id,
                origin=(
                    Branch.CET.value
                    if user_record.branch == Branch.CET.value
                    else Branch.MOD.value
                ),
                added_reason=reason,
                scheduled_removal=slowmode_end,
            )

            session.add(new_slowmode)
            session.commit()

        await channel.edit(slowmode_delay=duration_slowmode)

        await interaction.followup.send(
            f"{self.config.emotes.success} Slowmode of {datetime.timedelta(seconds=duration_slowmode)} set for {channel.mention}.",
            ephemeral=True,
        )

        slowmode_log = SersiEmbed(
            title="Slowmode Set",
            description=f"Slowmode of {datetime.timedelta(seconds=duration_slowmode)} set for {channel.mention}.",
            fields={
                "Reason": reason,
                "Added By": interaction.user.mention,
                "Scheduled Removal": f"{nextcord.utils.format_dt(slowmode_end, 'R') if slowmode_end else 'N/A'}",
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=slowmode_log
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=slowmode_log
        )

        slowmode_alert: nextcord.Embed = await determine_embed_type(
            title="Slowmode Set",
            body=f"A slowmode of {datetime.timedelta(seconds=duration_slowmode)} has been set for {channel.mention}. It will end {nextcord.utils.format_dt(slowmode_end, 'R') if slowmode_end else 'when manually removed'}. For more information, please open a {'Moderator' if user_record.branch == Branch.MOD.value else 'Community Engagement Team'} Ticket.",
            embed_type=f"{'moderator' if user_record.branch == Branch.MOD.value else 'cet'}",
            interaction=interaction,
            config=self.config,
            media_url=None,
            fields=None,
        )

        await channel.send(embed=slowmode_alert)

    @slowmode.subcommand(
        description="Remove slowmode from a channel.",
    )
    async def remove(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="The channel to remove slowmode from."
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason for removing slowmode",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            existing_slowmode: Slowmode = (
                session.query(Slowmode).filter_by(channel=channel.id).first()
            )

            if not existing_slowmode:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} There is no slowmode set for {channel.mention}.",
                    ephemeral=True,
                )
                return

            user_record = get_staff_record(interaction.user.id)

            if (
                existing_slowmode.origin != user_record.branch
                and user_record.branch != Branch.ADMIN.value
            ):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} You cannot remove slowmode set by another branch. Please contact a member of the {existing_slowmode.origin} branch or an Administrator.",
                    ephemeral=True,
                )
                return

            session.delete(existing_slowmode)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Slowmode removed from {channel.mention}.",
            ephemeral=True,
        )

        slowmode_log = SersiEmbed(
            title="Slowmode Removed",
            description=f"Slowmode removed from {channel.mention}.",
            fields={
                "Reason": reason,
                "Removed By": interaction.user.mention,
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=slowmode_log
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=slowmode_log
        )

        slowmode_alert: nextcord.Embed = await determine_embed_type(
            title="Slowmode Removed",
            body=f"The slowmode has been removed from {channel.mention}.",
            embed_type=f"{'cet' if user_record.branch == Branch.CET.value else 'moderator'}",
            interaction=interaction,
            config=self.config,
            media_url=None,
            fields=None,
        )

        await channel.send(embed=slowmode_alert)

    @slowmode.subcommand(
        description="View the active slowmode for a channel.",
    )
    async def view(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="The channel to view slowmode for."
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            existing_slowmode: Slowmode = (
                session.query(Slowmode).filter_by(channel=channel.id).first()
            )

            if not existing_slowmode:
                slowmode = channel.slowmode_delay

                if slowmode == 0:
                    await interaction.followup.send(
                        f"{self.config.emotes.fail} There is no slowmode set for {channel.mention}.",
                        ephemeral=True,
                    )
                    return

                else:
                    await interaction.followup.send(
                        f"{self.config.emotes.fail} There is no slowmode set for {channel.mention} via Sersi, however a slowmode for the channel is set to {datetime.timedelta(seconds=slowmode)}.\n\n This slowmode has been added to Sersi's database automatically.",
                        ephemeral=True,
                    )

                    new_slowmode = Slowmode(
                        channel=channel.id,
                        slowmode=slowmode,
                        added_by=self.bot.user.id,
                        added_reason="Unknown (Slowmode not set via Sersi)",
                        origin=Branch.MOD.value,
                    )

                    session.add(new_slowmode)
                    session.commit()

                    return

            slowmode_embed = SersiEmbed(
                title="Slowmode Information",
                description=f"Slowmode of {datetime.timedelta(seconds=existing_slowmode.slowmode)} set for {channel.mention}.",
                fields={
                    "Added By": interaction.guild.get_member(
                        existing_slowmode.added_by
                    ).mention,
                    "Reason": existing_slowmode.added_reason,
                    "Origin Branch": existing_slowmode.origin,
                    "Scheduled Removal": f"{nextcord.utils.format_dt(existing_slowmode.scheduled_removal, 'R') if existing_slowmode.scheduled_removal else 'N/A'}",
                },
            )

            await interaction.followup.send(embed=slowmode_embed)

    @slowmode.subcommand(
        description="View all active slowmodes.",
    )
    async def all(
        self,
        interaction: nextcord.Interaction,
        page: int = nextcord.SlashOption(
            description="The page of slowmodes to view.",
            required=False,
            default=1,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        slowmode_embed = SersiEmbed(
            title="Active Slowmodes",
        )

        view = PageView(
            config=self.config,
            base_embed=slowmode_embed,
            fetch_function=fetch_all_slowmodes,
            author=interaction.user,
            entry_form="{entry}",
            field_title="{entries[0].list_entry_header}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
        )

        await view.send_followup(interaction)

    @tasks.loop(seconds=30)
    async def slowmode_loop(self):
        with db_session() as session:
            slowmodes = session.query(Slowmode).all()

            for slowmode in slowmodes:
                if (
                    slowmode.scheduled_removal
                    and slowmode.scheduled_removal < datetime.datetime.utcnow()
                ):
                    channel = self.bot.get_channel(slowmode.channel)

                    if not channel:
                        raise ValueError(f"Channel {slowmode.channel} not found.")

                    await channel.edit(slowmode_delay=0)

                    session.delete(slowmode)
                    session.commit()

                    slowmode_log = SersiEmbed(
                        title="Slowmode Removed",
                        description=f"Slowmode removed from {channel.mention}.",
                        fields={
                            "Reason": "Automatic Removal",
                            "Removed By": self.bot.user.mention,
                        },
                    )

                    await channel.guild.get_channel(self.config.channels.logging).send(
                        embed=slowmode_log
                    )

                    await channel.guild.get_channel(self.config.channels.mod_logs).send(
                        embed=slowmode_log
                    )

                    slowmode_alert: nextcord.Embed = await determine_embed_type(
                        title="Slowmode Removed",
                        body=f"The slowmode has been removed from {channel.mention}. It was scheduled to be removed at {nextcord.utils.format_dt(slowmode.scheduled_removal, 'R')}.",
                        embed_type=f"{'moderator' if slowmode.origin == Branch.MOD.value else 'cet'}",
                        interaction=None,
                        config=self.config,
                        media_url=None,
                        fields=None,
                    )

                    await channel.send(embed=slowmode_alert)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(SlowmodeCog(bot, kwargs["config"]))
