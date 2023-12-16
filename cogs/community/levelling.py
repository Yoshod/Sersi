import math
from datetime import datetime, timedelta
from enum import Enum

import nextcord
from nextcord.ext import commands, tasks

from utils.base import ignored_message
from utils.config import Configuration
from utils.sersi_embed import SersiEmbed


class XPType(Enum):
    MESSAGE = "message"
    VOICE = "voice chat"


class Levelling(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        self.last_mesage: dict[tuple(int, int), int] = {}
        self.xp_earned: dict[int, int] = {}

        if self.bot.is_ready():
            self.daily_xp_report.start()
            self.voice_xp.start()
    
    def cog_unload(self):
        self.daily_xp_report.cancel()
        self.voice_xp.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.daily_xp_report.start()
        self.voice_xp.start()

    async def earn_xp(self, member: nextcord.Member, amount: int, type: XPType):
        if amount <= 0:
            return

        self.xp_earned[member.id] = self.xp_earned.get(member.id, 0) + amount

        print(f"{member.name} earned {amount} XP for {type.value}.")

    @tasks.loop(hours=24)
    async def daily_xp_report(self):
        # wait until midnight
        await nextcord.utils.sleep_until(
            datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            + timedelta(days=1)
        )

        guild = self.bot.get_guild(self.config.guilds.main)

        total = 0
        description = ""
        for member_id, xp in sorted(
            self.xp_earned.items(), key=lambda x: x[1], reverse=True
        ):
            member = guild.get_member(member_id)
            if member is None:
                continue

            if len(description) + len(member.mention) + 6 < 4000:
                description += f"{member.mention}: {xp:4d}\n"

            total += xp

        alert_channel = guild.get_channel(self.config.channels.alert)
        if alert_channel is None:
            return

        embed = SersiEmbed(
            title="Daily XP Report",
            description=description,
            fields={"Total XP Earned": total},
        )
        await alert_channel.send(embed=embed)

        self.xp_earned = {}

    @tasks.loop(minutes=1)
    async def voice_xp(self):
        guild = self.bot.get_guild(self.config.guilds.main)

        for member in guild.members:
            if (
                member.voice is None
                or member.voice.afk
                or member.voice.self_deaf
                or member.voice.mute
            ):
                continue

            xp = len(member.voice.channel.members)

            await self.earn_xp(member, xp, XPType.VOICE)

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
            return

        if message.edited_at:
            return

        xp = min(math.floor(math.sqrt(len(message.content) * 3 / 5)), 30)

        if (
            message.author.id,
            message.channel.id,
        ) not in self.last_mesage or message.created_at.timestamp() - self.last_mesage[
            (message.author.id, message.channel.id)
        ] > 60:
            xp += 5

        self.last_mesage[
            (message.author.id, message.channel.id)
        ] = message.created_at.timestamp()

        await self.earn_xp(message.author, xp, XPType.MESSAGE)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Levelling(bot, kwargs["config"]))
