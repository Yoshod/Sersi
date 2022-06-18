import nextcord
from nextcord.ext import commands
from baseutils import *


class CrossServerTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def messagecross(self, ctx, *, args):
        if not isDarkMod(ctx.author.roles):
            await ctx.send(f"<:sersifail:979070135799279698> Insufficient permission!")
            return
        guild_name = ctx.guild.name
        guild_id = ctx.guild.id
        message = args
        package = [guild_name, guild_id, message]
        error_channel = self.bot.get_channel(987397664280817754)
        await error_channel.send(package)


def setup(bot):
    bot.add_cog(CrossServerTest(bot))
