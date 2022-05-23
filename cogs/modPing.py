import nextcord
from baseutils import *

from nextcord.ext import commands
from nextcord.ui import Button, View

class ModPing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(ModPing(bot))