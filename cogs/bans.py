import nextcord
from nextcord.ext import commands, application_checks
from nextcord.ui import Button, View
from configutils import get_config_int, get_config


class BanAppealRejection(nextcord.ui.Modal):
    def __init__(self, userID: int):
        super().__init__("Adam Something Central Ban Appeal")
        self.userID = userID
        print(f"{self.userID}, {userID}")

        self.reason = nextcord.ui.TextInput(
            label="Reason for Ban Appeal Rejection:",
            max_length=1024,
            required=True,
            placeholder="Reason goes here.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.reason)

    async def callback(self, interaction):
        user = interaction.client.get_user(self.userID)
        print(f"{self.userID} is {user}")
        await user.send(f"Your Ban Appeal on Adam Something Central was **__denied__** under the reason `{self.reason.value}`.")
        await interaction.message.edit(view=None)


class BanAppealAccept(nextcord.ui.Modal):
    def __init__(self, userID: int):
        super().__init__("Adam Something Central Ban Appeal")
        self.userID = userID

        self.reason = nextcord.ui.TextInput(
            label="Reason for Ban Appeal Approval:",
            max_length=1024,
            required=True,
            placeholder="Reason goes here.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.reason)

    async def callback(self, interaction):
        user = interaction.client.get_user(self.userID)
        print(f"{self.userID} is {user}")
        await user.send(f"Your Ban Appeal on Adam Something Central was granted under the reason `{self.reason.value}`.\n\n{get_config('INVITES', 'banappeal', '')}")

        try:
            await interaction.guild.unban(user, reason=f"{interaction.user.name} gave reason {self.reason.value}")
        except nextcord.errors.NotFound:
            sersifail = get_config('EMOTES', "fail")
            await interaction.response.send_message(f"{sersifail} Ban was not found! (This likely means the person wasn't banned in the first place)", ephemeral=True)

        await interaction.message.edit(view=None)


class BanAppealForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Adam Something Central Ban Appeal")

        self.date = nextcord.ui.TextInput(
            label="Date of Ban:",
            max_length=1024,
            required=True,
            placeholder="Please enter the date you've been banned.")
        self.add_item(self.date)

        self.reason = nextcord.ui.TextInput(
            label="The Reason Given for your Ban:",
            max_length=1024,
            required=True,
            placeholder="If no reason was given, please explain in your own best words.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.reason)

        self.believe = nextcord.ui.TextInput(
            label="Why do you believe you should be unbanned:",
            max_length=1024,
            required=True,
            placeholder="Please use civil language.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.believe)

        self.other = nextcord.ui.TextInput(
            label="Is there anything else you would like to say?",
            max_length=1024,
            required=True,
            placeholder="This is a freetext field.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.other)

    async def callback(self, interaction):
        """run whenever the 'submit' button is pressed"""
        appellant_id = interaction.user.id

        appeal_embed = nextcord.Embed(
            title="Ban Appeal Sent",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        appeal_embed.add_field(name=self.date.label,    value=self.date.value,      inline=False)
        appeal_embed.add_field(name=self.reason.label,  value=self.reason.value,    inline=False)
        appeal_embed.add_field(name=self.believe.label, value=self.believe.value,   inline=False)
        appeal_embed.add_field(name=self.other.label,   value=self.other.value,     inline=False)

        async def cb_accept(interaction):
            await interaction.response.send_modal(BanAppealAccept(appellant_id))

        async def cb_reject(interaction):
            await interaction.response.send_modal(BanAppealRejection(appellant_id))

        accept_bttn = Button(label="Accept Appeal", style=nextcord.ButtonStyle.green)
        accept_bttn.callback = cb_accept

        reject_bttn = Button(label="Reject Appeal", style=nextcord.ButtonStyle.red)
        reject_bttn.callback = cb_reject

        button_view = View(timeout=None)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)

        channel = interaction.client.get_channel(get_config_int('CHANNELS', 'banappeals'))
        await channel.send(embed=appeal_embed, view=button_view)


class BanAppeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @application_checks.is_owner()
    async def appeal(self, ctx):

        await ctx.message.delete()

        async def cb_open_modal(interaction):
            await interaction.response.send_modal(BanAppealForm())

        test_embed = nextcord.Embed(
            title="Submit Appeal",
            # description="It appears you have been epically owned on ASC; or banned out of severe copeage of a single mod, who knows."
            description="Click Button below to submit your ban appeal.",
            colour=nextcord.Color.from_rgb(237, 91, 6)
        )
        open_modal = Button(label="Open Form", style=nextcord.ButtonStyle.blurple)
        open_modal.callback = cb_open_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)


def setup(bot):
    bot.add_cog(BanAppeals(bot))
