from datetime import timezone
from nextcord import Color, ContentFilter, Embed, Emoji, Guild, GuildSticker, Member, VerificationLevel
from nextcord.ext.commands import Cog
from typing import Any

from database.database import Database
from sersi import Sersi
from utilities.time import format_time_user_display


class LoggingMember(Cog, name="Logging - Guild", description="Logging guild related events."):
    def __init__(self, bot: Sersi, database: Database):
        self.bot      = bot
        self.database = database

    def get_member_description(self, member: Member) -> str:
        return f"{member.mention}\n\nID: `{member.id}`\nAccount creation date: {member.created_at.astimezone(tz=timezone.utc)}"

    def get_guild_description(self, guild: Guild) -> str:
        content_filter_name = "Unknown"
        match guild.explicit_content_filter:
            case ContentFilter.disabled:
                content_filter_name = "Disabled"

            case ContentFilter.no_role:
                content_filter_name = "Disabled for users with roles"

            case ContentFilter.all_members:
                content_filter_name = "Enabled"

        verification_level_name = "Unknown"
        match guild.verification_level:
            case VerificationLevel.none:
                verification_level_name = "None"

            case VerificationLevel.low:
                verification_level_name = "Requires email verification"

            case VerificationLevel.medium:
                verification_level_name = "Requires email verification and an account older than 5 minutes"

            case VerificationLevel.high:
                verification_level_name = "Requires email verification, an account older than 5 minutes and being a member for 10 minutes"

            case VerificationLevel.highest:
                verification_level_name = "Requires phone verification"

        # TODO: display more information
        return f"Name: **{guild.name}**\nExplicit content filter: **{content_filter_name}**\nVerification level: **{verification_level_name}**\nAFK Channel: **{guild.afk_channel.mention if guild.afk_channel is not None else 'None'}**\nAFK timeout: **{'None' if guild.afk_timeout == 0 else format_time_user_display(guild.afk_timeout)}**"

    def get_emoji_description(self, emote: Emoji) -> str:
        output = f"Name: **{emote.name}**\nID: `{emote.id}`"
        if emote.user is not None:
            output += f"\nAuthor: **{emote.user.mention}** (ID: `{emote.user.id}`)"

        return output

    def get_sticker_description(self, sticker: GuildSticker) -> str:
        output = f"Name: **{sticker.name}**\nID: `{sticker.id}`\nBased on emoji: {sticker.emoji}"

        if sticker.description != "":
            output += "\n```\n" + sticker.description.replace("```", "'''") + "\n```"

        if sticker.user is not None:
            output += f"\nAuthor: **{sticker.user.mention}** (ID: `{sticker.user.id}`)"

        return output

    @Cog.listener()
    async def on_member_join(self, member: Member):
        channel_id = self.database.guild_get_logging_channel(member.guild.id, "member_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Member joined",
            description=self.get_member_description(member),
            color=Color.from_rgb(237, 91, 6)
        )

        if member.bot:
            embed.title = "Bot joined"

        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar.url)

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        channel_id = self.database.guild_get_logging_channel(member.guild.id, "member_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Member left",
            description=self.get_member_description(member),
            color=Color.from_rgb(237, 91, 6)
        )

        if member.bot:
            embed.title = "Bot left"

        embed.set_author(name=f"{member.name}#{member.discriminator}", icon_url=member.avatar.url)

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        channel_id = self.database.guild_get_logging_channel(after.guild.id, "member_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Member changed",
            color=Color.from_rgb(237, 91, 6)
        )

        if after.bot:
            embed.title = "Bot updated"

        embed.add_field(name="Before", value=self.get_member_description(before), inline=False)
        embed.add_field(name="After",  value=self.get_member_description(after),  inline=False)

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_guild_update(self, before: Guild, after: Guild):
        channel_id = self.database.guild_get_logging_channel(after.id, "guild_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Guild updated",
            color=Color.from_rgb(237, 91, 6)
        )

        embed.add_field(name="Before", value=self.get_guild_description(before), inline=False)
        embed.add_field(name="After",  value=self.get_guild_description(after),  inline=False)

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_guild_emojis_update(self, guild: Guild, before: list[Emoji], after: list[Emoji]):
        channel_id = self.database.guild_get_logging_channel(guild.id, "emote_sticker_log_id")
        if channel_id is None:
            return

        embed = Embed(
            color=Color.from_rgb(237, 91, 6)
        )

        removed_emotes = set(before) - set(after)
        if len(removed_emotes) != 0:
            embed.title = "Emoji removed"
            embed.description = self.get_emoji_description(removed_emotes.pop())
            await self.bot.get_channel(channel_id).send(embed=embed)
            return

        added_emotes = set(after) - set(before)
        if len(added_emotes) != 0:
            embed.title = "Emoji added"
            embed.description = self.get_emoji_description(added_emotes.pop())
            await self.bot.get_channel(channel_id).send(embed=embed)
            return

        updated_emotes = list(filter(lambda a: a.name not in after, before))
        if len(updated_emotes) != 0:
            updated_emotes_after = list(filter(lambda a: a.name not in before, after))

            embed.title = "Emoji updated"
            embed.add_field(name="Before", value=self.get_emoji_description(updated_emotes[0]), inline=False)
            embed.add_field(name="After", value=self.get_emoji_description(updated_emotes_after[0]), inline=False)

            await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_guild_stickers_update(self, guild: Guild, before: list[GuildSticker], after: list[GuildSticker]):
        channel_id = self.database.guild_get_logging_channel(guild.id, "emote_sticker_log_id")
        if channel_id is None:
            return

        embed = Embed(
            color=Color.from_rgb(237, 91, 6)
        )

        removed_stickers = set(before) - set(after)
        if len(removed_stickers) != 0:
            embed.title = "Sticker removed"
            embed.description = self.get_sticker_description(removed_stickers[0])
            await self.bot.get_channel(channel_id).send(embed=embed)

        added_stickers = set(after) - set(before)
        if len(added_stickers) != 0:
            embed.title = "Sticker added"
            embed.description = self.get_sticker_description(added_stickers[0])
            await self.bot.get_channel(channel_id).send(embed=embed)

        updated_stickers = list(filter(lambda a: a.name or a.description or a.emoji not in after, before))
        if len(updated_stickers) != 0:
            embed.title = "Sticker updated"
            embed.description = self.get_sticker_description(updated_stickers[0])
            await self.bot.get_channel(channel_id).send(embed=embed)


def setup(bot: Sersi, **kwargs: dict[Any]):
    bot.add_cog(LoggingMember(bot, kwargs["database"]))
