import math
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

import nextcord
from nextcord.ext import commands, tasks

from utils.base import ignored_message, get_member_level
from utils.config import Configuration
from utils.database import db_session, MemberLevel, ExperienceJournal


class XPType(Enum):
    MESSAGE = "message"
    VOICE = "voice chat"


@dataclass
class MemberReport:
    member: nextcord.Member
    level: int
    xp: int

    last_message: dict[int, int] = {}


class Levelling(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        self.reports: dict[int, MemberReport] = {}

        self.session = db_session()

        if self.bot.is_ready():
            self.voice_xp.start()

    def cog_unload(self):
        self.voice_xp.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.voice_xp.start()

    async def earn_xp(self, member: nextcord.Member, amount: int, type: XPType):
        if amount <= 0:
            return

        if member.id not in self.reports:
            member_level = (
                self.session.query(MemberLevel).filter_by(member_id=member.id).first()
            )
            if member_level is None:
                member_level = MemberLevel(
                    member_id=member.id,
                    level=get_member_level(self.config, member),
                    xp=0,
                )
                self.session.add(member_level)
                self.session.commit()
            
            self.reports[member.id] = MemberReport(
                member=member,
                level=member_level.level,
                xp=member_level.xp,
            )

        self.reports[member.id].xp += amount
        self.reports[member.id].last_message[member.guild.id] = datetime.utcnow().timestamp()

        self.session.add(
            ExperienceJournal(
                member_id=member.id,
                timestamp=datetime.utcnow(),
                amount=amount,
                type=type.value,
            )
        )

    @tasks.loop(minutes=1)
    async def voice_xp(self):
        guild = self.bot.get_guild(self.config.guilds.main)

        for channel in guild.voice_channels:
            if len(channel.members) < 2:
                continue
            for member in channel.members:
                if member.bot:
                    continue

                await self.earn_xp(member, len(channel.members), XPType.VOICE)

        self.session.commit()
        self.session.close()
        self.session = db_session()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
            return

        if message.edited_at:
            return

        xp = min(math.floor(math.sqrt(len(message.content) * 3 / 5)), 30)

        if (
            message.author.id not in self.reports
            or message.channel.id not in self.reports[message.author.id].last_message
        ):
            xp += 5

        await self.earn_xp(message.author, xp, XPType.MESSAGE)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Levelling(bot, kwargs["config"]))
