import nextcord
from nextcord.ext import commands

from baseutils import SersiEmbed, get_discord_timestamp
from configutils import Configuration


class JoinLeave(commands.Cog):
    # Credit to: https://medium.com/@tonite/finding-the-invite-code-a-user-used-to-join-your-discord-server-using-discord-py-5e3734b8f21f
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.invites: dict[int : list[nextcord.Invite]] = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # Getting all the guilds our bot is in
        for guild in self.bot.guilds:
            # Adding each guild's invites to our dict
            self.invites[guild.id] = await guild.invites()

    def find_invite_by_code(self, invite_list: list[nextcord.Invite], code: str):

        for invite in invite_list:
            if invite.code == code:
                return invite

    async def get_invite_used(self, member: nextcord.Member) -> nextcord.Invite:

        invites_before_join: list[nextcord.Invite] = self.invites[member.guild.id]
        invites_after_join: list[nextcord.Invite] = await member.guild.invites()

        for invite in invites_before_join:
            if (
                invite.uses
                < self.find_invite_by_code(invites_after_join, invite.code).uses
            ):
                self.invites[member.guild.id] = invites_after_join
                return invite

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):

        invite: nextcord.Invite = await self.get_invite_used(member)

        logging_embed: nextcord.Embed = SersiEmbed(
            description=f"{member.mention} joined",
            fields={
                "Name": f"{member.mention} ({member.id})",
                "Joined At": f"{get_discord_timestamp(member.joined_at)} ({get_discord_timestamp(member.joined_at, relative=True)})",
                "Account Created": f"{get_discord_timestamp(member.created_at)} ({get_discord_timestamp(member.created_at, relative=True)})",
                "Guild Member Count": member.guild.member_count,
                "Inviter": f"{invite.inviter.mention} ({invite.inviter.id})",
                "Invite Used": f"{invite.code} with {invite.uses} uses",
            },
            footer="Sersi Join/Leave Logging",
            colour=nextcord.Colour.brand_green(),
        )
        logging_embed.set_author(name=member, icon_url=member.display_avatar.url)

        await member.guild.get_channel(self.config.channels.joinleave).send(
            embed=logging_embed
        )

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        # Updates the cache when a user leaves to make sure
        # everything is up to date

        self.invites[member.guild.id] = await member.guild.invites()

        logging_embed: nextcord.Embed = SersiEmbed(
            description=f"{member.mention} left",
            fields={
                "Name": f"{member.mention} ({member.id})",
                "Joined At": f"{get_discord_timestamp(member.joined_at)} ({get_discord_timestamp(member.joined_at, relative=True)})",
                "Account Created": f"{get_discord_timestamp(member.created_at)} ({get_discord_timestamp(member.created_at, relative=True)})",
                "Guild Member Count": member.guild.member_count,
                "Roles": ", ".join([role.name for role in member.roles]),
            },
            footer="Sersi Join/Leave Logging",
            colour=nextcord.Colour.brand_red(),
        )
        logging_embed.set_author(name=member, icon_url=member.display_avatar.url)

        await member.guild.get_channel(self.config.channels.joinleave).send(
            embed=logging_embed
        )


def setup(bot, **kwargs):
    bot.add_cog(JoinLeave(bot, kwargs["config"]))