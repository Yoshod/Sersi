import nextcord
from nextcord.ext import commands
from configutils import Configuration


class Suggest(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot

    @commands.command()
    async def suggest(self, ctx):
        sample_suggestion = nextcord.Embed(
            title="",
            description="",
            colour=nextcord.Color.from_rgb(237, 91, 6)
        )
        ask_embed.set_thumbnail(self.bot.user.avatar.url)
        await ctx.send(embed=ask_embed)


def setup(bot, **kwargs):
    bot.add_cog(Suggest(bot, kwargs["config"]))
