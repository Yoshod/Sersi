import nextcord

from nextcord.ext import commands

from configuration.configuration import Configuration


class About(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        # self.bot         = bot
        # self.config      = config

        self.version_num = "3.3.0"

        author_file  = open(f"data/{config.author_list}", "r")
        self.authors = author_file.read()
        author_file.close()

    @commands.command()
    async def about(self, ctx):
        about = nextcord.Embed(
            title="About Sersi",
            description="Sersi is the custom moderation help bot for Adam Something Central.",
            color=nextcord.Color.from_rgb(237, 91, 6))

        about.add_field(name="Version:",           value=f"**{self.version_num}**",         inline=False)
        about.add_field(name="Authors:",           value=self.authors,                      inline=False)
        about.add_field(name="GitHub Repository:", value="https://github.com/Yoshod/Sersi", inline=False)

        await ctx.send(embed=about)


def setup(bot, **kwargs):
    bot.add_cog(About(bot, kwargs["config"]))
