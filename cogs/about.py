import nextcord

from nextcord.ext import commands

from configuration.configuration import Configuration


class About(commands.Cog, name="About", description="Information about the bot, its authors and where its source can be found."):
    def __init__(self, config: Configuration, data_folder: str):
        author_file  = open(f"{data_folder}/{config.author_list}", "r")
        self.authors = author_file.read()

        author_file.close()

    @commands.command(brief="Displays information regarding the bot itself.", help="Shows information regarding the bot, its authors and where to find its source.")
    async def about(self, context: commands.Context):
        about: nextcord.Embed = nextcord.Embed(
            title="About Sersi",
            description="Sersi is the custom moderation help bot for Adam Something Central.",
            color=nextcord.Color.from_rgb(237, 91, 6))

        about.add_field(name="Version:",     value="**4.0.0**",                                                inline=True)
        about.add_field(name="Source code:", value="**[GitHub repository](https://github.com/Yoshod/Sersi)**", inline=True)
        about.add_field(name="Authors:",     value=self.authors,                                               inline=False)

        await context.send(embed=about)


def setup(bot, **kwargs):
    bot.add_cog(About(kwargs["config"], kwargs["data_folder"]))
