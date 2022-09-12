import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from configutils import get_config_int
from permutils import permcheck, is_dark_mod


class FeedbackResponse(nextcord.ui.Modal):
    def __init__(self, userID: int):
        super().__init__("Adam Something Central Feedback Response")
        self.userID = userID

        self.response = nextcord.ui.TextInput(
            label="Response to feedback given:",
            max_length=1024,
            required=True,
            placeholder="Response goes here.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.response)

    async def callback(self, interaction):
        user = interaction.client.get_user(self.userID)
        response_embed = nextcord.Embed(
            title="Your Feedback Has Been Responded To",
            colour=nextcord.Colour.from_rgb(237, 91, 6))
        response_embed.add_field(name="Response:", value=self.response.value, inline=False)
        await user.send(embed=response_embed)


class AnonymousFeedbackForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Adam Something Central Anon Internal Feedback")

        self.feedback = nextcord.ui.TextInput(
            label="What is the matter you wish to raise:",
            max_length=1024,
            required=True,
            placeholder="This can be anything, positive or negative.")
        self.add_item(self.feedback)

        self.action = nextcord.ui.TextInput(
            label="What actions do you think should be taken:",
            max_length=1024,
            required=True,
            placeholder="If you do not have any specific ideas, please respond N/A.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.action)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        feedback_id = interaction.user.id

        appeal_embed = nextcord.Embed(
            title="Internal Feedback Received",
            description="The user giving feedback wished to remain anonymous",
            color=nextcord.Color.from_rgb(237, 91, 6))
        appeal_embed.add_field(name=self.feedback.label,    value=self.feedback.value,      inline=False)
        appeal_embed.add_field(name=self.action.label,      value=self.action.value,        inline=False)

        respond_bttn = Button(custom_id=f"internal-feedback-response:{feedback_id}", label="Give Response", style=nextcord.ButtonStyle.green)

        button_view = View(auto_defer=False)
        button_view.add_item(respond_bttn)

        channel = interaction.client.get_channel(get_config_int('CHANNELS', 'internalfeedback'))
        await channel.send(embed=appeal_embed, view=button_view)


class FeedbackForm(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Adam Something Central Internal Feedback")

        self.feedback = nextcord.ui.TextInput(
            label="What is the matter you wish to raise:",
            max_length=1024,
            required=True,
            placeholder="This can be anything, positive or negative.")
        self.add_item(self.feedback)

        self.action = nextcord.ui.TextInput(
            label="What actions do you think should be taken:",
            max_length=1024,
            required=True,
            placeholder="If you do not have any specific ideas, please respond N/A.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.action)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        user = interaction.user

        appeal_embed = nextcord.Embed(
            title="Internal Feedback Received",
            description=f"The user giving feedback was {user.mention} ({user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        appeal_embed.add_field(name=self.feedback.label,    value=self.feedback.value,      inline=False)
        appeal_embed.add_field(name=self.action.label,      value=self.action.value,        inline=False)

        respond_bttn = Button(custom_id=f"internal-feedback-response:{user.id}", label="Give Response", style=nextcord.ButtonStyle.green)

        button_view = View(auto_defer=False)
        button_view.add_item(respond_bttn)

        channel = interaction.client.get_channel(get_config_int('CHANNELS', 'internalfeedback'))
        await channel.send(embed=appeal_embed, view=button_view)


class InternalFeedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def feedbackpost(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        feedback_embed = nextcord.Embed(
            title="Submit Feedback",
            description="Select one of the buttons below to submit your feedback.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        feedback = Button(custom_id="internal-feedback", label="Give Feedback", style=nextcord.ButtonStyle.blurple)
        anon_feedback = Button(custom_id="internal-feedback-anon", label="Give Feedback Anonymously", style=nextcord.ButtonStyle.blurple)

        button_view = View(auto_defer=False)
        button_view.add_item(feedback)
        button_view.add_item(anon_feedback)

        await ctx.send(embed=feedback_embed, view=button_view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            id_name, id_extra = interaction.data["custom_id"].split(":", 1)
        except ValueError:
            id_name = interaction.data["custom_id"]
            id_extra = None

        match id_name:
            case "internal-feedback":
                await interaction.response.send_modal(FeedbackForm())
            case "internal-feedback-anon":
                await interaction.response.send_modal(AnonymousFeedbackForm())
            case "internal-feedback-response":
                if await permcheck(interaction, is_dark_mod):
                    await interaction.response.send_modal(FeedbackResponse(int(id_extra)))


def setup(bot):
    bot.add_cog(InternalFeedback(bot))
