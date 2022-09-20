import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal

from baseutils import ConfirmView, DualCustodyView
from configutils import Configuration
from permutils import is_dark_mod, permcheck, is_staff, is_senior_mod


class ModAppModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Moderator Application")
        self.config = config

        self.aboutq = nextcord.ui.TextInput(label="Tell Us About Yourself", min_length=2, max_length=1024, required=True, style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.aboutq)

        self.whymod = nextcord.ui.TextInput(label="Why Do You Want To Become A Moderator", min_length=2, max_length=1024, required=True, style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.whymod)

        self.priorexp = nextcord.ui.TextInput(label="Do You Have Prior Moderation Experience", min_length=2, max_length=1024, required=True, style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.priorexp)

        self.age = nextcord.ui.TextInput(label="How Old Are You", min_length=1, max_length=2, required=True)
        self.add_item(self.age)

        self.vc = nextcord.ui.TextInput(label="Are You Able To Voice Chat", min_length=2, max_length=1024, required=True)
        self.add_item(self.vc)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        applicant_id = interaction.user.id

        application_embed = nextcord.Embed(
            title="Moderator Application Sent",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        application_embed.add_field(name=self.aboutq.label,     value=self.aboutq.value,    inline=False)
        application_embed.add_field(name=self.whymod.label,     value=self.whymod.value,    inline=False)
        application_embed.add_field(name=self.priorexp.label,   value=self.priorexp.value,  inline=False)
        application_embed.add_field(name=self.age.label,        value=self.age.value,       inline=False)
        application_embed.add_field(name=self.vc.label,         value=self.vc.value,        inline=False)

        accept_bttn = Button(custom_id=f"mod-application-next-steps:{applicant_id}", label="Move To Next Steps", style=nextcord.ButtonStyle.green)
        reject_bttn = Button(custom_id=f"mod-application-reject:{applicant_id}", label="Reject Application", style=nextcord.ButtonStyle.red)
        review_bttn = Button(custom_id=f"mod-application-review:{applicant_id}", label="Under Review", style=nextcord.ButtonStyle.grey)

        button_view = View(auto_defer=False)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)
        button_view.add_item(review_bttn)

        channel = interaction.client.get_channel(self.config.channels.mod_applications)
        await channel.send(embed=application_embed, view=button_view)


class Moderators(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    async def cb_open_mod_modal(self, interaction):
        await interaction.response.send_modal(ModAppModal(self.config))

    async def cb_addticket_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        ticket_support = interaction.guild.get_role(self.config.permission_roles.ticket_support)
        await member.add_roles(ticket_support)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was given the {ticket_support.name} role.", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title=f"New {ticket_support.name} member added.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="Responsible Staff Member:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name=f"New {ticket_support.name}:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
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

        ticket_support = interaction.guild.get_role(self.config.permission_roles.ticket_support)
        await member.remove_roles(ticket_support)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was removed from the {ticket_support.name} role.", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title=f"{ticket_support.name} member removed.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="Responsible Staff Member:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name=f"Former {ticket_support.name}:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
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

        trial_moderator = interaction.guild.get_role(self.config.permission_roles.trial_moderator)
        await member.add_roles(trial_moderator, reason="Sersi addtrialmod command", atomic=True)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was given the {trial_moderator.name} role.", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title="New Trial Moderator added."
        )
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name=f"New {trial_moderator.name}:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
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

        trial_moderator = interaction.guild.get_role(self.config.permission_roles.ticket_support)
        moderator       = interaction.guild.get_role(self.config.permission_roles.moderator)

        await member.remove_roles(trial_moderator, reason="Sersi makefullmod command", atomic=True)
        await member.add_roles(moderator, reason="Sersi makefullmod command", atomic=True)
        await interaction.message.edit(f"{self.sersisuccess} {member.mention} was given the {moderator.name} role.\nRemember: You're not truly a mod until your first ban. ;)", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title="Trial Moderator matured into a full Moderator."
        )
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="New Moderator:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
        await channel.send(embed=log_embed)

    @commands.command()
    async def makefullmod(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_senior_mod):
            return

        trial_moderator = ctx.guild.get_role(self.config.permission_roles.trial_moderator)

        if trial_moderator not in member.roles:
            await ctx.reply(f"{self.sersifail} Member is not a trial moderator.")
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

        for role in vars(self.config.permission_roles):
            role_obj = interaction.guild.get_role(vars(self.config.permission_roles)[role])
            try:
                await member.remove_roles(role_obj, reason=reason, atomic=True)
            except:
                continue

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

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
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

        channel = interaction.guild.get_channel(self.config.channels.alert)
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

        for role in vars(self.config.permission_roles):
            role_obj = interaction.guild.get_role(vars(self.config.permission_roles)[role])
            try:
                await member.remove_roles(role_obj)
            except:
                continue

        honourable_member = interaction.guild.get_role(self.config.roles.honourable_member)
        await member.add_roles(honourable_member)

        await interaction.message.edit(f"{self.sersisuccess} {member.mention} has retired from the mod team. Thank you for your service!", embed=None, view=None)

        # logging
        log_embed = nextcord.Embed(
            title="Moderator has (been) retired."
        )
        log_embed.add_field(name="Responsible Moderator:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="Retired Moderator:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
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

    @commands.command()
    async def mod_apps(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        test_embed = nextcord.Embed(
            title="Moderator Application",
            description="Press the button below to apply to become a moderator on Adam Something Central.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        open_modal = Button(custom_id="mod-application-start", label="Open Form", style=nextcord.ButtonStyle.blurple)
        open_modal.callback = self.cb_open_mod_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)

    @commands.command()
    async def mod_info(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        info_embed = nextcord.Embed(
            title="Moderator Application Information",
            description="Moderator applications are open all year round! If you wish to be a moderator on Adam Something Central, here are somethings to be aware of:",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        info_embed.add_field(name="Server Membership", value="We want all of our moderators to be members of the Adam Something Central community. This means if you have been here for less than two months we will not be able to consider you.", inline=False)
        info_embed.add_field(name="Moderation History", value="Whilst having a moderation history on the server does not automatically prevent you from becoming a moderator, expect to be challenged on your moderation history.", inline=False)
        info_embed.add_field(name="Age", value="Whilst we do not explicitly require moderators to be of a certain age, bar the fact they must be old enough to use discord, those under the age of 18 can expect a little more grilling in order to determine maturity.", inline=False)
        info_embed.add_field(name="Applying", value="To apply all you have to do is press the 'Open Form' button above. This will show a short form inside of discord that you can fill in. The process is easy, and you will usually get a response within two days.", inline=False)
        await ctx.send(embed=info_embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            id_name, id_extra = interaction.data["custom_id"].split(":", 1)
        except ValueError:
            id_name = interaction.data["custom_id"]
            id_extra = None

        match id_name:
            case "mod-application-next-steps":
                if await permcheck(interaction, is_dark_mod):
                    user = interaction.guild.get_member(int(id_extra))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(name="Application Advanced by:", value=interaction.user.mention)
                    await interaction.message.edit(embed=updated_form, view=None)

                    advance_embed = nextcord.Embed(
                        title="Your Moderator Application",
                        description="Your moderator application has been advanced to the next steps. Please create a Senior Moderator on Adam Something Central.",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    await user.send(embed=advance_embed)

            case "mod-application-reject":
                if await permcheck(interaction, is_dark_mod):
                    user = interaction.guild.get_member(int(id_extra))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(name="Application Rejected by:", value=interaction.user.mention)
                    await interaction.message.edit(embed=updated_form, view=None)

                    rejection_embed = nextcord.Embed(
                        title="Your Moderator Application",
                        description="Your moderator application has been rejected. Thanks for applying, we encourage you to try again in the future.",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    await user.send(embed=rejection_embed)

            case "mod-application-review":
                if await permcheck(interaction, is_dark_mod):
                    user = interaction.guild.get_member(int(id_extra))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(name="Review notified by:", value=interaction.user.mention)
                    accept_bttn = Button(custom_id=f"mod-application-next-steps:{id_extra}", label="Move To Next Steps", style=nextcord.ButtonStyle.green)
                    reject_bttn = Button(custom_id=f"mod-application-reject:{id_extra}", label="Reject Application", style=nextcord.ButtonStyle.red)
                    button_view = View(auto_defer=False)
                    button_view.add_item(accept_bttn)
                    button_view.add_item(reject_bttn)
                    await interaction.message.edit(embed=updated_form, view=button_view)

                    review_embed = nextcord.Embed(
                        title="Your Moderator Application",
                        description="Your moderator application has been received and is now under consideration. You will receive more information in the coming days.",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    await user.send(embed=review_embed)

            case "mod-application-start":
                await interaction.response.send_modal(ModAppModal(self.config))


def setup(bot, **kwargs):
    bot.add_cog(Moderators(bot, kwargs["config"]))
