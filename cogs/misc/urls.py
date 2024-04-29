import re
import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.database import db_session, TrackingMessages


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

        tracking_string_detected = False

        clean_urls = []

        for url in urls:
            if "?" in url and "watch?v=" not in url:
                url = url.split("?")[0]
                tracking_string_detected = True
                clean_urls.append(f"<{url}>")

        if tracking_string_detected:
            with db_session() as session:
                session.add(TrackingMessages(message_id=message.id))
                session.commit()

            await message.reply(
                f"Potential tracking strings were detected in your message. Here are the cleaned URL(s):\n{', '.join(clean_urls)}",
                mention_author=False,
            )

        return


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(TrackingUrls(bot, kwargs["config"]))
