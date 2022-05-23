import nextcord
from nextcord.ext import commands

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog is ready")
    
    # command
    @commands.command()
    async def cog(self, ctx):
        await ctx.send("Cog command test")

def setup(bot):
    bot.add_cog(Example(bot))