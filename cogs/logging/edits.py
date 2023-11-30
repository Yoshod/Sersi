import datetime

import nextcord
from nextcord.ext import commands

from utils.base import ignored_message
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class Edits(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message_edit(self, before: nextcord.Message, after: nextcord.Message):
        if ignored_message(self.config, after, ignore_channels=False):
            return
    
        if not before.content or not after.content or before.content == after.content:
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
                    },
                    footer="Sersi Pin Logging",
                )
                .set_author(name=pin_log.user, icon_url=pin_log.user.display_avatar.url)
                .add_id_field({"Author": after.author.id, "Message": after.id})
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
                    },
                    footer="Sersi Pin Logging",
                )
                .set_author(
                    name=unpin_log.user, icon_url=unpin_log.user.display_avatar.url
                )
                .add_id_field({"Author": after.author.id, "Message": after.id})
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
                    },
                    footer="Sersi Edit Logging",
                )
                .set_author(
                    name=before.author, icon_url=before.author.display_avatar.url
                )
                .add_id_field({"Author": after.author.id, "Message": after.id})
            )

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload: nextcord.RawMessageUpdateEvent):
        message_created_at: datetime.datetime = nextcord.utils.snowflake_time(
            payload.message_id
        )
        if (
            datetime.datetime.now(datetime.timezone.utc) - message_created_at
        ).days < 14:
            return

        channel: nextcord.TextChannel = self.bot.get_channel(payload.channel_id)
        message: nextcord.Message = await channel.fetch_message(payload.message_id)

        await self.bot.get_channel(self.config.channels.edited_messages).send(
            embed=SersiEmbed(
                description="An old message has been edited",
                fields={
                    "Channel": f"{channel.mention} ({channel.id})",
                    "After": message.content,
                    "Link": message.jump_url,
                    "Raw Data": payload.data,
                },
                footer="Sersi Edit Logging",
            )
            .set_author(name=message.author, icon_url=message.author.display_avatar.url)
            .add_id_field({"Author": message.author.id, "Message": message.id})
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Edits(bot, kwargs["config"]))


e = {
    "type": 0,
    "tts": False,
    "timestamp": "2022-05-22T23:08:15.634000+00:00",
    "pinned": False,
    "mentions": [],
    "mention_roles": [],
    "mention_everyone": False,
    "member": {
        "roles": [
            "978678150789754890",
            "978677753945657356",
            "985984664676225074",
            "977607515560869938",
            "1021476974901870652",
            "978668838692474910",
        ],
        "premium_since": None,
        "pending": False,
        "nick": "Lady Melanie",
        "mute": False,
        "joined_at": "2022-05-21T04:04:26.877000+00:00",
        "flags": 0,
        "deaf": False,
        "communication_disabled_until": None,
        "avatar": None,
    },
    "id": "978071828599812116",
    "flags": 0,
    "embeds": [],
    "edited_timestamp": "2023-09-10T20:34:51.101942+00:00",
    "content": "love yourselves",
    "components": [],
    "channel_id": "977377171054166037",
    "author": {
        "username": "kisachi5",
        "public_flags": 4194304,
        "id": "348142492245426176",
        "global_name": "kisachi",
        "discriminator": "0",
        "avatar_decoration_data": None,
        "avatar": "a2c80ab0d27c53f318661ae4800dc585",
    },
    "attachments": [],
    "guild_id": "977377117895536640",
}
