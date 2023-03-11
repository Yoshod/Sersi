import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from permutils import cb_is_cet
from configutils import Configuration


class Suggestions(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def suggest(self, ctx):
        suggest_embed = nextcord.Embed(
            title=f"New Suggestion by {ctx.author.mention}",
            description="A new suggestion has been submitted, please review this properly before deciding on whether to make available for the wider server to vote upon.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        suggest_embed.add_field(
            name="Suggester", value=f"{ctx.author.mention} ({ctx.author.id})"
        )
        suggest_embed.add_field(name="Suggestion", value=ctx.message.content)

        yes = Button(label="Approve", style=nextcord.ButtonStyle.green)
        yes.callback = self.cb_rq_yes

        no = Button(label="Deny", style=nextcord.ButtonStyle.red)
        no.callback = self.cb_no

        button_view = View(timeout=None)
        button_view.add_item(yes)
        button_view.add_item(no)
        button_view.interaction_check = cb_is_cet


def setup(bot, **kwargs):
    bot.add_cog(Suggestions(bot, kwargs["config"]))
