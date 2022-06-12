import nextcord
from nextcord.ext import commands
from baseutils import *
# Doesn't do anything yet, got plans for this


class Moderators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def addtrialmod(self, ctx, member: nextcord.Member):
        if not is_senior_mod(ctx.author):
            await ctx.send("<:sersifail:979070135799279698> Insufficient permission.")
            return

        is_blacklisted = await ctx.invoke(self.bot.get_command('checkblacklist'), member=member)
        if is_blacklisted:
            await ctx.send(f"Member {member} cannot be given Trial Mod! Reason: Is on blacklist")
            return

        trial_moderator = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        await member.add_roles(trial_moderator, reason="Sersi addtrialmod command", atomic=True)

        # logging
        log_embed = nextcord.Embed(
            title="New Trial Moderator added."
        )
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name="New Trial Moderator:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command()
    async def makefullmod(self, ctx, member: nextcord.Member):
        if not is_senior_mod(ctx.author):
            await ctx.send("<:sersifail:979070135799279698> Insufficient permission.")
            return

        trial_moderator = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        moderator       = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'moderator'))

        if trial_moderator not in member.roles:
            await ctx.reply("<:sersifail:979070135799279698> Member is not a trial mod")

        await member.remove_roles(trial_moderator, reason="Sersi makefullmod command", atomic=True)
        await member.add_roles(moderator, reason="Sersi makefullmod command", atomic=True)

        # logging
        log_embed = nextcord.Embed(
            title="Trial Moderator matured into a full Moderator."
        )
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name="New Moderator:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command(aliases=['purge'])
    async def removefrommod(self, ctx, member: nextcord.Member, *reason):
        if not is_senior_mod(ctx.author):
            await ctx.send("<:sersifail:979070135799279698> Insufficient permission.")
            return

        reason_string = " ".join(reason)
        if reason == "":
            await ctx.send(f"{ctx.author.mention} please provide a reason.")

        for role in get_options('PERMISSION ROLES'):
            role_obj = ctx.guild.get_role(get_config_int('PERMISSION ROLES', role))
            await member.remove_roles(role_obj, reason=reason_string, atomic=True)

        await ctx.invoke(self.bot.get_command('blacklistuser'), member=member, reason=reason_string)

        # logging
        log_embed = nextcord.Embed(
            title="Member has been purged from staff and mod team."
        )
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name="Purged Moderator:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)


def setup(bot):
    bot.add_cog(Moderators(bot))
