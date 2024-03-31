import math
from enum import Enum
from dataclasses import dataclass, field
from functools import cache

import nextcord
from nextcord.ext import commands, tasks
import requests

from utils.base import ignored_message, get_member_level
from utils.config import Configuration
from utils.database import db_session, MemberLevel
from utils.perms import permcheck, is_sersi_contributor

import discordTokens


class XPType(Enum):
    MESSAGE = "message"
    VOICE = "voice chat"


@dataclass
class MemberReport:
    member: nextcord.Member
    level: int
    xp: int

    last_message: dict[int, int] = field(default_factory=dict)
    updated: bool = False


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

        self.session = db_session()

        if self.bot.is_ready():
            self.voice_xp.start()

    def cog_unload(self):
        self.voice_xp.cancel()
        self.session.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        self.voice_xp.start()

    async def earn_xp(self, member: nextcord.Member, amount: int, type: XPType):
        if amount <= 0:
            return

        if member.id not in self.reports:
            member_level = (
                self.session.query(MemberLevel).filter_by(member=member.id).first()
            )
            if member_level is None:
                member_level = MemberLevel(
                    member=member.id,
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
        self.reports[member.id].updated = True

        if (
            xp_needed_to_next_level(self.reports[member.id].level)
            <= self.reports[member.id].xp
        ):
            self.reports[member.id].level += 1
            self.reports[member.id].xp -= xp_needed_to_next_level(
                self.reports[member.id].level - 1
            )

            await member.remove_roles(
                *list(
                    filter(
                        lambda role: role.id in self.config.level_roles.values(),
                        member.roles,
                    )
                )
            )
            await member.add_roles(
                member.guild.get_role(
                    self.config.level_roles[self.reports[member.id].level]
                )
            )

            self.session.query(MemberLevel).filter_by(member=member.id).update(
                {
                    "level": self.reports[member.id].level,
                    "xp": self.reports[member.id].xp,
                }
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

        for member_id, report in self.reports.items():
            if not report.updated:
                continue

            self.session.query(MemberLevel).filter_by(member=member_id).update(
                {
                    "level": report.level,
                    "xp": report.xp,
                }
            )

        self.session.commit()
        self.session.close()
        self.session = db_session()

    @nextcord.slash_command(
        description="get user experience report from Tatsu",
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        dm_permission=False,
    )
    async def get_tatsu_member_xp(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        await interaction.response.defer()

        response = requests.get(
            f"https://api.tatsu.gg/v1/guilds/856262303795380224/rankings/members/{member.id}/all",
            headers={"Authorization": discordTokens.getTatsuApiKey()},
        )

        if response.status_code != 200:
            await interaction.followup.send(
                "An error occurred while fetching data from Tatsu API", ephemeral=True
            )
            return

        data = response.json()
        await interaction.followup.send(
            f"{member.mention} has {data['score']} xp in Tatsu and is rank {data['rank']}",
        )

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
