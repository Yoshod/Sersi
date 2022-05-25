import nextcord
from nextcord.ext import commands
# Doesn't do anything yet, got plans for this


class Moderators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(Moderators(bot))
