import nextcord
from nextcord.ext import commands
import io
from chat_exporter import export
from utils.config import Configuration
from utils.perms import permcheck, is_dark_mod
from utils.sersi_embed import SersiEmbed


class Archive(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Archive a channel.",
    )
    async def archive(
        self,
        interaction: nextcord.Interaction,
        logged_channel: nextcord.TextChannel = nextcord.SlashOption(
            description="The channel to be archived and logged"
        ),
        output_channel: nextcord.TextChannel = nextcord.SlashOption(
            description="The channel to output the log to"
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer()

        transcript = await export(logged_channel, military_time=True)
        if transcript is None:
            await interaction.send(
                f"{self.config.emotes.fail} Failed to Generate Transcript!",
                ephemeral=True,
            )

        else:
            await output_channel.send(
                embed=SersiEmbed(
                    title=f"Channel {logged_channel.name} archived",
                    description=f"The channel {logged_channel.name} has been archived.",
                ),
                file=nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{logged_channel.name}.html",
                ),
            )

            await interaction.send(
                f"{self.config.emotes.success} Transcript sent to {output_channel.mention}!",
                ephemeral=True,
            )


def setup(bot, **kwargs):
    bot.add_cog(Archive(bot, kwargs["config"]))
