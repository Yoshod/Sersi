from nextcord import ChannelType, Color, Embed, ForumChannel, StageChannel, TextChannel, VoiceChannel
from nextcord.abc import GuildChannel
from nextcord.ext.commands import Cog
from typing import Any

from database.database import Database
from sersi import Sersi
from utilities.text import text_embed_value_escape_codeblock
from utilities.time import format_time_user_display


class LoggingChannel(Cog, name="Logging - Channel", description="Logging channel related events."):
    def __init__(self, bot: Sersi, database: Database):
        self.bot      = bot
        self.database = database

    def get_channel_description(self, channel: GuildChannel) -> str:
        # BUG: the position is COMPLETELY wrong
        description = f"Name: **{channel.name}**\nID: `{channel.id}`\nPosition: **{channel.position}**"

        if channel.type != ChannelType.category and channel.category is not None:
            description += f"\nCategory: **{channel.category.name}** (ID: `{channel.category_id}`)"

        description += "\nType: **"
        match channel.type:
            case ChannelType.text:
                text_channel: TextChannel = channel
                description += f"Text Channel**\nNSFW: **{'Yes' if text_channel.is_nsfw() else 'No'}\n**Slowmode delay: **{'None' if text_channel.slowmode_delay == 0 else format_time_user_display(text_channel.slowmode_delay)}**\nTopic: {text_embed_value_escape_codeblock(text_channel.topic)}"

            case ChannelType.voice:
                voice_channel: VoiceChannel = channel
                description += f"Voice Channel**\nBitrate: **{int(voice_channel.bitrate / 1000)} kb/s**\nRegion: **{'Automatic' if voice_channel.rtc_region is None else voice_channel.rtc_region.name}**\nMember limit: **{'None' if voice_channel.user_limit == 0 else voice_channel.user_limit}**"

            case ChannelType.category:
                description += "Category**"

            case ChannelType.news:
                news_channel: TextChannel = channel
                description += f"News/Announcements Channel**\nNSFW: **{'Yes' if news_channel.is_nsfw() else 'No'}\nTopic: {text_embed_value_escape_codeblock(news_channel.topic)}"

            case ChannelType.stage_voice:
                stage_channel: StageChannel = channel
                description += f"Stage**\nBitrate: **{int(stage_channel.bitrate / 1000)} kb/s**\nRegion: **{'Automatic' if stage_channel.rtc_region is None else stage_channel.rtc_region.name}**"

            case ChannelType.forum:
                forum_channel: ForumChannel = channel
                description += f"Forum**\nGuidelines: {text_embed_value_escape_codeblock(forum_channel.topic)}"

            case _:
                description += "Unknown**"

        return description

    @Cog.listener()
    async def on_guild_channel_create(self, channel: GuildChannel):
        channel_id = self.database.guild_get_logging_channel(channel.guild.id, "channel_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Channel created",
            description=self.get_channel_description(channel),
            color=Color.from_rgb(237, 91, 6)
        )

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_guild_channel_update(self, before: GuildChannel, after: GuildChannel):
        channel_id = self.database.guild_get_logging_channel(after.guild.id, "channel_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Channel updated",
            color=Color.from_rgb(237, 91, 6)
        )

        embed.add_field(name="Before", value=self.get_channel_description(before), inline=False)
        embed.add_field(name="After",  value=self.get_channel_description(after),  inline=False)

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        channel_id = self.database.guild_get_logging_channel(channel.guild.id, "channel_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Channel deleted",
            description=self.get_channel_description(channel),
            color=Color.from_rgb(237, 91, 6)
        )

        await self.bot.get_channel(channel_id).send(embed=embed)


def setup(bot: Sersi, **kwargs: dict[Any]):
    bot.add_cog(LoggingChannel(bot, kwargs["database"]))
