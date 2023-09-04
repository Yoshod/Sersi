import nextcord
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class Edits(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        if before.guild is None:
            return
        elif (
            before.content == ""
            or after.content == ""
            or before.content == after.content
        ):
            return

        if before.pinned is False and after.pinned is True:
            pin_log: nextcord.AuditLogEntry = (
                await after.guild.audit_logs(
                    limit=1, action=nextcord.AuditLogAction.message_pin
                ).flatten()
            )[0]

            if not pin_log.extra.message_id == after.id:
                return

            await before.guild.get_channel(self.config.channels.edited_messages).send(
                embed=SersiEmbed(
                    description="A message has been pinned",
                    fields={
                        "Channel": f"{before.channel.mention} ({before.channel.id})",
                        "Link": after.jump_url,
                        "IDs": f"```ini\nMessage = {after.id}```",
                    },
                    footer="Sersi Pin Logging",
                ).set_author(
                    name=pin_log.user, icon_url=pin_log.user.display_avatar.url
                )
            )
        elif before.pinned is True and after.pinned is False:
            unpin_log: nextcord.AuditLogEntry = (
                await after.guild.audit_logs(
                    limit=1, action=nextcord.AuditLogAction.message_unpin
                ).flatten()
            )[0]

            if not unpin_log.extra.message_id == after.id:
                return

            await before.guild.get_channel(self.config.channels.edited_messages).send(
                embed=SersiEmbed(
                    description="A message has been unpinned",
                    fields={
                        "Channel": f"{before.channel.mention} ({before.channel.id})",
                        "Link": after.jump_url,
                        "IDs": f"```ini\nMessage = {after.id}```",
                    },
                    footer="Sersi Pin Logging",
                ).set_author(
                    name=unpin_log.user, icon_url=unpin_log.user.display_avatar.url
                )
            )
        else:
            await before.guild.get_channel(self.config.channels.edited_messages).send(
                embed=SersiEmbed(
                    description="A message has been edited",
                    fields={
                        "Channel": f"{before.channel.mention} ({before.channel.id})",
                        "Before": before.content,
                        "After": after.content,
                        "Link": after.jump_url,
                        "IDs": f"```ini\nMessage = {after.id}```",
                    },
                    footer="Sersi Edit Logging",
                ).set_author(
                    name=before.author, icon_url=before.author.display_avatar.url
                )
            )


def setup(bot, **kwargs):
    bot.add_cog(Edits(bot, kwargs["config"]))
