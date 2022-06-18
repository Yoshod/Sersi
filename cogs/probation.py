import nextcord
from nextcord.ext import commands
from baseutils import *


class Probation(commands.Cog):
    def __init__(self, bot):
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.bot = bot

    async def cb_addprob_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        probation_role = interaction.guild.get_role(get_config_int('ROLES', 'probation'))
        await member.add_roles(probation_role, reason=reason, atomic=True)

        confirmation_embed = nextcord.Embed(
            title="Member in Probation",
            description=f"{member.mention} has been put into probation, continued rule breaking may result in a ban",
            colour=nextcord.Colour.brand_red())
        await interaction.message.edit(embed=confirmation_embed, view=None)

        log_embed = nextcord.Embed(
            title="Member put into Probation",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        log_embed.add_field(name="Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="Member:", value=member.mention, inline=False)
        log_embed.add_field(name="Reason:", value=reason, inline=False)
        log_channel = interaction.user.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await log_channel.send(embed=log_embed)

        dm_embed = nextcord.Embed(
            title="Adam Something Central Probation",
            description="Your behaviour on Adam Something Central has resulted in being put into probation by a moderator, continued rule breaking may result in a ban",
            colour=nextcord.Colour.brand_red())
        dm_embed.add_field(name="Reason specified by moderator:", value=reason, inline=False)
        await member.send(embed=dm_embed)

    @commands.command(aliases=['addp', 'addprob'])
    async def addprobation(self, ctx, member: nextcord.Member, *, reason):
        if not await permcheck(ctx, is_mod):
            return

        probation_role = ctx.guild.get_role(get_config_int('ROLES', 'probation'))

        if reason == "":
            reason = "not specified"

        if probation_role in member.roles:
            await ctx.reply(f"{self.sersifail} member is already in probation")
        else:
            dialog_embed = nextcord.Embed(
                title="Add Member to probation",
                description="Following member will be given probation:",
                color=nextcord.Color.from_rgb(237, 91, 6))
            dialog_embed.add_field(name="User", value=member.mention)
            dialog_embed.add_field(name="User ID", value=member.id)
            dialog_embed.add_field(name="Reason", value=reason)

            await ConfirmView(self.cb_addprob_proceed).send_as_reply(ctx, embed=dialog_embed)

    async def cb_rmprob_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        probation_role = interaction.guild.get_role(get_config_int('ROLES', 'probation'))
        await member.remove_roles(probation_role, reason=reason, atomic=True)

        confirmation_embed = nextcord.Embed(
            title="Member removed from Probation",
            description=f"{member.mention} was succesfully removed from probation!",
            colour=nextcord.Colour.brand_red())
        await interaction.message.edit(embed=confirmation_embed, view=None)

        log_embed = nextcord.Embed(
            title="Member removed from Probation",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        log_embed.add_field(name="Moderator:", value=interaction.user.author.mention, inline=False)
        log_embed.add_field(name="Member:", value=member.mention, inline=False)
        log_embed.add_field(name="Reason:", value=reason, inline=False)
        log_channel = interaction.user.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await log_channel.send(embed=log_embed)

        dm_embed = nextcord.Embed(
            title="Adam Something Central Probation Over",
            description="You were removed from probation on Adam Something Central",
            colour=nextcord.Colour.brand_red())
        dm_embed.add_field(name="Reason specified by moderator:", value=reason, inline=False)
        await member.send(embed=dm_embed)

    @commands.command(aliases=['rmp', 'rmprob'])
    async def removeprobation(self, ctx, member: nextcord.Member, *, reason):
        if not await permcheck(ctx, is_mod):
            return

        probation_role = ctx.guild.get_role(get_config_int('ROLES', 'probation'))

        if probation_role not in member.roles:
            await ctx.reply("Error: cannot remove user from probation, member is currently not in probation")
        else:
            dialog_embed = nextcord.Embed(
                title="Add Member to probation",
                description="Following member will be given probation:",
                color=nextcord.Color.from_rgb(237, 91, 6))
            dialog_embed.add_field(name="User", value=member.mention)
            dialog_embed.add_field(name="User ID", value=member.id)
            dialog_embed.add_field(name="Reason", value=reason)

            await ConfirmView(self.cb_rmprob_proceed).send_as_reply(ctx, embed=dialog_embed)


def setup(bot):
    bot.add_cog(Probation(bot))
