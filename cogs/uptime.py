import datetime
import time

from nextcord.ext import commands
from baseutils import *


class Uptime(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global start_time
        start_time = time.time()

    @commands.command()
    async def uptime(self, ctx):
        """Displays Sersi's uptime"""
        sersi_uptime = str(datetime.timedelta(second=int(round(time.time() - sersi_uptime))))
        embedVar = nextcord.Embed(
            title="Moderator Ping",
            description=f"Sersi has been online for:`\n{sersi_uptime}`",
            color=nextcord.Color.from_rgb(237, 91, 6))
        await ctx.send(embed=embedVar)


def setup(bot):
    bot.add_cog(Uptime(bot))
