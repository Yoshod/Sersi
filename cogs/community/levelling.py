import math
from enum import Enum
from dataclasses import dataclass, field
from functools import cache
from datetime import datetime, timedelta
import json
from collections import namedtuple

import nextcord
from nextcord.ext import commands, tasks
import requests

from utils.base import ignored_message, get_member_level, get_page
from utils.config import Configuration
from utils.database import db_session, MemberLevel
from utils.dialog import confirm
from utils.perms import permcheck, is_cet, is_admin, is_cet_lead
from utils.sersi_embed import SersiEmbed
from utils.views import PageView

import discordTokens


class XPType(Enum):
    MESSAGE = "message"
    VOICE = "voice chat"
    COMMAND = "command"


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
        for xp_type in XPType:
            if xp_type.value not in self.xp_breakdown:
                self.xp_breakdown[xp_type.value] = 0

    def __setattr__(self, __name: str, __value) -> None:
        if __name == "level":
            self.next_level = xp_needed_to_level(__value + 1)
        super().__setattr__(__name, __value)


@cache
def xp_needed_to_next_level(level: int) -> int:
    return int(round(10 ** (level / 5) * 1000, -2 - level // 5))


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


XP_COMMAND_LIMITS = {
    2000: is_cet_lead,
    5000: is_admin,
}


MemberRank = namedtuple("MemberRank", ["id", "xp", "level", "rank"])


def fetch_leaderboard(
    config: Configuration, page: int, per_page: int = 10
) -> tuple[list[MemberRank], int, int]:
    with db_session() as session:
        members: MemberLevel = (
            session.query(MemberLevel).order_by(MemberLevel.xp.desc()).all()
        )

    members, pages, page = get_page(members, page, per_page)
    return (
        [
            MemberRank(id=member.member, xp=member.xp, level=member.level, rank=i + 1)
            for i, member in enumerate(members)
        ],
        pages,
        page,
    )


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
        if get_member_level(self.config, member) == level:
            return
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
                            "legacy": xp,
                        }
                    ),
                )
                session.add(member_level)
                session.commit()

            elif member_level.level != xp_to_level(member_level.xp):
                member_level.level = xp_to_level(member_level.xp)
                session.commit()

            self.reports[member.id] = MemberReport(
                member=member,
                level=member_level.level,
                xp=member_level.xp,
                xp_breakdown=member_level.xp_dict,
                last_saved=datetime.now(),
            )

        await self.update_member_level(member, self.reports[member.id].level)

    async def get_report(self, member: nextcord.Member) -> MemberReport:
        if member.id not in self.reports:
            await self.fetch_report(member)
        return self.reports[member.id]

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

        report = await self.get_report(member)

        report.xp += amount
        report.xp_breakdown[type.value] += amount
        report.xp_since_last_save += amount

        if report.next_level <= report.xp:
            report.level += 1
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

    async def lose_xp(self, member: nextcord.Member, amount: int, type: XPType):
        if amount <= 0:
            return

        report = await self.get_report(member)

        report.xp -= amount
        report.xp_breakdown[type.value] -= amount

        if report.xp < 0:
            report.xp = 0

        if report.xp < xp_needed_to_level(report.level):
            report.level -= 1

            await self.update_member_level(member, report.level)

        self.save_report(report)

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def level(self, interaction: nextcord.Interaction):
        pass

    @level.subcommand(description="View your own XP and level or someone else's.")
    async def show(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            name="member",
            description="Member to view the level of",
            required=False,
        ),
    ):
        if member is None:
            member = interaction.user
        report = await self.get_report(member)

        xp_base = xp_needed_to_level(report.level)
        xp_above_current = report.xp - xp_base
        xp_to_next = report.next_level - report.xp
        fraction = xp_above_current / xp_needed_to_next_level(report.level)

        level_role = member.guild.get_role(
            self.config.level_roles.get(report.level, None)
        )
        level_name = (
            level_role.name.replace("(", "(Level ")
            if level_role
            else "Civil Engineering Initiate (Level 0)"
        )

        embed = SersiEmbed(
            title=f"__{level_name}__",
            description=f"`{report.xp:13d} XP / {report.next_level:7d} XP`\n"
            f"`{report.level:2d}` {'█'*round(fraction*20)}{'░'*(20-round(fraction*20))} `{report.level+1:2d}`\n\n"
            f"XP needed to next level: **{xp_to_next}**",
            fields=[
                {
                    XPType(type).value.capitalize(): f"{amount} XP"
                    for type, amount in report.xp_breakdown.items()
                    if amount and type in [type.value for type in XPType]
                }
            ],
            colour=member.colour,
            thumbnail_url=member.avatar.url,
            author=member,
            footer_icon=interaction.user.avatar.url,
            footer=f"Requested by {interaction.user.display_name}",
        )
        await interaction.response.send_message(embed=embed)

    @level.subcommand(description="View the leaderboard.")
    async def leaderboard(
        self,
        interaction: nextcord.Interaction,
        page: int = nextcord.SlashOption(
            name="page",
            description="Page number",
            required=False,
            default=1,
        ),
    ):
        await interaction.response.defer()

        embed = SersiEmbed(
            title=f"{interaction.guild.name} Leaderboard",
            thumbnail_url=interaction.guild.icon.url,
            footer_icon=interaction.user.avatar.url,
        )

        view = PageView(
            config=self.config,
            base_embed=embed,
            fetch_function=fetch_leaderboard,
            author=interaction.user,
            init_page=page,
            use_description=True,
            entry_form="**{entry.rank}.** <@{entry.id}> - {entry.xp} XP - Level {entry.level}",
        )

        await view.send_followup(interaction)

    @level.subcommand(description="Give a specified amount of XP to a member.")
    async def give_xp(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        amount: int = nextcord.SlashOption(
            name="amount",
            description="Amount of XP to give",
            min_value=100,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for giving XP",
        ),
    ):
        if not await permcheck(interaction, is_cet):
            return

        for limit, check in XP_COMMAND_LIMITS.items():
            if amount > limit and not check(interaction.user):
                await interaction.response.send_message(
                    f"You can only give up to {limit} XP.", ephemeral=True
                )
                return

        await interaction.response.defer()

        if amount >= 1000:
            if not await confirm(
                interaction,
                title="Giving a large amount of XP",
                description="Are you sure you want to give this much XP?",
                embed_fields={
                    "Amount:": amount,
                    "Recipient:": member.mention,
                },
            ):
                return

        await self.earn_xp(member, amount, XPType.COMMAND)
        await interaction.followup.send(
            f"{interaction.user.mention} gave **{amount}** XP to {member.mention} for *{reason}*!"
        )

        # logging
        log_embed = SersiEmbed(
            title="XP Given",
            colour=nextcord.Colour.green(),
            fields={
                "Giver:": interaction.user.mention,
                "Recipient:": member.mention,
                "Amount:": amount,
                "Reason:": reason,
            },
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )
        await interaction.guild.get_channel(self.config.channels.user_chanes).send(
            embed=log_embed
        )
        await interaction.guild.get_channel(self.config.channels.alert).send(
            embed=log_embed
        )

    @level.subcommand(description="Remove a specified amount of XP from a member.")
    async def remove_xp(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        amount: int = nextcord.SlashOption(
            name="amount",
            description="Amount of XP to remove",
            min_value=100,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for removing XP",
        ),
        hidden: bool = nextcord.SlashOption(
            name="hidden",
            description="Whether to hide the response from other users.",
            required=False,
            choices={
                "True": True,
                "False": False,
            },
        ),
    ):
        if not await permcheck(interaction, is_cet):
            return

        for limit, check in XP_COMMAND_LIMITS.items():
            if amount > limit and not check(interaction.user):
                await interaction.response.send_message(
                    f"You can only remove up to {limit} XP.", ephemeral=True
                )
                return

        await interaction.response.defer(ephemeral=hidden)

        if amount >= 1000:
            if not await confirm(
                interaction,
                title="Removing a large amount of XP",
                description="Are you sure you want to remove this much XP?",
                embed_fields={
                    "Amount:": amount,
                    "Recipient:": member.mention,
                },
                ephemeral=hidden,
            ):
                return

        await self.lose_xp(member, amount, XPType.COMMAND)
        await interaction.followup.send(
            f"{interaction.user.mention} removed **{amount}** XP from {member.mention} for *{reason}*!",
            ephemeral=hidden,
        )

        # logging
        log_embed = SersiEmbed(
            title="XP Removed",
            colour=nextcord.Colour.red(),
            fields={
                "Giver:": interaction.user.mention,
                "Recipient:": member.mention,
                "Amount:": amount,
                "Reason:": reason,
            },
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )
        await interaction.guild.get_channel(self.config.channels.user_chanes).send(
            embed=log_embed
        )
        await interaction.guild.get_channel(self.config.channels.alert).send(
            embed=log_embed
        )

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

        if message.type == nextcord.MessageType.reply:
            xp += 5

        await self.earn_xp(message.author, xp, XPType.MESSAGE)

        self.reports[message.author.id].last_message[message.channel.id] = (
            message.created_at.timestamp()
        )

    @commands.Cog.listener()
    async def on_add_xp(self, member: nextcord.Member, amount: int, type: str):
        await self.earn_xp(member, amount, XPType[type])

    @commands.Cog.listener()
    async def on_remove_xp(self, member: nextcord.Member, amount: int, type: str):
        await self.lose_xp(member, amount, XPType[type])


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Levelling(bot, kwargs["config"]))
