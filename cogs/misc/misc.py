from nextcord.ext import commands

from baseutils import SersiEmbed


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["dontasktoask", "justask", "ask2ask", "a2a", "ja"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def asktoask(self, ctx):
        ask_embed = SersiEmbed(
            title="Don't Ask To Ask, Just Ask",
            url="https://dontasktoask.com",
            description="Don't ask permission to ask a question, just ask the question.\nhttps://dontasktoask.com",
        )
        ask_embed.set_thumbnail("https://dontasktoask.com/favicon.png")
        await ctx.send(embed=ask_embed)


def setup(bot, **kwargs):
    bot.add_cog(Misc(bot))
