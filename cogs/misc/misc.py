import nextcord
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
        description="When someone asks an if they can as something",
    )
    async def asktoask(self, interaction: nextcord.Interaction):
        await interaction.send(
            embed=SersiEmbed(
                title="Don't Ask To Ask, Just Ask",
                url="https://dontasktoask.com",
                description="Don't ask permission to ask a question, just ask the question.\nhttps://dontasktoask.com",
            ).set_thumbnail("https://dontasktoask.com/favicon.png")
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Misc(bot))
