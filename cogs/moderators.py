import nextcord
from nextcord.ext import commands

from baseutils import ConfirmView, DualCustodyView
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
        log_embed.add_field(name="Responsible Staff Member:", value=interaction.user.mention, inline=False)
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
        log_embed.add_field(name="Responsible Staff Member:", value=interaction.user.mention, inline=False)
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

    async def cb_addtrialmod_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        trial_moderator = interaction.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        await member.add_roles(trial_moderator, reason="Sersi addtrialmod command", atomic=True)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was given the {trial_moderator.name} role.", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title="New Trial Moderator added."
        )
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name=f"New {trial_moderator.name}:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command()
    async def addtrialmod(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_senior_mod):
            return

        is_blacklisted = await ctx.invoke(self.bot.get_command('checkblacklist'), member=member)
        if is_blacklisted:
            await ctx.send(f"Member {member} cannot be given Trial Mod! Reason: Is on blacklist")
            return

        dialog_embed = nextcord.Embed(
            title="Add new Trial Moderator",
            description="Following member will be assigned the Trial Moderator role:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_addtrialmod_proceed).send_as_reply(ctx, embed=dialog_embed)

    async def cb_makefullmod_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        trial_moderator = interaction.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))
        moderator       = interaction.guild.get_role(get_config_int('PERMISSION ROLES', 'moderator'))

        await member.remove_roles(trial_moderator, reason="Sersi makefullmod command", atomic=True)
        await member.add_roles(moderator, reason="Sersi makefullmod command", atomic=True)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was given the {moderator.name} role.\nRemember: You're not truly a mod until your first ban. ;)", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title="Trial Moderator matured into a full Moderator."
        )
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="New Moderator:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command()
    async def makefullmod(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_senior_mod):
            return

        trial_moderator = ctx.guild.get_role(get_config_int('PERMISSION ROLES', 'trial moderator'))

        if trial_moderator not in member.roles:
            await ctx.reply(f"{self.sersifail} Member is not a trial mod")
            return

        dialog_embed = nextcord.Embed(
            title="Promote Trial Moderator to Moderator",
            description="Following Trial Moderator will be promoted to Moderator:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_makefullmod_proceed).send_as_reply(ctx, embed=dialog_embed)

    async def cb_purgemod_confirm(self, interaction):
        member_id, mod_id, reason = 0, 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
            elif field.name == "Moderator ID":
                mod_id = int(field.value)
        member = interaction.guild.get_member(member_id)
        moderator = interaction.guild.get_member(mod_id)

        for role in get_options('PERMISSION ROLES'):
            role_obj = interaction.guild.get_role(get_config_int('PERMISSION ROLES', role))
            await member.remove_roles(role_obj, reason=reason, atomic=True)

        await interaction.message.edit(f"{self.sersisuccess} {member.mention} has been dishonourly discharged from the staff team. Good riddance!", embed=None, view=None)
        ctx = await self.bot.get_context(interaction.message)
        await ctx.invoke(self.bot.get_command('blacklistuser'), member=member, reason="Moderator purged with reason: " + reason)

        # logging
        log_embed = nextcord.Embed(
            title="Member has been purged from staff and mod team and added to blacklist."
        )
        log_embed.add_field(name="Responsible Moderator:", value=moderator.mention, inline=False)
        log_embed.add_field(name="Confirming Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="Purged Moderator:", value=member.mention, inline=False)
        log_embed.add_field(name="Reason:", value=reason, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    async def cb_purgemod_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        await interaction.message.edit(f"{self.sersisuccess} Dihonourable discharge of {member.mention} is now awaiting confirmation!", embed=None, view=None)

        dialog_embed = nextcord.Embed(
            title="Purge Moderator Confirmation",
            description="Following Moderator will be dishonorably discharged from the staff:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)
        dialog_embed.add_field(name="Responsible Moderator", value=interaction.user.mention)
        dialog_embed.add_field(name="Moderator ID", value=interaction.user.id)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'alert'))
        view = DualCustodyView(self.cb_purgemod_confirm, interaction.user, is_senior_mod)
        await view.send_dialogue(channel, embed=dialog_embed)

    @commands.command(aliases=['purgemod', 'purge_mod'])
    async def removefrommod(self, ctx, member: nextcord.Member, *, reason=""):
        if not await permcheck(ctx, is_senior_mod):
            return

        if reason == "":
            await ctx.send(f"{ctx.author.mention} please provide a reason.")
            return

        dialog_embed = nextcord.Embed(
            title="Purge Moderator",
            description="Following Moderator will be dishonorably discharged from the staff:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)

        await ConfirmView(self.cb_purgemod_proceed).send_as_reply(ctx, embed=dialog_embed)

    async def cb_retire_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        for role in get_options('PERMISSION ROLES'):
            role_obj = interaction.guild.get_role(get_config_int('PERMISSION ROLES', role))
            await member.remove_roles(role_obj)

        honourable_member = interaction.guild.get_role(get_config_int('ROLES', 'honourable member'))
        await member.add_roles(honourable_member)

        await interaction.message.edit(f"{self.sersisuccess} {member.mention} has retired from the mod team. Thank you for your service!", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title="Moderator has (been) retired."
        )
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="Retired Moderator:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.command()
    async def retire(self, ctx, member: nextcord.Member = None):
        if member is None and await permcheck(ctx, is_staff):
            member = ctx.author
        elif not await permcheck(ctx, is_senior_mod):
            return

        if member == ctx.author:
            dialog_embed = nextcord.Embed(
                title="Retire from Adam Something Central staff",
                description="Are you sure you want to retire?",
                color=nextcord.Color.from_rgb(237, 91, 6))
            dialog_embed.add_field(name="User", value=ctx.author.mention)
            dialog_embed.add_field(name="User ID", value=ctx.author.id)
        else:
            dialog_embed = nextcord.Embed(
                title="Retire Moderator",
                description="Following Moderator will be retired from the staff and given the Honourable member role:",
                color=nextcord.Color.from_rgb(237, 91, 6))
            dialog_embed.add_field(name="User", value=member.mention)
            dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_retire_proceed).send_as_reply(ctx, embed=dialog_embed)


def setup(bot):
    bot.add_cog(Moderators(bot))
