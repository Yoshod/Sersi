import nextcord
from nextcord.ext import commands
import io
from chat_exporter import export
from utils.config import Configuration
from utils.perms import permcheck, is_dark_mod
from utils.base import SersiEmbed


class Archive(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def archive(
        self,
        ctx,
        logged_channel: nextcord.TextChannel,
        output_channel: nextcord.TextChannel,
    ):
        """Archive a channel."""

        if not await permcheck(ctx, is_dark_mod):
            return

        transcript = await export(logged_channel, military_time=True)
        if transcript is None:
            await output_channel.send(
                f"{self.config.emotes.fail} Failed to Generate Transcript!"
            )

        else:
            transcript_file = nextcord.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-{logged_channel.name}.html",
            )

            log_embed = SersiEmbed(
                title=f"Channel {logged_channel.name} archived",
                description=f"The channel {logged_channel.name} has been archived.",
            )

            await output_channel.send(embed=log_embed, file=transcript_file)


def setup(bot, **kwargs):
    bot.add_cog(Archive(bot, kwargs["config"]))
