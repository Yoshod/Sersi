import nextcord
from nextcord.ext import commands

from utils.base import SersiEmbed


class Misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
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


def setup(bot, **kwargs):
    bot.add_cog(Misc(bot))
