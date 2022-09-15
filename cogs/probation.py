import nextcord
from nextcord.ext import commands

from baseutils import ConfirmView, DualCustodyView
from configutils import Configuration
from permutils import permcheck, is_mod, is_full_mod
from caseutils import case_history, probation_case


class Probation(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    async def cb_addprob_confirm(self, interaction):
        member_id, mod_id, reason = 0, 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Moderator ID":
                mod_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)
        moderator = interaction.guild.get_member(mod_id)

        probation_role = interaction.guild.get_role(self.config.roles.probation)
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
        log_embed.add_field(name="Resposible Moderator:", value=moderator.mention, inline=False)
        log_embed.add_field(name="Confirming Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="Member:", value=member.mention, inline=False)
        log_embed.add_field(name="Reason:", value=reason, inline=False)

        log_channel = interaction.guild.get_channel(self.config.channels.logging)
        await log_channel.send(embed=log_embed)

        log_channel = interaction.guild.get_channel(self.config.channels.modlogs)
        await log_channel.send(embed=log_embed)

        unique_id = case_history(member.id, "Probation")
        probation_case(unique_id, member.id, moderator.id, interaction.user.id, reason)

        dm_embed = nextcord.Embed(
            title="Adam Something Central Probation",
            description="Your behaviour on Adam Something Central has resulted in being put into probation by a moderator, continued rule breaking may result in a ban",
            colour=nextcord.Colour.brand_red())
        dm_embed.add_field(name="Reason specified by moderator:", value=reason, inline=False)
        await member.send(embed=dm_embed)

    async def cb_addprob_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        dialog_embed = nextcord.Embed(
            title="Add Member to probation",
            description="Following member will be given probation:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)
        dialog_embed.add_field(name="Moderator", value=interaction.user.mention)
        dialog_embed.add_field(name="Moderator ID", value=interaction.user.id)

        channel = interaction.guild.get_channel(self.config.channels.alert)
        view = DualCustodyView(self.cb_addprob_confirm, interaction.user, is_full_mod)
        await view.send_dialogue(channel, embed=dialog_embed)

        await interaction.message.edit(f"Putting {member.mention} into probation was sent for approval by another moderator", embed=None, view=None)

    @commands.command(aliases=['addp', 'addprob', 'pn'])
    async def addprobation(self, ctx, member: nextcord.Member, *, reason="not specified"):
        if not await permcheck(ctx, is_mod):
            return

        probation_role = ctx.guild.get_role(self.config.roles.probation)

        if probation_role in member.roles:
            await ctx.reply(f"{self.sersifail} member is already in probation")
        else:
            dialog_embed = nextcord.Embed(
                title="Add Member to probation",
                description="Following member will be given probation:",
                color=nextcord.Color.from_rgb(237, 91, 6))
            dialog_embed.add_field(name="User", value=member.mention)
            dialog_embed.add_field(name="User ID", value=member.id)
            dialog_embed.add_field(name="Reason", value=reason, inline=False)

            await ConfirmView(self.cb_addprob_proceed).send_as_reply(ctx, embed=dialog_embed)

    async def cb_rmprob_confirm(self, interaction):
        member_id, mod_id, reason = 0, 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Moderator ID":
                mod_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)
        moderator = interaction.guild.get_member(mod_id)

        probation_role = interaction.guild.get_role(self.config.roles.probation)
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
        log_embed.add_field(name="Resposible Moderator:", value=moderator.mention, inline=False)
        log_embed.add_field(name="Confirming Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="Member:", value=member.mention, inline=False)
        log_embed.add_field(name="Reason:", value=reason, inline=False)

        log_channel = interaction.guild.get_channel(self.config.channels.logging)
        await log_channel.send(embed=log_embed)

        log_channel = interaction.guild.get_channel(self.config.channels.modlogs)
        await log_channel.send(embed=log_embed)

        dm_embed = nextcord.Embed(
            title="Adam Something Central Probation Over",
            description="You were removed from probation on Adam Something Central",
            colour=nextcord.Colour.brand_red())
        dm_embed.add_field(name="Reason specified by moderator:", value=reason, inline=False)
        await member.send(embed=dm_embed)

    async def cb_rmprob_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        dialog_embed = nextcord.Embed(
            title="Remove Member from probation",
            description="Following member will be removed from probation:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)
        dialog_embed.add_field(name="Moderator", value=interaction.user.mention)
        dialog_embed.add_field(name="Moderator ID", value=interaction.user.id)

        channel = interaction.guild.get_channel(self.config.channels.alert)
        view = DualCustodyView(self.cb_rmprob_confirm, interaction.user, is_full_mod)
        await view.send_dialogue(channel, embed=dialog_embed)

        await interaction.message.edit(f"Removing {member.mention} from probation was sent for approval by another moderator", embed=None, view=None)

    @commands.command(aliases=['rmp', 'rmprob'])
    async def removeprobation(self, ctx, member: nextcord.Member, *, reason):
        if not await permcheck(ctx, is_mod):
            return

        probation_role = ctx.guild.get_role(self.config.roles.probation)

        if probation_role not in member.roles:
            await ctx.reply("Error: cannot remove user from probation, member is currently not in probation")
        else:
            dialog_embed = nextcord.Embed(
                title="Add Member to probation",
                description="Following member will be given probation:",
                color=nextcord.Color.from_rgb(237, 91, 6))
            dialog_embed.add_field(name="User", value=member.mention)
            dialog_embed.add_field(name="User ID", value=member.id)
            dialog_embed.add_field(name="Reason", value=reason, inline=False)

            await ConfirmView(self.cb_rmprob_proceed).send_as_reply(ctx, embed=dialog_embed)


def setup(bot, **kwargs):
    bot.add_cog(Probation(bot, kwargs["config"]))
