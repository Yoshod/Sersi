from nextcord import Color, Embed, Message, MessageFlags, RawBulkMessageDeleteEvent, RawMessageDeleteEvent, RawMessageUpdateEvent, TextChannel
from nextcord.abc import GuildChannel
from nextcord.ext.commands import Cog
from typing import Any

from database.database import Database
from sersi import Sersi


class LoggingMessage(Cog, name="Logging - Message", description="Logging message related events."):
    def __init__(self, bot: Sersi, database: Database):
        self.bot      = bot
        self.database = database

    def clean_message(self, message: Message) -> str:
        return message.clean_content.replace('```', '\'\'\'')

    @Cog.listener()
    async def on_raw_message_edit(self, payload: RawMessageUpdateEvent):
        if payload.guild_id is None:
            return

        channel_id = self.database.guild_get_logging_channel(payload.guild_id, "message_log_id")
        if channel_id is None:
            return

        if "flags" in payload.data:
            flags: MessageFlags = payload.data["flags"]
            if flags.has_thread():
                return

        channel: GuildChannel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if message.author.bot:
            return

        embed = Embed(
            title="Message edited",
            color=Color.from_rgb(237, 91, 6)
        )

        embed.description = f"User: **{message.author.mention}** (`{message.author.id}`)\nChannel: {channel.mention}"
        embed.set_author(name=f"{message.author.name}#{message.author.discriminator}", icon_url=message.author.avatar.url)

        if payload.cached_message is not None:
            embed.add_field(name="Before", value=f"```\n{self.clean_message(payload.cached_message)}\n```", inline=False)
        else:
            embed.add_field(name="Before", value="*Message uncached.*", inline=False)

        embed.add_field(name="Now", value=f"```\n{self.clean_message(message)}\n```", inline=False)

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_raw_message_delete(self, payload: RawMessageDeleteEvent):
        if payload.guild_id is None:
            return

        channel_id = self.database.guild_get_logging_channel(payload.guild_id, "message_log_id")
        if channel_id is None:
            return

        channel: TextChannel = self.bot.get_channel(payload.channel_id)

        embed = Embed(
            title="Message deleted",
            color=Color.from_rgb(237, 91, 6)
        )

        if payload.cached_message is not None:
            if payload.cached_message.author.bot:
                return

            embed.description = f"User: **{payload.cached_message.author.mention}** (`{payload.cached_message.author.id}`)\nChannel: {channel.mention}\n\nMessage:\n```\n{self.clean_message(payload.cached_message)}\n```"
            embed.set_author(name=f"{payload.cached_message.author.name}#{payload.cached_message.author.discriminator}", icon_url=payload.cached_message.author.avatar.url)
        else:
            embed.description = f"Channel: {channel.mention}\n\n*Message uncached.*"

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_raw_bulk_message_delete(self, payload: RawBulkMessageDeleteEvent):
        if payload.guild_id is None:
            return

        channel_id = self.database.guild_get_logging_channel(payload.guild_id, "message_log_id")
        if channel_id is None:
            return

        channel: TextChannel = self.bot.get_channel(payload.channel_id)

        embed = Embed(
            title="Messages deleted in bulk",
            description=f"Channel: {channel.mention}\nNumber of messages: **{len(payload.message_ids)}**",
            color=Color.from_rgb(237, 91, 6)
        )

        await self.bot.get_channel(channel_id).send(embed=embed)


def setup(bot: Sersi, **kwargs: dict[Any]):
    bot.add_cog(LoggingMessage(bot, kwargs["database"]))
