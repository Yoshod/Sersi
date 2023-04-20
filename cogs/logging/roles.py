import nextcord
from nextcord.ext import commands
from configutils import Configuration
from baseutils import SersiEmbed


class MemberRoles(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        ...
        # moved to users.py

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: nextcord.Role):
        ...

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: nextcord.Role):
        ...

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: nextcord.Role, after: nextcord.Role):
        ...


def setup(bot, **kwargs):
    bot.add_cog(MemberRoles(bot, kwargs["config"]))
