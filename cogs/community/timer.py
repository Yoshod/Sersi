import asyncio
import datetime

import nextcord.ext.commands

from utils.base import get_discord_timestamp
from utils.config import Configuration


class Timer(nextcord.ext.commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
    )
    async def timer(self, interaction: nextcord.Interaction, time_minutes: int):
        await interaction.response.defer(ephemeral=False)

        timestamp: str = get_discord_timestamp(
            datetime.datetime.now() + datetime.timedelta(minutes=time_minutes),
            relative=True,
        )
        message: nextcord.WebhookMessage = await interaction.followup.send(
            f"{timestamp} left."
        )

        await asyncio.sleep(time_minutes * 60)

        await interaction.followup.send(interaction.user.mention)
        await message.delete()


def setup(bot, **kwargs):
    bot.add_cog(Timer(bot, kwargs["config"]))
