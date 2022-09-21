import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from configutils import Configuration
from permutils import permcheck, is_dark_mod


class ToAppealRejection(nextcord.ui.Modal):
    def __init__(self, config: Configuration, userID: int):
        super().__init__("Adam Something Central Timeout Appeal")
        self.userID = userID
        self.config = config

        self.reason = nextcord.ui.TextInput(
            label="Reason for Timeout Appeal Rejection:",
            max_length=1024,
            required=True,
            placeholder="Reason goes here.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.reason)

    async def callback(self, interaction):
        user = interaction.client.get_user(self.userID)
        rejected_embed = nextcord.Embed(
            title="Your Timeout Appeal Was Rejected",
            colour=nextcord.Colour.from_rgb(237, 91, 6))
        rejected_embed.add_field(name="Reason:", value=self.reason.value, inline=False)
        await user.send(embed=rejected_embed)

        updated_form = interaction.message.embeds[0]
        updated_form.add_field(name="Rejected by:", value=interaction.user.mention, inline=False)

        await interaction.message.edit(embed=updated_form, view=None)

        log_embed = nextcord.Embed(
            title="Timeout Appeal Denied",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="User:", value=f"{user} ({user.name})", inline=False)
        log_embed.add_field(name="Reason:", value=self.reason.value, inline=False)

        guild = nextcord.Client.get_guild(self.config.guilds.main)

        channel = guild.get_channel(self.config.channels.modlogs)
        await channel.send(embed=log_embed)


class ToAppealAccept(nextcord.ui.Modal):
    def __init__(self, config: Configuration, userID: int):
        super().__init__("Adam Something Central Timeout Appeal")
        self.config = config
        self.userID = userID

        self.reason = nextcord.ui.TextInput(
            label="Reason for Timeout Appeal Approval:",
            max_length=1024,
            required=True,
            placeholder="Reason goes here.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.reason)

    async def callback(self, interaction):
        user = interaction.client.get_user(self.userID)
        timeoutappeal_embed = nextcord.Embed(
            title="Your Timeout Appeal has been accepted",
            colour=nextcord.Colour.from_rgb(237, 91, 6))
        timeoutappeal_embed.add_field(name="Reason:", value=self.reason.value, inline=False)
        await user.send(embed=timeoutappeal_embed)

        updated_form = interaction.message.embeds[0]
        updated_form.add_field(name="Approved by:", value=interaction.user.mention)

        await interaction.message.edit(embed=updated_form, view=None)

        log_embed = nextcord.Embed(
            title="Timeout Appeal Approved",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="User:", value=f"{user} ({user.name})", inline=False)
        log_embed.add_field(name="Reason:", value=self.reason.value, inline=False)

        guild = nextcord.Client.get_guild(self.config.guilds.main)

        channel = guild.get_channel(self.config.channels.modlogs)
        await channel.send(embed=log_embed)


class ToAppealForm(nextcord.ui.Modal):
    def __init__(self, config: Configuration):
        super().__init__("Adam Something Central Timeout Appeal")
        self.config = config

        self.reason = nextcord.ui.TextInput(
            label="The Reason Given for your Timeout:",
            max_length=1024,
            required=True,
            placeholder="If no reason was given, please explain in your own best words.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.reason)

        self.recourse = nextcord.ui.TextInput(
            label="What Recourse Are You Seeking:",
            max_length=1024,
            required=True,
            placeholder="This could be a reduction in timeout length, or total removal.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.recourse)

        self.believe = nextcord.ui.TextInput(
            label="Why Do You Believe You Deserve That Recourse:",
            max_length=1024,
            required=True,
            placeholder="Please be civil.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.believe)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        appellant_id = interaction.user.id

        appeal_embed = nextcord.Embed(
            title="Timeout Appeal Sent",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        appeal_embed.add_field(name=self.reason.label,   value=self.reason.value,    inline=False)
        appeal_embed.add_field(name=self.recourse.label, value=self.reason.value,    inline=False)
        appeal_embed.add_field(name=self.believe.label, value=self.believe.value,   inline=False)

        accept_bttn = Button(custom_id=f"to-appeal-accept:{appellant_id}", label="Accept Appeal", style=nextcord.ButtonStyle.green)
        reject_bttn = Button(custom_id=f"to-appeal-reject:{appellant_id}", label="Reject Appeal", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)

        guild = nextcord.Client.get_guild(self.config.guilds.main)
        member = guild.get_member(interaction.user.id)

        if member.communication_disabled_until is None:
            return

        channel = guild.get_channel(self.config.channels.timeoutappeals)
        await channel.send(embed=appeal_embed, view=button_view)


class ToAppeals(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def toappeal(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        test_embed = nextcord.Embed(
            title="Submit Appeal",
            description="If you have been timedout, press the button below to appeal the timeout.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        open_modal = Button(custom_id="to-appeal-open", label="Open Form", style=nextcord.ButtonStyle.blurple)

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
            case "to-appeal-open":
                await interaction.response.send_modal(ToAppealForm())
            case "to-appeal-accept":
                if await permcheck(interaction, is_dark_mod):
                    await interaction.response.send_modal(ToAppealAccept(int(id_extra)))
            case "to-appael-reject":
                if await permcheck(interaction, is_dark_mod):
                    await interaction.response.send_modal(ToAppealRejection(int(id_extra)))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is None and message.author != self.bot.user:
            if message.content.lower() == "timeout appeal":
                test_embed = nextcord.Embed(
                    title="Submit Appeal",
                    description="If you have been timedout, press the button below to appeal the timeout.",
                    colour=nextcord.Color.from_rgb(237, 91, 6))
            open_modal = Button(custom_id="to-appeal-open", label="Open Form", style=nextcord.ButtonStyle.blurple)

            button_view = View(auto_defer=False)
            button_view.add_item(open_modal)

            await message.author.send(embed=test_embed, view=button_view)


def setup(bot, **kwargs):
    bot.add_cog(ToAppeals(bot, kwargs["config"]))
