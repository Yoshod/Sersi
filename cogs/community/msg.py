import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.perms import permcheck, is_staff


class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Sends a specified recipient a DM",
    )
    async def dm(
        self,
        interaction: nextcord.Interaction,
        recipient: nextcord.Member,
        message: str,
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        await recipient.send(message)
        await interaction.followup.send(
            f"{self.sersisuccess} Direct Message sent to {recipient}!"
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        logging = nextcord.Embed(
            title="DM Sent",
            description="A DM has been sent.",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        logging.add_field(name="Sender:", value=interaction.user.mention, inline=False)
        logging.add_field(name="Recipient:", value=recipient.mention, inline=False)
        logging.add_field(name="Message Content:", value=message, inline=False)
        await channel.send(embed=logging)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Messages(bot, kwargs["config"]))
