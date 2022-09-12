import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from configutils import get_config_int, get_config
from permutils import permcheck, is_dark_mod


class BanAppealRejection(nextcord.ui.Modal):
    def __init__(self, userID: int):
        super().__init__("Adam Something Central Ban Appeal")
        self.userID = userID

        self.reason = nextcord.ui.TextInput(
            label="Reason for Ban Appeal Rejection:",
            max_length=1024,
            required=True,
            placeholder="Reason goes here.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.reason)

    async def callback(self, interaction):
        user = interaction.client.get_user(self.userID)

        updated_form = interaction.message.embeds[0]
        updated_form.add_field(name="Rejected by:", value=interaction.user.mention, inline=False)

        await interaction.message.edit(embed=updated_form, view=None)

        log_embed = nextcord.Embed(
            title="Ban Appeal Denied",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="User:", value=f"{user} ({user.name})", inline=False)
        log_embed.add_field(name="Reason:", value=self.reason.value, inline=False)

        channel = interaction.client.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

        rejected_embed = nextcord.Embed(
            title="Your Ban Appeal Was Rejected",
            colour=nextcord.Colour.from_rgb(237, 91, 6))
        rejected_embed.add_field(name="Reason:", value=self.reason.value, inline=False)
        rejected_embed.add_field(name="Wait Time:", value="You may reapply in 28 days.", inline=False)
        try:
            await user.send(embed=rejected_embed)
        except nextcord.Forbidden:
            sersifail = get_config('EMOTES', "fail")
            await interaction.response.send_message(f"{sersifail} Cannot message the user, likely left the appeals server or has closed DMs", ephemeral=True)

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

        try:
            await interaction.guild.unban(user, reason=f"{interaction.user.name} gave reason {self.reason.value}")
        except nextcord.errors.NotFound:
            sersifail = get_config('EMOTES', "fail")
            await interaction.response.send_message(f"{sersifail} Ban was not found! (This likely means the person wasn't banned in the first place)", ephemeral=True)

        updated_form = interaction.message.embeds[0]
        updated_form.add_field(name="Approved by:", value=interaction.user.mention)

        await interaction.message.edit(embed=updated_form, view=None)

        log_embed = nextcord.Embed(
            title="Ban Appeal Approved",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="User:", value=f"{user} ({user.name})", inline=False)
        log_embed.add_field(name="Reason:", value=self.reason.value, inline=False)

        channel = interaction.client.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

        unban_embed = nextcord.Embed(
            title="You Have Been Unbanned",
            colour=nextcord.Colour.from_rgb(237, 91, 6))
        unban_embed.add_field(name="Reason:", value=self.reason.value, inline=False)
        unban_embed.add_field(name="Rejoin URL:", value=get_config('INVITES', 'banappeals'), inline=False)
        try:
            await user.send(embed=unban_embed)
        except nextcord.Forbidden:
            sersifail = get_config('EMOTES', "fail")
            await interaction.response.send_message(f"{sersifail} Cannot message the user, likely left the appeals server or has closed DMs", ephemeral=True)


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
        """Run whenever the 'submit' button is pressed."""
        appellant_id = interaction.user.id

        appeal_embed = nextcord.Embed(
            title="Ban Appeal Sent",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        appeal_embed.add_field(name=self.date.label,    value=self.date.value,      inline=False)
        appeal_embed.add_field(name=self.reason.label,  value=self.reason.value,    inline=False)
        appeal_embed.add_field(name=self.believe.label, value=self.believe.value,   inline=False)
        appeal_embed.add_field(name=self.other.label,   value=self.other.value,     inline=False)

        accept_bttn = Button(custom_id=f"ban-appeal-accept:{appellant_id}", label="Accept Appeal", style=nextcord.ButtonStyle.green)
        reject_bttn = Button(custom_id=f"ban-appeal-reject:{appellant_id}", label="Reject Appeal", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)

        channel = interaction.client.get_channel(get_config_int('CHANNELS', 'banappeals'))
        await channel.send(embed=appeal_embed, view=button_view)


class BanAppeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def appeal(self, ctx):
        print(ctx.author.id)
        if ctx.author.id == 261870562798731266 or ctx.author.id == 348142492245426176:
            pass

        else:
            return

        await ctx.message.delete()

        test_embed = nextcord.Embed(
            title="Submit Appeal",
            description="Click Button below to submit your ban appeal.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        open_modal = Button(custom_id="ban-appeal-open", label="Open Form", style=nextcord.ButtonStyle.blurple)

        button_view = View(auto_defer=False)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            id_name, id_extra = interaction.data["custom_id"].split(":", 1)
        except ValueError:
            id_name = interaction.data["custom_id"]
            id_extra = None

        match id_name:
            case "ban-appeal-open":
                await interaction.response.send_modal(BanAppealForm())
            case "ban-appeal-accept":
                if await permcheck(interaction, is_dark_mod):
                    await interaction.response.send_modal(BanAppealAccept(int(id_extra)))
            case "ban-appeal-reject":
                if await permcheck(interaction, is_dark_mod):
                    await interaction.response.send_modal(BanAppealRejection(int(id_extra)))


def setup(bot):
    bot.add_cog(BanAppeals(bot))
