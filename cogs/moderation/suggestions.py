import nextcord
import shortuuid
from nextcord.ext import commands
from nextcord.ui import Button, View
from utils.permutils import cb_is_cet
from utils.configutils import Configuration
from utils.baseutils import SersiEmbed


class Suggestions(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Make a suggestion on Adam Something Central",
    )
    async def suggest(
        self,
        interaction: nextcord.Interaction,
        suggestion: str = nextcord.SlashOption(
            name="suggestion",
            description="The suggestion you wish to make",
            min_length=8,
            max_length=1240,
        ),
        image_suggestion: nextcord.Attachment = nextcord.SlashOption(
            name="suggestion image",
            description="This is optional. Attach any images as relevant to the suggestion.",
            required=False,
        ),
    ):
        has_image: bool = False
        if image_suggestion is not None:
            if "image" in image_suggestion.content_type:
                has_image = True

        suggestion_id = shortuuid.uuid()

        suggest_embed = SersiEmbed(
            title=f"New Suggestion By {interaction.user.display_name}",
            description=(
                "A new suggestion has been submitted for review. Please make due considerations before deciding to "
                "publish the suggestion or reject it."
            ),
            fields={
                "Suggester:": f"{interaction.user.mention} ({interaction.user.id})",
                "Suggestion:": suggestion,
            },
        )

        suggest_embed.set_footer(text=suggestion_id)
        if has_image:
            suggest_embed.set_image(image_suggestion.url)

        yes = Button(
            label="Approve",
            style=nextcord.ButtonStyle.green,
            custom_id=f"suggestion-approve:{suggestion_id}",
        )
        yes.callback = self.cb_rq_yes

        no = Button(
            label="Deny",
            style=nextcord.ButtonStyle.red,
            custom_id=f"suggestion-deny:{suggestion_id}",
        )
        no.callback = self.cb_no

        button_view = View(timeout=None)
        button_view.add_item(yes)
        button_view.add_item(no)
        button_view.interaction_check = cb_is_cet

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["suggestion-approve"]:
                # original_embed = interaction.message.embeds[0]
                pass


def setup(bot, **kwargs):
    bot.add_cog(Suggestions(bot, kwargs["config"]))
