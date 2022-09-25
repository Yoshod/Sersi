import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal
from configutils import Configuration
from permutils import is_dark_mod, permcheck, is_senior_mod, is_cet


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


class CetAppModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Community Engagement Application")
        self.config = config

        self.aboutq = nextcord.ui.TextInput(label="Tell Us About Yourself", min_length=2, max_length=1024, required=True, style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.aboutq)

        self.whycet = nextcord.ui.TextInput(label="Why Do You Want To Join CET", min_length=2, max_length=1024, required=True, style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.whycet)

        self.priorexp = nextcord.ui.TextInput(label="Do You Have Prior Management Experience", min_length=2, max_length=1024, required=True, style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.priorexp)

        self.age = nextcord.ui.TextInput(label="How Old Are You", min_length=1, max_length=2, required=True)
        self.add_item(self.age)

        self.vc = nextcord.ui.TextInput(label="Are You Able To Voice Chat", min_length=2, max_length=1024, required=True)
        self.add_item(self.vc)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        applicant_id = interaction.user.id

        application_embed = nextcord.Embed(
            title="CET Application Received",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        application_embed.add_field(name=self.aboutq.label,     value=self.aboutq.value,    inline=False)
        application_embed.add_field(name=self.whycet.label,     value=self.whycet.value,    inline=False)
        application_embed.add_field(name=self.priorexp.label,   value=self.priorexp.value,  inline=False)
        application_embed.add_field(name=self.age.label,        value=self.age.value,       inline=False)
        application_embed.add_field(name=self.vc.label,         value=self.vc.value,        inline=False)

        accept_bttn = Button(custom_id=f"cet-application-next-steps:{applicant_id}", label="Move To Next Steps", style=nextcord.ButtonStyle.green)
        reject_bttn = Button(custom_id=f"cet-application-reject:{applicant_id}", label="Reject Application", style=nextcord.ButtonStyle.red)
        review_bttn = Button(custom_id=f"cet-application-review:{applicant_id}", label="Under Review", style=nextcord.ButtonStyle.grey)

        button_view = View(auto_defer=False)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)
        button_view.add_item(review_bttn)

        channel = interaction.client.get_channel(self.config.channels.cet_applications)
        await channel.send(embed=application_embed, view=button_view)


class Applications(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    async def cb_open_mod_modal(self, interaction):
        await interaction.response.send_modal(ModAppModal(self.config))

    async def cb_open_cet_modal(self, interaction):
        await interaction.response.send_modal(CetAppModal(self.config))

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
    async def staff_info(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        info_embed = nextcord.Embed(
            title="Staff Application Information",
            description="Staff applications are open all year round! If you wish to be a moderator, member of CET, or anything else on Adam Something Central, here are somethings to be aware of:",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        info_embed.add_field(name="Server Membership", value="We want all of our staff to be members of the Adam Something Central community. This means if you have been here for less than two months we will not be able to consider you.", inline=False)
        info_embed.add_field(name="Moderation History", value="Whilst having a moderation history on the server does not automatically prevent you from becoming a member of staff, expect to be challenged on your moderation history.", inline=False)
        info_embed.add_field(name="Age", value="Whilst we do not explicitly require staff to be of a certain age, bar the fact they must be old enough to use discord, those under the age of 18 can expect a little more grilling in order to determine maturity.", inline=False)
        info_embed.add_field(name="Applying", value="To apply all you have to do is press the 'Open Form' button above. This will show a short form inside of discord that you can fill in. The process is easy, and you will usually get a response within two days.", inline=False)
        await ctx.send(embed=info_embed)

    @commands.command()
    async def cet_apps(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        test_embed = nextcord.Embed(
            title="Community Engagement Team Application",
            description="Press the button below to apply to become a member of the Community Engagement Team on Adam Something Central.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        open_modal = Button(custom_id="cet-application-start", label="Open Form", style=nextcord.ButtonStyle.blurple)
        open_modal.callback = self.cb_open_cet_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            id_name, id_extra = interaction.data["custom_id"].split(":", 1)
        except ValueError:
            id_name = interaction.data["custom_id"]
            id_extra = None

        match id_name:
            case "mod-application-next-steps":
                if await permcheck(interaction, is_senior_mod):
                    user = interaction.guild.get_member(int(id_extra))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(name="Application Advanced by:", value=interaction.user.mention)
                    await interaction.message.edit(embed=updated_form, view=None)

                    advance_embed = nextcord.Embed(
                        title="Your Moderator Application",
                        description="Your moderator application has been advanced to the next steps. Please create a Senior Moderator Ticket on Adam Something Central.",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    await user.send(embed=advance_embed)

            case "mod-application-reject":
                if await permcheck(interaction, is_senior_mod):
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
                if await permcheck(interaction, is_senior_mod):
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

            case "cet-application-next-steps":
                if await permcheck(interaction, is_cet):
                    user = interaction.guild.get_member(int(id_extra))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(name="Application Advanced by:", value=interaction.user.mention)
                    await interaction.message.edit(embed=updated_form, view=None)

                    advance_embed = nextcord.Embed(
                        title="Your Community Engagement Application",
                        description="Your community engagement application has been advanced to the next steps. Please contact the Community Engagement Team Lead on Adam Something Central.",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    await user.send(embed=advance_embed)

            case "cet-application-reject":
                if await permcheck(interaction, is_cet):
                    user = interaction.guild.get_member(int(id_extra))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(name="Application Rejected by:", value=interaction.user.mention)
                    await interaction.message.edit(embed=updated_form, view=None)

                    rejection_embed = nextcord.Embed(
                        title="Your Community Engagement Application",
                        description="Your community engagement application has been rejected. Thanks for applying, we encourage you to try again in the future.",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    await user.send(embed=rejection_embed)

            case "cet-application-review":
                if await permcheck(interaction, is_cet):
                    user = interaction.guild.get_member(int(id_extra))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(name="Review notified by:", value=interaction.user.mention)
                    accept_bttn = Button(custom_id=f"cet-application-next-steps:{id_extra}", label="Move To Next Steps", style=nextcord.ButtonStyle.green)
                    reject_bttn = Button(custom_id=f"cet-application-reject:{id_extra}", label="Reject Application", style=nextcord.ButtonStyle.red)
                    button_view = View(auto_defer=False)
                    button_view.add_item(accept_bttn)
                    button_view.add_item(reject_bttn)
                    await interaction.message.edit(embed=updated_form, view=button_view)

                    review_embed = nextcord.Embed(
                        title="Your Community Engagement Application",
                        description="Your community engagement application has been received and is now under consideration. You will receive more information in the coming days.",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    await user.send(embed=review_embed)

            case "cet-application-start":
                await interaction.response.send_modal(CetAppModal(self.config))


def setup(bot, **kwargs):
    bot.add_cog(Applications(bot, kwargs["config"]))
