import nextcord

from nextcord.ext import commands


class About(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.version_num = "`4.0.0`"

        with open(self.config.datafiles.author_list, "r") as file:
            self.authors = file.read()

    @commands.command()
    async def about(self, ctx):
        """Display basic information about the bot."""
        about = nextcord.Embed(
            title="About Sersi",
            description="Sersi is the custom moderation help bot for Adam Something Central.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        about.add_field(name="Version:", value=self.version_num, inline=False)
        about.add_field(name="Authors:", value=self.authors, inline=False)
        about.add_field(name="GitHub Repository:", value="https://github.com/Yoshod/Sersi", inline=False)
        await ctx.send(embed=about)


def setup(bot):
    bot.add_cog(About(bot))
