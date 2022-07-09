#Modal Testing
from discord import Embed
import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View

class EmbedModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Test Modal")
        self.emTitle = nextcord.ui.TextInput(label = "First Question", min_length=2, max_length=1024, required=True, placeholder="The answer doesn't matter because this is a test.")
        self.add_item(self.emTitle)

        self.emDesc = nextcord.ui.TextInput(label = "Second Question", min_length=5, max_length=4000, required=True, placeholder="The answer doesn't matter because this is a test.", style = nextcord.TextInputStyle.paragraph)
        self.add_item(self.emDesc)

class ModalTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cb_open_modal(self, interaction):
        await interaction.response.send_modal(EmbedModal())

    @commands.command()
    async def modaltest(self, ctx):
        test_embed = nextcord.Embed(
            title = "Modal Test Embed",
            description = "This embed should have a button, whereupon pressing the button a Discord modal opens."
        )
        open_modal = Button(label="Open Modal")
        open_modal.callback = self.cb_open_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)


def setup(bot):
    bot.add_cog(ModalTest(bot))