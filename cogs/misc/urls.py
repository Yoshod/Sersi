import re
import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View

from utils.config import Configuration
from utils.database import db_session, TrackingMessages
import urllib.parse


class TrackingUrls(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        urls = re.findall(r"(https?://[^\s]+)", message.content)

        if not urls:
            return

        with db_session() as session:
            if session.query(TrackingMessages).filter_by(message_id=message.id).first():
                return

        cleaned_urls = []

        tracking_regex = r"(utm_source=|utm_medium=|utm_campaign=|gclid=|fbclid=|si=)"

        for url in urls:
            parsed_url = urllib.parse.urlparse(url)

            if parsed_url.query:
                valid_params = []
                for param in parsed_url.query.split("&"):
                    if not re.search(tracking_regex, param):
                        valid_params.append(param)

                cleaned_url = (
                    f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
                )
                if valid_params:
                    cleaned_url += f"?{'&'.join(valid_params)}"

                if cleaned_url != url:
                    cleaned_urls.append(f"<{cleaned_url}>")

        if not cleaned_urls:
            return

        with db_session() as session:
            tracking_message = TrackingMessages(message_id=message.id)
            session.add(tracking_message)
            session.commit()

        learn_more_button = Button(
            label="Learn More",
            style=nextcord.ButtonStyle.grey,
            custom_id="tracking_learn_more",
            emoji="❓",
        )

        view = View(timeout=None, auto_defer=False)
        view.add_item(learn_more_button)

        await message.reply(
            f"Potential tracking strings were detected in your message. Here are the cleaned URL(s):\n{', '.join(cleaned_urls)}",
            mention_author=False,
            view=view,
        )

        return

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return
        if not interaction.data["custom_id"].startswith("tracking_learn_more"):
            return

        await interaction.response.send_message(
            "Tracking strings are used by companies to track your activity online. They can be used to track your location, the device you are using, and other information. They are often added to the end of URLs automatically by the website itself. We have detected that the URL *may* contain a tracking string, but this could be a [false positive](<https://en.wikipedia.org/wiki/False_positives_and_false_negatives#False_positive_error>).",
            ephemeral=True,
        )

        return


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(TrackingUrls(bot, kwargs["config"]))
