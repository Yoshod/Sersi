import nextcord
from nextcord.ext import commands
import io
from chat_exporter import export
from configutils import Configuration
from permutils import permcheck, is_dark_mod


class Archive(commands.Cog):

    def __init__(self, bot, config: Configuration):
        self.sersisuccess = self.config.emotes.success
        self.sersifail = self.config.emotes.fail
        self.bot = bot
        self.config = config

    @commands.command()
    async def archive(self, ctx, logged_channel: nextcord.TextChannel, output_channel: nextcord.TextChannel):
        """Archive a channel."""

        if not await permcheck(ctx, is_dark_mod):
            return

        transcript = await export(logged_channel, military_time=True)
        if transcript is None:
            await output_channel.send(f"{self.sersifail} Failed to Generate Transcript!")

        else:
            transcript_file = nextcord.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-{logged_channel.name}.html",
            )

            log_embed = nextcord.Embed(
                title=f"Channel {logged_channel.name} archived",
                description=f"The channel {logged_channel.name} has been archived.",
                color=nextcord.Color.from_rgb(237, 91, 6))

            await output_channel.send(embed=log_embed, file=transcript_file)


def setup(bot, **kwargs):
    bot.add_cog(Archive(bot, kwargs["config"]))
