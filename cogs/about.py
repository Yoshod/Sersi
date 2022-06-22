import nextcord

from nextcord.ext import commands


class About(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.version_num = "`3.2.0`"

        authors = []
        with open("Files/About/authors.txt", "r") as file:
            for line in file:
                line = line.replace('\n', '')
                authors.append(line)
        self.authors_list = authors

    @commands.command()
    async def about(self, ctx):
        """Displays basic information about the bot."""

        author_string = ""
        for author in self.authors_list:
            author_string = author_string + f"{author}\n"

        about = nextcord.Embed(
            title="About Sersi",
            description="Sersi is the custom moderation help bot for Adam Something Central.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        about.add_field(name="Version:", value=self.version_num, inline=False)
        about.add_field(name="Authors:", value=author_string, inline=False)
        await ctx.send(embed=about)


def setup(bot):
    bot.add_cog(About(bot))
