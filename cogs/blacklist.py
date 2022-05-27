import nextcord

from nextcord.ext import commands
from baseutils import *


class Blacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['bl', 'bluser', 'addbl'])
    async def blacklistuser(self, ctx):
        ctx.reply("blacklistuser")
        return

    @commands.command(aliases=['lbl', 'bllist', 'listbl', 'bll'])
    async def listblacklist(self, ctx):
        ctx.reply("listblacklist")
        return

    @commands.command(aliases=['rmbl', 'removeuserfromblacklist', 'blrmuser', 'blremoveuser', ])
    async def removefromblacklist(self, ctx):
        ctx.reply("removefromblacklist")
        return


def setup(bot):
    bot.add_cog(Blacklist(bot))
