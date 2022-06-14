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
        if not is_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission!")
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


def setup(bot):
    bot.add_cog(Voice(bot))
