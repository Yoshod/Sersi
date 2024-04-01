import math
from enum import Enum
from dataclasses import dataclass, field
from functools import cache
from datetime import datetime, timedelta
import json

import nextcord
from nextcord.ext import commands, tasks
import requests

from utils.base import ignored_message, get_member_level
from utils.config import Configuration
from utils.database import db_session, MemberLevel

import discordTokens


class XPType(Enum):
    MESSAGE = "message"
    VOICE = "voice chat"


@dataclass
class MemberReport:
    member: nextcord.Member
    level: int
    xp: int

    xp_breakdown: dict[str, int] = field(default_factory=dict)

    last_message: dict[int, int] = field(default_factory=dict)

    updated: bool = False

    xp_since_last_save: int = 0
    last_saved: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self.next_level = xp_needed_to_level(self.level + 1)


@cache
def xp_needed_to_next_level(level: int) -> int:
    return round(10 ** (level / 5) * 1000, -2 - level // 5)


@cache
def xp_needed_to_level(level: int) -> int:
    return sum(xp_needed_to_next_level(i) for i in range(level))


@cache
def xp_to_level(xp: int) -> int:
    level = 0
    while xp >= xp_needed_to_next_level(level):
        xp -= xp_needed_to_next_level(level)
        level += 1
    return level


class Levelling(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        self.reports: dict[int, MemberReport] = {}

        if self.bot.is_ready():
            self.voice_xp.start()

    def cog_unload(self):
        self.voice_xp.cancel()
        for report in self.reports.values():
            if report.xp_since_last_save:
                self.save_report(report)

    @commands.Cog.listener()
    async def on_ready(self):
        self.voice_xp.start()

    async def update_member_level(self, member: nextcord.Member, level: int):
        if level > 0 and level not in self.config.level_roles:
            await member.guild.owner.send(
                f"Level {level} does not have a role assigned in the configuration, should be given to {member.mention} `{member.id}`."
            )
            return

        await member.remove_roles(
            *list(
                filter(
                    lambda role: role.id in self.config.level_roles.values(),
                    member.roles,
                )
            )
        )
        if level == 0:
            return
        await member.add_roles(member.guild.get_role(self.config.level_roles[level]))

    async def fetch_report(self, member: nextcord.Member):
        with db_session() as session:
            member_level = (
                session.query(MemberLevel).filter_by(member=member.id).first()
            )
            if member_level is None:  # migrate from Tatsu
                response = requests.get(
                    f"https://api.tatsu.gg/v1/guilds/856262303795380224/rankings/members/{member.id}/all",
                    headers={"Authorization": discordTokens.getTatsuApiKey()},
                )
                if response.status_code != 200:
                    xp = xp_needed_to_level(get_member_level(self.config, member))
                else:
                    xp = response.json()["score"]

                member_level = MemberLevel(
                    member=member.id,
                    level=xp_to_level(xp),
                    xp=xp,
                    xp_breakdown=json.dumps(
                        {
                            "message": xp,
                            "voice chat": 0,
                            "legacy": xp,
                        }
                    ),
                )
                session.add(member_level)
                session.commit()

                await self.update_member_level(member, xp_to_level(xp))

            self.reports[member.id] = MemberReport(
                member=member,
                level=member_level.level,
                xp=member_level.xp,
                xp_breakdown=member_level.xp_dict,
                last_saved=datetime.now(),
            )

    def save_report(self, report: MemberReport):
        with db_session() as session:
            session.query(MemberLevel).filter_by(member=report.member.id).update(
                {
                    "level": report.level,
                    "xp": report.xp,
                    "xp_breakdown": json.dumps(report.xp_breakdown),
                }
            )
            session.commit()

        report.last_saved = datetime.now()
        report.xp_since_last_save = 0

    async def earn_xp(self, member: nextcord.Member, amount: int, type: XPType):
        if amount <= 0:
            return

        if member.id not in self.reports:  # get record from database
            await self.fetch_report(member)
        report = self.reports[member.id]

        report.xp += amount
        report.xp_breakdown[type.value] += amount
        report.xp_since_last_save += amount

        if report.next_level <= report.xp:
            report.level += 1
            report.next_level = xp_needed_to_next_level(report.level)
            self.save_report(report)

            await self.update_member_level(member, report.level)
            return

        if not report.xp_since_last_save:
            return

        if (
            report.last_saved + timedelta(minutes=5) <= datetime.now()
            or report.xp_since_last_save >= 100
        ):
            self.save_report(report)

    @tasks.loop(minutes=1)
    async def voice_xp(self):
        guild = self.bot.get_guild(self.config.guilds.main)

        for channel in guild.voice_channels:
            if channel.id == self.config.channels.afk_voice:
                continue
            if len(channel.members) < 2:
                continue
            for member in channel.members:
                if member.bot:
                    continue

                if len(channel.members) <= 3:
                    xp = len(channel.members) * 2 - 1
                elif len(channel.members) <= 5:
                    xp = len(channel.members) + 2
                elif len(channel.members) < 10:
                    xp = len(channel.members) // 2 + 5
                else:
                    xp = 10

                await self.earn_xp(member, xp, XPType.VOICE)

        for report in self.reports.values():
            if (
                report.xp_since_last_save
                and report.last_saved + timedelta(minutes=5) <= datetime.now()
            ):
                self.save_report(report)

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
            or message.created_at.timestamp()
            - self.reports[message.author.id].last_message[message.channel.id]
            >= 60
        ):
            xp += 5

        await self.earn_xp(message.author, xp, XPType.MESSAGE)

        self.reports[message.author.id].last_message[message.channel.id] = (
            message.created_at.timestamp()
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Levelling(bot, kwargs["config"]))
