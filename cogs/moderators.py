import nextcord
from nextcord.ext import commands
from baseutils import *
# Doesn't do anything yet, got plans for this


class Moderators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')

    @commands.command(aliases=["addticket"])
    async def addticketsupport(self, ctx, member: nextcord.Member):
        if not is_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission!")
            return

        ticket_support = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'ticket support'))
        await member.add_roles(ticket_support)
        ctx.send(f"{self.sersisuccess} {member.mention} was given the {ticket_support.name} role.")

        # logging
        log_embed = nextcord.Embed(
            title=f"New {ticket_support.name} member added.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name=f"New {ticket_support.name}:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command(aliases=["rmticket"])
    async def removeticketsupport(self, ctx, member: nextcord.Member):
        if not is_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission!")
            return

        ticket_support = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'ticket support'))
        await member.remove_roles(ticket_support)
        ctx.send(f"{self.sersisuccess} {member.mention} was removed from the {ticket_support.name} role.")

        # logging
        log_embed = nextcord.Embed(
            title=f"{ticket_support.name} member removed.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name=f"Former {ticket_support.name}:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command()
    async def addtrialmod(self, ctx, member: nextcord.Member):
        if not is_senior_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission.")
            return

        is_blacklisted = await ctx.invoke(self.bot.get_command('checkblacklist'), member=member)
        if is_blacklisted:
            await ctx.send(f"Member {member} cannot be given Trial Mod! Reason: Is on blacklist")
            return

        trial_moderator = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        await member.add_roles(trial_moderator, reason="Sersi addtrialmod command", atomic=True)
        ctx.send(f"{self.sersisuccess} {member.mention} was given the {trial_moderator.name} role.")

        # logging
        log_embed = nextcord.Embed(
            title="New Trial Moderator added."
        )
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name=f"New {trial_moderator.name}:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command()
    async def makefullmod(self, ctx, member: nextcord.Member):
        if not is_senior_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission.")
            return

        trial_moderator = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        moderator       = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'moderator'))

        if trial_moderator not in member.roles:
            await ctx.reply(f"{self.sersifail} Member is not a trial mod")

        await member.remove_roles(trial_moderator, reason="Sersi makefullmod command", atomic=True)
        await member.add_roles(moderator, reason="Sersi makefullmod command", atomic=True)
        ctx.send(f"{self.sersisuccess} {member.mention} was given the {moderator.name} role.\n Remember: You're not truly a mod until your first ban. ;)")

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
            await ctx.send(f"{self.sersifail} Insufficient permission.")
            return

        reason_string = " ".join(reason)
        if reason == "":
            await ctx.send(f"{ctx.author.mention} please provide a reason.")

        for role in get_options('PERMISSION ROLES'):
            role_obj = ctx.guild.get_role(get_config_int('PERMISSION ROLES', role))
            await member.remove_roles(role_obj, reason=reason_string, atomic=True)

        await ctx.send(f"{self.sersisuccess} {member.mention} has been dishonourly discharged from the staff team. Good riddance!")
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
