import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.perms import permcheck, is_staff
from utils.sersi_embed import SersiEmbed


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = self.config.emotes.success
        self.sersifail = self.config.emotes.fail

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Mass move members from one VC to another.",
    )
    async def mass_move(
        self,
        interaction: nextcord.Interaction,
        current: nextcord.VoiceChannel,
        target: nextcord.VoiceChannel,
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        memberlist = ""
        for member in current.members:
            memberlist = memberlist + f"**{member.display_name}** ({member.id})\n"
            await member.move_to(
                channel=target,
                reason=f"Mass move by {interaction.user} ({interaction.user.id})",
            )

        await interaction.followup.send(
            f"All members in {current.mention} were moved to {target.mention}",
            ephemeral=True,
        )

        # logging

        embed = SersiEmbed(
            title="Members mass moved to other VC",
            description="All members in channel were moved to another VC",
            fields=[
                {
                    "Move done by:": interaction.user.mention,
                    "From channel:": current.mention,
                    "To channel:": target.mention,
                },
                {
                    "Members Moved:": memberlist,
                },
            ],
            footer="Voice Cog",
            footer_icon=interaction.user.avatar.url,
        )

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ):
        if after.channel != before.channel:
            # channel change. at least one message has to be sent
            # specifications regardless of message content

            if after.channel is not None:
                embed = SersiEmbed(
                    description=f"Hello {member.mention}, welcome to {after.channel.mention}!"
                    if before.channel is None
                    else f"Hello {member.mention}, welcome to {after.channel.mention}! Glad you came over from {before.channel.mention}",
                    footer=member.display_name,
                    footer_icon=member.avatar.url,
                )
                await after.channel.send(embed=embed)

            if before.channel is not None:
                embed = SersiEmbed(
                    description=f"{member.mention} has left the voice channel. Goodbye!"
                    if after.channel is None
                    else f"{member.mention} ran off to {after.channel.mention}, guess the grass was greener there!",
                    footer=member.display_name,
                    footer_icon=member.avatar.url,
                )
                await before.channel.send(embed=embed)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Voice(bot, kwargs["config"]))
