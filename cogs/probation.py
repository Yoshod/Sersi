import nextcord
from nextcord.ext import commands
from baseutils import *


class Probation(commands.Cog):
    def __init__(self, bot):
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.bot = bot
        self.notModFail = f"{sersifail} Only moderators can use this command."

    @commands.command(aliases=['addp', 'addprob'])
    async def addprobation(self, ctx, member: nextcord.Member, *args):
        if not is_mod(ctx.author):
            await ctx.reply(self.notModFail)
            return

        probation_role = ctx.guild.get_role(get_config_int('ROLES', 'probation'))
        reason = " ".join(args)
        if reason == "":
            reason = "not specified"

        if probation_role in member.roles:
            await ctx.reply("Error: member is already in probation")
        else:
            await member.add_roles(probation_role, reason=reason, atomic=True)

            confirmation_embed = nextcord.Embed(
                title="Member in Probation",
                description=f"{member.mention} has been put into probation, continued rule breaking may result in a ban",
                colour=nextcord.Colour.brand_red())
            await ctx.send(embed=confirmation_embed)

            log_embed = nextcord.Embed(
                title="Member put into Probation",
                color=nextcord.Color.from_rgb(237, 91, 6)
            )
            log_embed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
            log_embed.add_field(name="Member:", value=member.mention, inline=False)
            log_embed.add_field(name="Reason:", value=reason, inline=False)
            log_channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
            await log_channel.send(embed=log_embed)

            dm_embed = nextcord.Embed(
                title="Adam Something Central Probation",
                description=f"Your behauviour on Adam Something Central has resulted in being put into probation by a moderator, continued rule breaking may result in swift ban",
                colour=nextcord.Colour.brand_red())
            dm_embed.add_field(name="Reason specified by moderator:", value=reason, inline=False)
            await member.send(embed=dm_embed)

    @commands.command(aliases=['rmp', 'rmprob'])
    async def removeprobation(self, ctx, member: nextcord.Member, *args):
        if not is_mod(ctx.author):
            await ctx.reply(self.notModFail)
            return

        probation_role = ctx.guild.get_role(get_config_int('ROLES', 'probation'))
        reason = " ".join(args)

        if probation_role not in member.roles:
            await ctx.reply("Error: cannot remove user from probation, member is currently not in probation")
        else:
            await member.remove_roles(probation_role, reason=reason, atomic=True)

            confirmation_embed = nextcord.Embed(
                title="Member removed from Probation",
                description=f"{member.mention} was succesfully removed from probation!",
                colour=nextcord.Colour.brand_red())
            await ctx.send(embed=confirmation_embed)

            log_embed = nextcord.Embed(
                title="Member removed from Probation",
                color=nextcord.Color.from_rgb(237, 91, 6)
            )
            log_embed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
            log_embed.add_field(name="Member:", value=member.mention, inline=False)
            log_embed.add_field(name="Reason:", value=reason, inline=False)
            log_channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
            await log_channel.send(embed=log_embed)

            dm_embed = nextcord.Embed(
                title="Adam Something Central Probation Over",
                description=f"You were removed from probation on Adam Something Central",
                colour=nextcord.Colour.brand_red())
            dm_embed.add_field(name="Reason specified by moderator:", value=reason, inline=False)
            await member.send(embed=dm_embed)


def setup(bot):
    bot.add_cog(Probation(bot))
