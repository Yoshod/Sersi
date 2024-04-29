import nextcord
import nextcord.ui
from nextcord.ext import commands

from utils.config import Configuration
from utils.sersi_embed import SersiEmbed


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        if member.flags.did_rejoin and member.communication_disabled_until:
            welcome_embed = SersiEmbed(
                title="Welcome back!",
                description=f"Welcome back to **{member.guild.name}**, {member.mention}! We're glad to have you back!\nYou are currently timed out from sending messages until {member.communication_disabled_until}. To appeal this, you can run the </ticket create:1169396755788468345> command. You can reply in that ticket using the </ticket send_message:1169396755788468345> command. To view the ticket, it will appear in the channel list in the server.",
            )

        elif member.flags.did_rejoin and member.communication_disabled_until is None:
            welcome_embed = SersiEmbed(
                title="Welcome back!",
                description=f"Welcome back to **{member.guild.name}**, {member.mention}! We're glad to have you back!",
            )

        else:
            welcome_embed = SersiEmbed(
                title="Welcome!",
                description=f"Welcome to **{member.guild.name}**, {member.mention}! We're glad to have you here! Once you have completed onboarding you will be able to chat in the server. Remember to check out our opt-in roles to see additional channels.",
            )

        try:
            await member.send(embed=welcome_embed)

        except nextcord.Forbidden:
            pass


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Welcome(bot, kwargs["config"]))
