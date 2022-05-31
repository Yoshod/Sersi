import nextcord

from nextcord.ext import commands
from baseutils import *


class About(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.verNum = str("`3.1.4`")
        self.buildNum = str("`Build 00234`")
        self.authorsList = load_authors()

    @commands.command()
    async def about(self, ctx):
        """Displays basic information about the bot."""
        authorString = ""
        for authors in self.authorsList:
            authorString = (str(authorString) + str(authors) + str("\n"))
        embedVar = nextcord.Embed(
            title="About Sersi",
            description="Sersi is the custom moderation help bot for Adam Something Central.\n\nVersion:\n"
            + str(self.verNum)
            + str("\n\nBuild Number:\n")
            + str(self.buildNum)
            + str("\n\nAuthors:\n")
            + str(authorString),
            color=nextcord.Color.from_rgb(237, 91, 6))
        await ctx.send(embed=embedVar)


def setup(bot):
    bot.add_cog(About(bot))
