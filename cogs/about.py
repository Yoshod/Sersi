import nextcord
from configutils import Configuration
from nextcord.ext import commands


class About(commands.Cog):

    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def about(self, ctx):
        """Display basic information about the bot."""
        about = nextcord.Embed(
            title="About Sersi",
            description="Sersi is the custom moderation help bot for Adam Something Central.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        about.add_field(name="Version:", value=self.config.bot.version, inline=False)
        about.add_field(name="Authors:", value="\n".join(self.config.bot.authors), inline=False)
        about.add_field(name="GitHub Repository:", value=self.config.bot.git_url, inline=False)
        await ctx.send(embed=about)


def setup(bot, **kwargs):
    bot.add_cog(About(bot, kwargs["config"]))
