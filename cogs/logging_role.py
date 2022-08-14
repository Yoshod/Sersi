from nextcord import Color, Embed, Role
from nextcord.ext.commands import Cog
from typing import Any

from database.database import Database
from sersi import Sersi


class LoggingRole(Cog, name="Logging - Role", description="Logging role related events."):
    def __init__(self, bot: Sersi, database: Database):
        self.bot      = bot
        self.database = database

    def int_to_8_bit_hex(self, value: int) -> str:
        return "{:02x}".format(value)

    def get_role_description(self, role: Role) -> str:
        # TODO: permissions
        return f"Name: **{role.name}**\nHoisted: **{'Yes' if role.hoist else 'No'}**\nMentionable by all: **{'Yes' if role.mention else 'No'}**\nColor: **#{self.int_to_8_bit_hex(role.color.r)}{self.int_to_8_bit_hex(role.color.g)}{self.int_to_8_bit_hex(role.color.b)}**\nPosition: **{len(role.guild.roles) - role.position}**"

    @Cog.listener()
    async def on_guild_role_create(self, role: Role):
        channel_id = self.database.guild_get_logging_channel(role.guild.id, "role_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Role created",
            description=self.get_role_description(role),
            color=Color.from_rgb(237, 91, 6)
        )

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_guild_role_update(self, before: Role, after: Role):
        # NOTE: for positional changes, this'll report changes for ALL roles
        # TODO: attempt packaging role updates together and reporting them as one

        channel_id = self.database.guild_get_logging_channel(after.guild.id, "role_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Role updated",
            color=Color.from_rgb(237, 91, 6)
        )

        embed.add_field(name="Before", value=self.get_role_description(before), inline=False)
        embed.add_field(name="After",  value=self.get_role_description(after),  inline=False)

        await self.bot.get_channel(channel_id).send(embed=embed)

    @Cog.listener()
    async def on_guild_role_delete(self, role: Role):
        channel_id = self.database.guild_get_logging_channel(role.guild.id, "role_log_id")
        if channel_id is None:
            return

        embed = Embed(
            title="Role deleted",
            description=self.get_role_description(role),
            color=Color.from_rgb(237, 91, 6)
        )

        await self.bot.get_channel(channel_id).send(embed=embed)


def setup(bot: Sersi, **kwargs: dict[Any]):
    bot.add_cog(LoggingRole(bot, kwargs["database"]))
