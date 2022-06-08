import nextcord

from nextcord.ext import commands
from baseutils import *


class About(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.verNum = "`3.1.5`"

        authors = []
        with open("authors.txt", "r") as file:
            for line in file:
                line = line.replace('\n', '')
                authors.append(line)
        return authors

        self.authorsList = authors

    @commands.command()
    async def about(self, ctx):
        """Displays basic information about the bot."""

        authorString = ""
        for author in self.authorsList:
            authorString = authorString + f"{author}\n"

        about = nextcord.Embed(
            title="About Sersi",
            description="Sersi is the custom moderation help bot for Adam Something Central.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        about.add_field(name="Version:", value=self.verNum, inline=False)
        about.add_field(name="Authors:", value=authorString, inline=False)
        await ctx.send(embed=about)


def setup(bot):
    bot.add_cog(About(bot))
