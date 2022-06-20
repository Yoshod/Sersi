import nextcord
from nextcord.ext import commands
from baseutils import ConfirmView
from configutils import get_options, get_config, get_config_int
from permutils import permcheck, is_staff, is_mod, is_senior_mod


class Moderators(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')

    async def cb_addticket_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        ticket_support = interaction.guild.get_role(get_config_int('PERMISSION ROLES', 'ticket support'))
        await member.add_roles(ticket_support)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was given the {ticket_support.name} role.", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title=f"New {ticket_support.name} member added.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name=f"New {ticket_support.name}:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command(aliases=["addticket"])
    async def addticketsupport(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_staff):
            return

        dialog_embed = nextcord.Embed(
            title="Add Member as ticket Support",
            description="Following member will be assigned the ticket support role:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_addticket_proceed).send_as_reply(ctx, embed=dialog_embed)

    async def cb_rmticket_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        ticket_support = interaction.guild.get_role(get_config_int('PERMISSION ROLES', 'ticket support'))
        await member.remove_roles(ticket_support)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was removed from the {ticket_support.name} role.", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title=f"{ticket_support.name} member removed.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name=f"Former {ticket_support.name}:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command(aliases=["rmticket"])
    async def removeticketsupport(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_staff):
            return

        dialog_embed = nextcord.Embed(
            title="Add Member as ticket Support",
            description="Following member will be assigned the ticket support role:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_rmticket_proceed).send_as_reply(ctx, embed=dialog_embed)

    @commands.command()
    async def addtrialmod(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_senior_mod):
            return

        is_blacklisted = await ctx.invoke(self.bot.get_command('checkblacklist'), member=member)
        if is_blacklisted:
            await ctx.send(f"Member {member} cannot be given Trial Mod! Reason: Is on blacklist")
            return

        trial_moderator = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        await member.add_roles(trial_moderator, reason="Sersi addtrialmod command", atomic=True)
        await ctx.send(f"{self.sersisuccess} {member.mention} was given the {trial_moderator.name} role.")

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
        if not await permcheck(ctx, is_senior_mod):
            return

        trial_moderator = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        moderator       = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'moderator'))

        if trial_moderator not in member.roles:
            await ctx.reply(f"{self.sersifail} Member is not a trial mod")
            return

        await member.remove_roles(trial_moderator, reason="Sersi makefullmod command", atomic=True)
        await member.add_roles(moderator, reason="Sersi makefullmod command", atomic=True)
        await ctx.send(f"{self.sersisuccess} {member.mention} was given the {moderator.name} role.\nRemember: You're not truly a mod until your first ban. ;)")

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

    @commands.command(aliases=['purgemod', 'purge_mod'])
    async def removefrommod(self, ctx, member: nextcord.Member, *, reason=""):
        if not await permcheck(ctx, is_senior_mod):
            return

        if reason == "":
            await ctx.send(f"{ctx.author.mention} please provide a reason.")
            return

        for role in get_options('PERMISSION ROLES'):
            role_obj = ctx.guild.get_role(get_config_int('PERMISSION ROLES', role))
            await member.remove_roles(role_obj, reason=reason, atomic=True)

        await ctx.send(f"{self.sersisuccess} {member.mention} has been dishonourly discharged from the staff team. Good riddance!")
        await ctx.invoke(self.bot.get_command('blacklistuser'), member=member, reason=reason)

        # logging
        log_embed = nextcord.Embed(
            title="Member has been purged from staff and mod team."
        )
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name="Purged Moderator:", value=member.mention, inline=False)
        log_embed.add_field(name="Reason:", value=reason, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command()
    async def retire(self, ctx, member: nextcord.Member = None):
        if member is None and permcheck(ctx, is_mod):
            member = ctx.author
        elif not await permcheck(ctx, is_senior_mod):
            return

        for role in get_options('PERMISSION ROLES'):
            role_obj = ctx.guild.get_role(get_config_int('PERMISSION ROLES', role))
            await member.remove_roles(role_obj)

        honourable_member = ctx.guild.get_role(get_config_int('ROLES', 'honourable member'))
        await member.add_roles(honourable_member)

        await ctx.send(f"{self.sersisuccess} {member.mention} has retired from the mod team. Thank you for your service!")

        # logging
        log_embed = nextcord.Embed(
            title="Moderator has (been) retired."
        )
        log_embed.add_field(name="Responsible Moderator:", value=ctx.author.mention, inline=False)
        log_embed.add_field(name="Retired Moderator:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)


def setup(bot):
    bot.add_cog(Moderators(bot))
