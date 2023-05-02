import nextcord
from nextcord import SlashOption
from nextcord.ext import commands

from utils.base import ConfirmView, DualCustodyView, SersiEmbed
from utils.config import Configuration
from utils.perms import permcheck, is_staff, is_senior_mod, is_slt, is_dark_mod


class Staff(commands.Cog):
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

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Remove user from server staff in bad standing.",
    )
    async def discharge(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            required=True,
            description="Who to discharge, blacklist from server staff;",
        ),
        reason: str = SlashOption(
            required=True,
            description="Reason for discharging the user;",
            min_length=8,
            max_length=1024,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="(Mega Administrator only!) Reason to bypass dual custody",
            min_length=8,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_slt):
            return

        await interaction.response.defer()

        @ConfirmView.query(
            title="Discharge Staff Member",
            prompt=f"""Are you sure you want to proceed with dishonourable discharge of {member.mention}?
                All staff and permission roles will be removed from the member.
                This action will result in the user being blacklisted from the server staff.""",
            embed_args={"Reason": reason},
        )
        @DualCustodyView.query(
            title="Discharge Staff Member",
            prompt="Following staff member will be dishonorably discharged from the staff:",
            perms=is_slt,
            embed_args={"Member": member, "Reason": reason},
            bypass=True if bypass_reason else False,
        )
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            # remove staff/permission roles
            for role in vars(self.config.permission_roles):
                role_object: nextcord.Role = interaction.guild.get_role(
                    vars(self.config.permission_roles)[role]
                )
                if role_object is None:
                    continue
                try:
                    await member.remove_roles(role_object, reason=reason, atomic=True)
                except nextcord.errors.HTTPException:
                    continue

            embed_fields = {
                "Discharged Member:": member.mention,
                "Reason:": reason,
                "Responsible Member:": interaction.user.mention,
            }
            if bypass_reason and is_dark_mod(interaction.user):
                embed_fields["Bypass Reason:"] = bypass_reason
            else:
                embed_fields["Confirming Member:"] = confirming_moderator.mention

            log_embed = SersiEmbed(
                title="Dishonourable Discharge of Staff Member",
                description="Member has been purged from staff and mod team and added to blacklist.",
                fields=embed_fields,
                footer="Staff Discharge",
            )

            if bypass_reason:
                await interaction.followup.send(embed=log_embed)

            channel = interaction.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=log_embed)

        await execute(self.bot, self.config, interaction)

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
        if member is None:
            member = interaction.user
        print(member)
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
            if role_object is None:
                continue
            try:
                await member.remove_roles(role_object)
            except nextcord.errors.HTTPException:
                continue

        honourable_member: nextcord.Role = interaction.guild.get_role(
            self.config.roles.honourable_member
        )
        if honourable_member is None:
            await interaction.followup.send(
                f"{self.sersifail} Honourable Member role not found. Please contact an admin."
            )
        else:
            await member.add_roles(honourable_member)

        await interaction.followup.send(
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


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Staff(bot, kwargs["config"]))
