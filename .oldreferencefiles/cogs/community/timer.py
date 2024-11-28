import asyncio
from datetime import datetime, timedelta

import nextcord
from nextcord.ext import commands

from utils.base import get_discord_timestamp
from utils.config import Configuration


class Timer(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        self.timers: dict[int, dict[int, tuple[datetime, asyncio.Task]]] = {}

    async def timer_task(self, end_time: datetime, interaction: nextcord.Interaction):
        timestamp: str = get_discord_timestamp(end_time, relative=True)
        message: nextcord.WebhookMessage = await interaction.followup.send(timestamp)

        await asyncio.sleep((end_time - datetime.now()).total_seconds())

        await message.reply(f"{interaction.user.mention} time is up!")
        self.timers[interaction.user.id].pop(interaction.id)

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def timer(self, interaction: nextcord.Interaction):
        pass

    @timer.subcommand(
        name="start",
        description="Create a timer.",
    )
    async def timer_start(self, interaction: nextcord.Interaction, time_minutes: int):
        await interaction.response.defer(ephemeral=False)

        if interaction.user.id not in self.timers:
            self.timers[interaction.user.id] = {}

        self.timers[interaction.user.id][interaction.id] = (
            timer_end := datetime.now() + timedelta(minutes=time_minutes),
            self.bot.loop.create_task(self.timer_task(timer_end, interaction)),
        )

    @timer.subcommand(
        name="cancel",
        description="Cancel a timer.",
    )
    async def timer_cancel(self, interaction: nextcord.Interaction, timer: str):
        if interaction.user.id not in self.timers:
            interaction.response.send_message("You have no active timers.")
            return

        if int(timer) not in self.timers[interaction.user.id]:
            interaction.response.send_message("Timer not found.")
            return

        self.timers[interaction.user.id][int(timer)][1].cancel()
        timer = self.timers[interaction.user.id].pop(int(timer))

        await interaction.response.send_message(
            f"Timer for {get_discord_timestamp(timer[0], relative=True)} has been cancelled."
        )

    @timer_cancel.on_autocomplete("timer")
    async def timer_cancel_autocomplete(
        self, interaction: nextcord.Interaction, timer: str
    ):
        if interaction.user.id not in self.timers:
            return

        return {
            str(end_time - datetime.now()): str(timer)
            for timer, (end_time, _) in self.timers[interaction.user.id].items()
        }


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Timer(bot, kwargs["config"]))
