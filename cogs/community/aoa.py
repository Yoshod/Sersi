import nextcord
import random
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal
from configutils import Configuration
from permutils import is_dark_mod, permcheck, is_senior_mod, is_cet
from baseutils import SersiEmbed

from configutils import Configuration


class AdultAccessModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Over 18s Access")
        self.config = config

        self.whyjoin = nextcord.ui.TextInput(
            label="Why do you want access to the channel?",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.whyjoin)

        self.age = nextcord.ui.TextInput(
            label="How Old Are You", min_length=1, max_length=2, required=True
        )
        self.add_item(self.age)

        self.ageproof = nextcord.ui.TextInput(
            label="If required would you verify your age?",
            min_length=2,
            max_length=3,
            required=True,
        )
        self.add_item(self.ageproof)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        applicant_id = interaction.user.id

        application_embed = SersiEmbed(
            title="Over 18s Channel Application",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            fields={
                self.whyjoin.label: self.whyjoin.value,
                self.age.label: self.age.value,
                self.ageproof.label: self.ageproof.value,
            },
        )

        accept_bttn = Button(
            custom_id=f"mod-application-next-steps:{applicant_id}",
            label="Approve",
            style=nextcord.ButtonStyle.green,
        )
        reject_bttn = Button(
            custom_id=f"mod-application-reject:{applicant_id}",
            label="Reject",
            style=nextcord.ButtonStyle.red,
        )
        review_bttn = Button(
            custom_id=f"mod-application-review:{applicant_id}",
            label="Require Proof",
            style=nextcord.ButtonStyle.grey,
        )

        button_view = View(auto_defer=False)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)
        button_view.add_item(review_bttn)

        channel = interaction.client.get_channel(self.config.channels.ageverification)
        await channel.send(embed=application_embed, view=button_view)



class AdultAccess(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    async def cb_open_adult_modal(self, interaction):
        await interaction.response.send_modal(AdultAccessModal(self.config))

    @commands.command()
    async def adult_access(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        test_embed = SersiEmbed(
            title="Over 18's Channel",
            description="Press the button below to request access to the Over 18's Channel.",
        )
        open_modal = Button(
            custom_id="adult-channel-start",
            label="Request Access",
            style=nextcord.ButtonStyle.blurple,
        )
        open_modal.callback = self.cb_open_adult_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)


    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["adult-channel-start"]:
                await interaction.response.send_modal(AdultAccessModal(self.config))


def setup(bot, **kwargs):
    bot.add_cog(AdultAccess(bot, kwargs["config"]))