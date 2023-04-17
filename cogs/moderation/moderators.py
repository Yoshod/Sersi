import datetime

import nextcord
from nextcord import SlashOption
from nextcord.ext import commands

from baseutils import ConfirmView, DualCustodyView, SersiEmbed
from configutils import Configuration
from permutils import permcheck, is_staff, is_senior_mod, is_slt


class Moderators(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    async def cb_addticket_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        ticket_support = interaction.guild.get_role(
            self.config.permission_roles.ticket_support
        )
        await member.add_roles(ticket_support)
        await interaction.message.edit(
            f"{self.sersisuccess} {member.mention} was given the {ticket_support.name} role.",
            embed=None,
            view=None,
        )

        # logging
        log_embed = nextcord.Embed(
            title=f"New {ticket_support.name} member added.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        log_embed.add_field(
            name="Responsible Staff Member:",
            value=interaction.user.mention,
            inline=False,
        )
        log_embed.add_field(
            name=f"New {ticket_support.name}:", value=member.mention, inline=False
        )

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=log_embed)

    @commands.command(aliases=["addticket"])
    async def addticketsupport(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_staff):
            return

        dialog_embed = nextcord.Embed(
            title="Add Member as ticket Support",
            description="Following member will be assigned the ticket support role:",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_addticket_proceed).send_as_reply(
            ctx, embed=dialog_embed
        )

    async def cb_rmticket_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        ticket_support = interaction.guild.get_role(
            self.config.permission_roles.ticket_support
        )
        await member.remove_roles(ticket_support)
        await interaction.message.edit(
            f"{self.sersisuccess} {member.mention} was removed from the {ticket_support.name} role.",
            embed=None,
            view=None,
        )

        # logging
        log_embed = nextcord.Embed(
            title=f"{ticket_support.name} member removed.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        log_embed.add_field(
            name="Responsible Staff Member:",
            value=interaction.user.mention,
            inline=False,
        )
        log_embed.add_field(
            name=f"Former {ticket_support.name}:", value=member.mention, inline=False
        )

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=log_embed)

    @commands.command(aliases=["rmticket"])
    async def removeticketsupport(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_staff):
            return

        dialog_embed = nextcord.Embed(
            title="Add Member as ticket Support",
            description="Following member will be assigned the ticket support role:",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_rmticket_proceed).send_as_reply(
            ctx, embed=dialog_embed
        )

    async def cb_addtrialmod_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        trial_moderator = interaction.guild.get_role(
            self.config.permission_roles.trial_moderator
        )
        await member.add_roles(
            trial_moderator, reason="Sersi addtrialmod command", atomic=True
        )
        await interaction.message.edit(
            f"{self.sersisuccess} {member.mention} was given the {trial_moderator.name} role.",
            embed=None,
            view=None,
        )

        # logging
        log_embed = nextcord.Embed(title="New Trial Moderator added.")
        log_embed.add_field(
            name="Responsible Moderator:", value=interaction.user.mention, inline=False
        )
        log_embed.add_field(
            name=f"New {trial_moderator.name}:", value=member.mention, inline=False
        )

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=log_embed)

    @commands.command()
    async def addtrialmod(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_senior_mod):
            return

        is_blacklisted = await ctx.invoke(
            self.bot.get_command("checkblacklist"), member=member
        )
        if is_blacklisted:
            await ctx.send(
                f"Member {member} cannot be given Trial Mod! Reason: Is on blacklist"
            )
            return

        dialog_embed = nextcord.Embed(
            title="Add new Trial Moderator",
            description="Following member will be assigned the Trial Moderator role:",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_addtrialmod_proceed).send_as_reply(
            ctx, embed=dialog_embed
        )

    async def cb_makefullmod_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        trial_moderator = interaction.guild.get_role(
            self.config.permission_roles.ticket_support
        )
        moderator = interaction.guild.get_role(self.config.permission_roles.moderator)

        await member.remove_roles(
            trial_moderator, reason="Sersi makefullmod command", atomic=True
        )
        await member.add_roles(
            moderator, reason="Sersi makefullmod command", atomic=True
        )
        await interaction.message.edit(
            f"{self.sersisuccess} {member.mention} was given the {moderator.name} role.\nRemember: You're not truly a "
            "mod until your first ban. ;)",
            embed=None,
            view=None,
        )

        # logging
        log_embed = nextcord.Embed(
            title="Trial Moderator matured into a full Moderator."
        )
        log_embed.add_field(
            name="Responsible Moderator:", value=interaction.user.mention, inline=False
        )
        log_embed.add_field(name="New Moderator:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=log_embed)

    @commands.command()
    async def makefullmod(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_senior_mod):
            return

        trial_moderator = ctx.guild.get_role(
            self.config.permission_roles.trial_moderator
        )

        if trial_moderator not in member.roles:
            await ctx.reply(f"{self.sersifail} Member is not a trial moderator.")
            return

        dialog_embed = nextcord.Embed(
            title="Promote Trial Moderator to Moderator",
            description="Following Trial Moderator will be promoted to Moderator:",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_makefullmod_proceed).send_as_reply(
            ctx, embed=dialog_embed
        )

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

        for role in vars(self.config.permission_roles):
            role_obj = interaction.guild.get_role(
                vars(self.config.permission_roles)[role]
            )
            try:
                await member.remove_roles(role_obj, reason=reason, atomic=True)
            except nextcord.errors.HTTPException:
                continue

        await interaction.message.edit(
            f"{self.sersisuccess} {member.mention} has been dishonourly discharged from the staff team. Good riddance!",
            embed=None,
            view=None,
        )

        # logging
        log_embed: nextcord.Embed = SersiEmbed(
            title="Member has been purged from staff and mod team and added to blacklist.",
            fields={
                "Responsible Moderator:": moderator.mention,
                "Confirming Moderator:": interaction.user.mention,
                "Purged Moderator:": member.mention,
                "Reason:": reason,
            },
            footer="Moderator Purge",
        )
        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=log_embed)

    async def cb_purgemod_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        await interaction.message.edit(
            f"{self.sersisuccess} Dihonourable discharge of {member.mention} is now awaiting confirmation!",
            embed=None,
            view=None,
        )

        dialog_embed = nextcord.Embed(
            title="Purge Moderator Confirmation",
            description="Following Moderator will be dishonorably discharged from the staff:",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)
        dialog_embed.add_field(
            name="Responsible Moderator", value=interaction.user.mention
        )
        dialog_embed.add_field(name="Moderator ID", value=interaction.user.id)

        channel = interaction.guild.get_channel(self.config.channels.alert)
        view = DualCustodyView(
            self.cb_purgemod_confirm, interaction.user, is_senior_mod
        )
        await view.send_dialogue(channel, embed=dialog_embed)

    @commands.command(aliases=["purgemod", "purge_mod"])
    async def removefrommod(self, ctx, member: nextcord.Member, *, reason=""):
        if not await permcheck(ctx, is_senior_mod):
            return

        if reason == "":
            await ctx.send(f"{ctx.author.mention} please provide a reason.")
            return

        dialog_embed = nextcord.Embed(
            title="Purge Moderator",
            description="Following Moderator will be dishonorably discharged from the staff:",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)

        await ConfirmView(self.cb_purgemod_proceed).send_as_reply(
            ctx, embed=dialog_embed
        )

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to retire staff members from their post",
    )
    async def retire(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            required=False,
            description="Who to retire; Specify yourself to retire yourself.",
        ),
    ):
        if member == interaction.user:
            if not await permcheck(interaction, is_staff):
                return
        else:
            if not await permcheck(interaction, is_slt):
                return

        await interaction.response.defer(ephemeral=True)

        print("remove any permission roles")
        # remove any permission roles
        for role in vars(self.config.permission_roles):
            role_object: nextcord.Role = interaction.guild.get_role(
                vars(self.config.permission_roles)[role]
            )
            try:
                await member.remove_roles(role_object)
            except nextcord.errors.HTTPException:
                continue

        honourable_member: nextcord.Role = interaction.guild.get_role(
            self.config.roles.honourable_member
        )
        await member.add_roles(honourable_member)

        await interaction.followup.edit(
            f"{self.sersisuccess} {member.mention} has retired from the mod team. Thank you for your service!",
            embed=None,
            view=None,
        )

        # logging
        log_embed: nextcord.Embed = SersiEmbed(
            title="Moderator has (been) retired.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                "Retired Moderator:": member.mention,
            },
        )

        channel: nextcord.TextChannel = interaction.guild.get_channel(
            self.config.channels.logging
        )
        await channel.send(embed=log_embed)

        channel: nextcord.TextChannel = interaction.guild.get_channel(
            self.config.channels.mod_logs
        )
        await channel.send(embed=log_embed)


def setup(bot, **kwargs):
    bot.add_cog(Moderators(bot, kwargs["config"]))
