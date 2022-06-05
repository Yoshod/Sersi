import nextcord
from nextcord.ext import commands
# Doesn't do anything yet, got plans for this


class Moderators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addtrialmod(self, ctx, member: nextcord.Member):
        is_blacklisted = await ctx.invoke(self.bot.get_command('checkblacklist'), member=member)
        if is_blacklisted:
            await ctx.send(f"Member {member} cannot be given Trial Mod! Reason: Is on blacklist")
            return


def setup(bot):
    bot.add_cog(Moderators(bot))
