import nextcord
from nextcord.ext import commands
from baseutils import *


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')

    @commands.command(aliases=['mvc', 'movevc', 'vcmove', 'mm'])
    async def massmove(self, ctx, current: nextcord.VoiceChannel, target: nextcord.VoiceChannel):
        """mass move members from one VC to another

        both VCs must be referenced to by mention or Channel ID"""
        if not await permcheck(ctx, is_mod):
            return

        memberlist = ""
        for member in current.members:
            memberlist = memberlist + f"**{member.display_name}** ({member.id})\n"
            await member.move_to(channel=target, reason=f"Mass move by {ctx.author} ({ctx.author.id})")

        # logging
        embed = nextcord.Embed(
            title="Members mass moved to other VC",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        embed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Original channel:", value=current.mention, inline=False)
        embed.add_field(name="Members moved to channel:", value=target.mention, inline=False)
        embed.add_field(name="Members Moved:", value=memberlist, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=embed)


    """The following, but not limited to, examples illustrate when this event is called:

    A member joins a voice or stage channel.
    A member leaves a voice or stage channel.
    A member is muted or deafened by their own accord.
    A member is muted or deafened by a guild administrator.
    """
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(f"Voice State Update")
        await channel.send(f"Member: {member}\nbefore: {before}\nafter: {after}")

        if before.channel is None:
            # greetings
            await after.channel.send(f"Hello {member.mention}, welcome to {after.channel.mention}!")

        elif after.channel is None:
            # goodbye
            await before.channel.send(f"{member.mention} has left the voice channel. Goodbye!")


def setup(bot):
    bot.add_cog(Voice(bot))
