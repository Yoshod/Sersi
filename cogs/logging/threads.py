import nextcord
from nextcord.ext import commands

from utils.base import SersiEmbed, get_discord_timestamp
from utils.config import Configuration


class Threads(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_thread_create(self, thread: nextcord.Thread):
        log: nextcord.AuditLogEntry = (
            await thread.guild.audit_logs(
                limit=1, action=nextcord.AuditLogAction.thread_create
            ).flatten()
        )[0]

        await thread.guild.get_channel(self.config.channels.channel_logs).send(
            embed=SersiEmbed(
                description="A Thread was created",
                fields={
                    "Name": f"{thread.mention} {thread.name} (`{thread.id}`)",
                    "Created At": get_discord_timestamp(thread.created_at),
                    "Archived": thread.archived,
                    "Locked": thread.locked,
                    "Auto Archive Duration": f"{thread.auto_archive_duration} minutes",
                },
                footer="Sersi Thread Logs",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )

    @commands.Cog.listener()
    async def on_thread_delete(self, thread: nextcord.Thread):
        log: nextcord.AuditLogEntry = (
            await thread.guild.audit_logs(
                limit=1, action=nextcord.AuditLogAction.thread_delete
            ).flatten()
        )[0]

        await thread.guild.get_channel(self.config.channels.channel_logs).send(
            embed=SersiEmbed(
                description="A Thread was deleted",
                fields={
                    "Name": f"{thread.name} (`{thread.id}`)",
                    "Created At": get_discord_timestamp(thread.created_at),
                    "Archived": thread.archived,
                    "Locked": thread.locked,
                    "Auto Archive Duration": f"{thread.auto_archive_duration} minutes",
                },
                footer="Sersi Thread Logs",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )

    @commands.Cog.listener()
    async def on_thread_update(self, before: nextcord.Thread, after: nextcord.Thread):
        log: nextcord.AuditLogEntry = (
            await after.guild.audit_logs(
                limit=1, action=nextcord.AuditLogAction.thread_update
            ).flatten()
        )[0]
        before_values: str = ""
        for attribute, value in log.before:
            before_values += f"{attribute}: {value}\n"
        after_values: str = ""
        for attribute, value in log.after:
            after_values += f"{attribute}: {value}\n"

        await after.guild.get_channel(self.config.channels.channel_logs).send(
            embed=SersiEmbed(
                description="A Thread was updated",
                fields={
                    "Name": f"{after.mention} {after.name} (`{after.id}`)",
                    "Before": before_values,
                    "After": after_values,
                },
                footer="Sersi Thread Logs",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )


def setup(bot, **kwargs):
    bot.add_cog(Threads(bot, kwargs["config"]))
