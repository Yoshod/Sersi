import nextcord
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class GuildChanges(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_guild_emojis_update(
        self,
        guild: nextcord.Guild,
        before: tuple[nextcord.Emoji],
        after: tuple[nextcord.Emoji],
    ):
        before_list: list[nextcord.Emoji] = list(before)
        after_list: list[nextcord.Emoji] = list(after)
        for before_emoji in before:
            if before_emoji.name in [after_emoji.name for after_emoji in after]:
                after_list.remove(before_emoji)
                before_list.remove(before_emoji)
                # the emoji has not changed

        # removal case:
        if not after_list:

            log: nextcord.AuditLogEntry = (
                await guild.audit_logs(
                    action=nextcord.AuditLogAction.emoji_delete, limit=1
                ).flatten()
            )[0]
            emoji: nextcord.Emoji = before_list[0]

            if not log.target.id == emoji.id:
                return

            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild emoji was removed",
                    fields={
                        "Removed Emote": f"Name: {emoji.name}\nManaged: {emoji.managed}\nAnimated: {emoji.animated}",
                        "Emote Removed by:": f"{log.user.mention} ({log.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_thumbnail(emoji.url)
                .set_author(name=log.user, icon_url=log.user.display_avatar.url)
                .add_id_field({"Emoji": emoji.id, "User": log.user.id})
            )
        # adding case:
        elif not before_list:
            emoji: nextcord.Emoji = await guild.fetch_emoji(after_list[0].id)
            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild emoji was added",
                    fields={
                        "Added Emote": f"Name: {emoji.name}\nManaged: {emoji.managed}\nAnimated: {emoji.animated}",
                        "User": f"{emoji.user.mention} ({emoji.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_thumbnail(emoji.url)
                .set_author(name=emoji.user, icon_url=emoji.user.display_avatar.url)
                .add_id_field({"Emoji": emoji.id, "User": emoji.user.id})
            )
        # edit moment:
        else:
            after_emoji: nextcord.Emoji = after_list[0]
            before_emoji: nextcord.Emoji = before_list[0]
            emoji: nextcord.Emoji = await guild.fetch_emoji(after_list[0].id)

            log: nextcord.AuditLogEntry = (
                await guild.audit_logs(
                    action=nextcord.AuditLogAction.emoji_update, limit=1
                ).flatten()
            )[0]

            if not log.target.id == emoji.id:
                return

            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild emoji was changed",
                    fields={
                        "Before": f"Name: {before_emoji.name}\nManaged: {before_emoji.managed}\nAnimated: {before_emoji.animated}",
                        "After": f"Name: {after_emoji.name}\nManaged: {after_emoji.managed}\nAnimated: {after_emoji.animated}",
                        "Added By": f"{emoji.user.mention} ({emoji.user.id})",
                        "Changed By": f"{log.user.mention} ({log.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_thumbnail(after_emoji.url)
                .set_author(name=log.user, icon_url=log.user.display_avatar.url)
                .add_id_field({"Emoji": emoji.id, "User": log.user.id})
            )

    async def on_guild_stickers_update(
        self,
        guild: nextcord.Guild,
        before: tuple[nextcord.GuildSticker],
        after: tuple[nextcord.GuildSticker],
    ):
        before_list: list[nextcord.GuildSticker] = list(before)
        after_list: list[nextcord.GuildSticker] = list(after)
        for before_emoji in before:
            if before_emoji.name in [after_emoji.name for after_emoji in after]:
                after_list.remove(before_emoji)
                before_list.remove(before_emoji)

        # removal case:
        if not after_list:

            log: nextcord.AuditLogEntry = (
                await guild.audit_logs(
                    action=nextcord.AuditLogAction.sticker_delete, limit=1
                ).flatten()
            )[0]
            sticker: nextcord.GuildSticker = before_list[0]

            if not log.target.id == sticker.id:
                return

            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild sticker was removed",
                    fields={
                        "Removed Sticker": f"Name: {sticker.name}\nDescription: {sticker.description}",
                        "Sticker Removed by:": f"{log.user.mention} ({log.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_image(sticker.url)
                .set_author(name=log.user, icon_url=log.user.display_avatar.url)
                .add_id_field({"Sticker": sticker.id, "User": log.user.id})
            )
        # adding case:
        elif not before_list:
            sticker: nextcord.GuildSticker = await guild.fetch_sticker(after_list[0].id)
            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild emoji was added",
                    fields={
                        "Added Emote": f"Name: {sticker.name}\nDescription: {sticker.description}\nEmoji: {sticker.emoji}",
                        "User": f"{sticker.user.mention} ({sticker.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_thumbnail(sticker.url)
                .set_author(name=sticker.user, icon_url=sticker.user.display_avatar.url)
                .add_id_field({"Emoji": sticker.id, "User": sticker.user.id})
            )
        # edit moment:
        else:
            after_sticker: nextcord.GuildSticker = after_list[0]
            before_emoji: nextcord.GuildSticker = before_list[0]
            sticker: nextcord.GuildSticker = await guild.fetch_sticker(after_list[0].id)

            log: nextcord.AuditLogEntry = (
                await guild.audit_logs(
                    action=nextcord.AuditLogAction.emoji_update, limit=1
                ).flatten()
            )[0]

            if not log.target.id == sticker.id:
                return

            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild emoji was changed",
                    fields={
                        "Before": f"Name: {before_emoji.name}\nDescription: {before_emoji.description}\nEmoji: {before_emoji.emoji}",
                        "After": f"Name: {after_sticker.name}\nDescription: {after_sticker.description}\nEmoji: {after_sticker.emoji}",
                        "Added By": f"{sticker.user.mention} ({sticker.user.id})",
                        "Changed By": f"{log.user.mention} ({log.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_image(sticker.url)
                .set_author(name=log.user, icon_url=log.user.display_avatar.url)
                .add_id_field({"Emoji": sticker.id, "User": log.user.id})
            )

    @commands.Cog.listener()
    async def on_guild_update(self, before: nextcord.Guild, after: nextcord.Guild):
        entries = await after.audit_logs(
            action=nextcord.AuditLogAction.guild_update, limit=1
        ).flatten()
        log: nextcord.AuditLogEntry = entries[0]

        after_values: str = ""
        for attribute, value in log.after:
            after_values = f"{after_values}\n{attribute}: {value}"

        before_values: str = ""
        for attribute, value in log.before:
            before_values = f"{before_values}\n{attribute}: {value}"

        await after.get_channel(self.config.channels.guild_logs).send(
            embed=SersiEmbed(
                description="Guild was changed",
                fields={"Before": before_values, "After": after_values},
                footer="Sersi Guild Changes",
            )
            .set_thumbnail(after.icon.url)
            .set_author(name=log.user, icon_url=log.user.display_avatar.url)
            .add_id_field({"User": log.user.id})
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(GuildChanges(bot, kwargs["config"]))
