import nextcord
from nextcord.ext import commands

from utils.base import SersiEmbed
from utils.config import Configuration


class GuildChanges(commands.Cog):
    def __init__(self, bot, config: Configuration):
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
        print(f"before: {before_list}")
        print(f"after: {after_list}")

        # removal case:
        if not after_list:
            emoji: nextcord.Emoji = await guild.fetch_emoji(before_list[0].id)
            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild emoji was removed",
                    fields={
                        "Removed Emote": f"Name: {emoji.name}\nManaged: {emoji.managed}\nAnimated: {emoji.animated}",
                        "User": f"{emoji.user.mention} ({emoji.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_thumbnail(emoji.url)
                .set_author(name=emoji.user, icon_url=emoji.user.display_avatar.url)
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
            )
        # edit moment:
        else:
            after_emoji: nextcord.Emoji = after_list[0]
            before_emoji: nextcord.Emoji = before_list[0]
            emoji: nextcord.Emoji = await guild.fetch_emoji(after_list[0].id)
            await guild.get_channel(self.config.channels.guild_logs).send(
                embed=SersiEmbed(
                    description="Guild emoji was changed",
                    fields={
                        "Before": f"Name: {before_emoji.name}\nManaged: {before_emoji.managed}\nAnimated: {before_emoji.animated}",
                        "After": f"Name: {after_emoji.name}\nManaged: {after_emoji.managed}\nAnimated: {after_emoji.animated}",
                        "User": f"{emoji.user.mention} ({emoji.user.id})",
                    },
                    footer="Sersi Guild Changes",
                )
                .set_thumbnail(after_emoji.url)
                .set_author(name=emoji.user, icon_url=emoji.user.display_avatar.url)
            )

    async def on_guild_stickers_update(
        self,
        guild: nextcord.Guild,
        before: list[nextcord.Emoji],
        after: list[nextcord.Emoji],
    ):
        ...

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
        )


def setup(bot, **kwargs):
    bot.add_cog(GuildChanges(bot, kwargs["config"]))
