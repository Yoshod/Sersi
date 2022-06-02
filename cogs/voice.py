import nextcord
from nextcord.ext import commands
from baseutils import *


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['mvc', 'movevc', 'vcmove'])
    async def massmove(self, ctx, current: nextcord.VoiceChannel, target: nextcord.VoiceChannel):
        if not isMod(ctx.author.roles):
            await ctx.send(f"<:sersifail:979070135799279698> Insufficient permission!")
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
        embed.add_field(name="Members Moved:", value=memberlist, inline=False)

        channel = ctx.guild.get_channel(getLoggingChannel(ctx.guild.id))
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Voice(bot))
