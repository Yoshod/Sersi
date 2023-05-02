import datetime
import io

import nextcord
from nextcord.ext import commands
import chat_exporter

from utils.baseutils import SersiEmbed, get_discord_timestamp
from utils.configutils import Configuration


class Deletions(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message_delete(self, message: nextcord.Message):
        if message.guild is None:
            return
        deleted_messages: nextcord.TextChannel = message.guild.get_channel(
            self.config.channels.deleted_messages
        )
        deleted_images: nextcord.TextChannel = message.guild.get_channel(
            self.config.channels.deleted_images
        )

        message_has_images: bool = False

        entries = await message.guild.audit_logs(
            action=nextcord.AuditLogAction.message_delete, limit=1
        ).flatten()

        log: nextcord.AuditLogEntry = entries[0]

        if log is None:
            return

        if message.author != log.target:
            self_delete: bool = True
        else:
            self_delete: bool = False

        if not self_delete:
            logging_embed: nextcord.Embed = SersiEmbed(
                description="A message has been deleted",
                fields={
                    "Message Content": message.content,
                    "Message Created": get_discord_timestamp(message.created_at),
                    "Message Deleted": get_discord_timestamp(
                        datetime.datetime.now(datetime.timezone.utc)
                    ),
                    "Deleted By": f"{log.user.mention} ({log.user.id})",
                    "IDs": f"```ini\nAuthor = {message.author.id}\nPerpetrator = {log.user.id}```",
                },
                footer="Sersi Deletion Logging",
            )
        else:
            logging_embed: nextcord.Embed = SersiEmbed(
                description="A message has been deleted",
                fields={
                    "Message Content": message.content,
                    "Message Created": get_discord_timestamp(message.created_at),
                    "Message Deleted": get_discord_timestamp(
                        datetime.datetime.now(datetime.timezone.utc)
                    ),
                    "IDs": f"```ini\nAuthor = {message.author.id}```",
                },
                footer="Sersi Deletion Logging",
                url="http://217.160.153.216/",
            )
        logging_embed.set_author(
            name=message.author, icon_url=message.author.display_avatar.url
        )

        further_images: list[nextcord.Embed] = []
        for attachment in message.attachments:
            logging_embed.add_field(
                name=f"Attachment {attachment.content_type}",
                value=attachment.url,
                inline=False,
            )
            if "image" in attachment.content_type and not logging_embed.image:
                message_has_images = True
                logging_embed.set_image(attachment.url)
            elif "image" in attachment.content_type:
                further_images.append(
                    nextcord.Embed(url="http://217.160.153.216/").set_image(
                        attachment.url
                    )
                )

        await deleted_messages.send(embeds=[logging_embed, *further_images])
        if message_has_images:
            await deleted_images.send(embeds=[logging_embed, *further_images])

    @commands.Cog.listener()
    async def on_bulk_message_delete(self, messages: list[nextcord.Message]):
        log: nextcord.AuditLogEntry = (
            await messages[0]
            .guild.audit_logs(
                action=nextcord.AuditLogAction.message_bulk_delete, limit=1
            )
            .flatten()
        )[0]

        await messages[0].guild.get_channel(self.config.channels.deleted_messages).send(
            embed=SersiEmbed(
                description="Bulk Message deletion",
                fields={
                    "Channel": messages[0].channel.mention,
                    "Message Count": len(messages),
                },
                footer="Sersi Deletion Logging",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url),
            file=nextcord.File(
                io.BytesIO(
                    (
                        await chat_exporter.raw_export(
                            channel=messages[0].channel,
                            messages=messages[::-1],
                            military_time=True,
                        )
                    ).encode()
                ),
                filename=f"bulk-{log.created_at.strftime('%Y-%m-%d_%H_%M_%Z')}.html",
            ),
        )


def setup(bot, **kwargs):
    bot.add_cog(Deletions(bot, kwargs["config"]))
