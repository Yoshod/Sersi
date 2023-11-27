import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal
from utils.config import Configuration
from utils.perms import (
    is_dark_mod,
    permcheck,
    is_senior_mod,
    is_cet,
    is_mod,
)
from utils.sersi_embed import SersiEmbed
from datetime import datetime
import pytz
from utils.roles import blacklist_check


class ModAppModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Moderator Application")
        self.config = config

        self.aboutq = nextcord.ui.TextInput(
            label="Tell Us About Yourself",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.aboutq)

        self.whymod = nextcord.ui.TextInput(
            label="Why Do You Want To Become A Moderator",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.whymod)

        self.priorexp = nextcord.ui.TextInput(
            label="Do You Have Prior Moderation Experience",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.priorexp)

        self.age = nextcord.ui.TextInput(
            label="How Old Are You", min_length=1, max_length=2, required=True
        )
        self.add_item(self.age)

        self.vc = nextcord.ui.TextInput(
            label="Are You Able To Voice Chat",
            min_length=2,
            max_length=1024,
            required=True,
        )
        self.add_item(self.vc)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        applicant_id = interaction.user.id

        if blacklist_check(interaction.user.id):
            embed_fields = {
                self.aboutq.label: self.aboutq.value,
                self.whymod.label: self.whymod.value,
                self.priorexp.label: self.priorexp.value,
                self.age.label: self.age.value,
                self.vc.label: self.vc.value,
                "Blacklisted": self.config.emotes.success,
            }

        else:
            embed_fields = {
                self.aboutq.label: self.aboutq.value,
                self.whymod.label: self.whymod.value,
                self.priorexp.label: self.priorexp.value,
                self.age.label: self.age.value,
                self.vc.label: self.vc.value,
            }

        application_embed = SersiEmbed(
            title="Moderator Application Sent",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            fields=embed_fields,
        )

        accept_bttn = Button(
            custom_id=f"mod-application-next-steps:{applicant_id}",
            label="Move To Next Steps",
            style=nextcord.ButtonStyle.green,
        )
        reject_bttn = Button(
            custom_id=f"mod-application-reject:{applicant_id}",
            label="Reject Application",
            style=nextcord.ButtonStyle.red,
        )
        review_bttn = Button(
            custom_id=f"mod-application-review:{applicant_id}",
            label="Under Review",
            style=nextcord.ButtonStyle.grey,
        )

        button_view = View(auto_defer=False)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)
        button_view.add_item(review_bttn)

        guild = interaction.client.get_guild(self.config.guilds.main)

        channel = guild.get_channel(self.config.channels.mod_applications)
        await channel.send(embed=application_embed, view=button_view)
        await interaction.response.send_message(
            f"{self.config.emotes.success} Your application has been received! Thanks for applying.",
            ephemeral=True,
        )


class CetAppModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Community Engagement Application")
        self.config = config

        self.aboutq = nextcord.ui.TextInput(
            label="Tell Us About Yourself",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.aboutq)

        self.whycet = nextcord.ui.TextInput(
            label="Why Do You Want To Join CET",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.whycet)

        self.priorexp = nextcord.ui.TextInput(
            label="Do You Have Prior Management Experience",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.priorexp)

        self.age = nextcord.ui.TextInput(
            label="How Old Are You", min_length=1, max_length=2, required=True
        )
        self.add_item(self.age)

        self.vc = nextcord.ui.TextInput(
            label="Are You Able To Voice Chat",
            min_length=2,
            max_length=1024,
            required=True,
        )
        self.add_item(self.vc)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        applicant_id = interaction.user.id

        application_embed = SersiEmbed(
            title="CET Application Received",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            fields={
                self.aboutq.label: self.aboutq.value,
                self.whycet.label: self.whycet.value,
                self.priorexp.label: self.priorexp.value,
                self.age.label: self.age.value,
                self.vc.label: self.vc.value,
            },
        )

        accept_bttn = Button(
            custom_id=f"cet-application-next-steps:{applicant_id}",
            label="Move To Next Steps",
            style=nextcord.ButtonStyle.green,
        )
        reject_bttn = Button(
            custom_id=f"cet-application-reject:{applicant_id}",
            label="Reject Application",
            style=nextcord.ButtonStyle.red,
        )
        review_bttn = Button(
            custom_id=f"cet-application-review:{applicant_id}",
            label="Under Review",
            style=nextcord.ButtonStyle.grey,
        )

        button_view = View(auto_defer=False)
        button_view.add_item(accept_bttn)
        button_view.add_item(reject_bttn)
        button_view.add_item(review_bttn)

        channel = interaction.client.get_channel(self.config.channels.cet_applications)
        await channel.send(embed=application_embed, view=button_view)


class Applications(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
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

        test_embed = SersiEmbed(
            title="Moderator Application",
            description="Press the button below to apply to become a moderator on The Crossroads.",
        )
        open_modal = Button(
            custom_id="mod-application-start",
            label="Open Form",
            style=nextcord.ButtonStyle.blurple,
        )
        open_modal.callback = self.cb_open_mod_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)

    @commands.command()
    async def staff_info(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        info_embed = SersiEmbed(
            title="Staff Application Information",
            description="Staff applications are open all year round! If you wish to be a moderator, member of CET, "
            "or anything else on The Crossroads, here are somethings to be aware of:",
            fields={
                "Server Membership": "We want all of our staff to be members of the The Crossroads community. "
                "This means if you have been here for less than two months we will not be able "
                "to consider you.",
                "Moderation History": "Whilst having a moderation history on the server does not automatically "
                "prevent you from becoming a member of staff, expect to be challenged on your "
                "moderation history.",
                "Age": "Whilst we do not explicitly require staff to be of a certain age, bar the fact they must be "
                "old enough to use discord, those under the age of 18 can expect a little more grilling in "
                "order to determine maturity.",
                "Applying": "To apply all you have to do is press the 'Open Form' button above. This will show a "
                "short form inside of discord that you can fill in. The process is easy, and you will "
                "usually get a response within two days.",
            },
        )

        await ctx.send(embed=info_embed)

    @commands.command()
    async def cet_apps(self, ctx: commands.Context):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        test_embed = SersiEmbed(
            title="Community Engagement Team Application",
            description=f"Press the button below to apply to become a member of the Community Engagement Team on {ctx.guild.name}",
        )
        open_modal = Button(
            custom_id="cet-application-start",
            label="Open Form",
            style=nextcord.ButtonStyle.blurple,
        )
        open_modal.callback = self.cb_open_cet_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Used to invite a user to apply to become a moderator",
    )
    async def moderator_invite(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member,
    ):
        if not await permcheck(interaction, is_mod):
            return

        if await blacklist_check(user):
            interaction.response.send_message(
                f"{self.config.emotes.fail} The user you wish to invite is blacklisted from the Staff Team. Speak to an Administrator.",
                ephemeral=True,
            )

        await interaction.response.defer(ephemeral=True)

        test_embed = SersiEmbed(
            title="Moderator Invite",
            description=""
            "Hey there! You've received this DM because a Moderator on The Crossroads thinks "
            "you'd be a great fit on our moderation team.\n\n"
            "If this interests you then all you have to do is press the Open Form button below and "
            "submit an application. If you're not interested in the role then that's okay too. "
            "In that case you can simply ignore this DM and you won't receive another one.",
        )
        open_modal = Button(
            custom_id="mod-application-start",
            label="Open Form",
            style=nextcord.ButtonStyle.blurple,
        )
        open_modal.callback = self.cb_open_mod_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        try:
            await user.send(embed=test_embed, view=button_view)
            await interaction.followup.send(
                f"{self.config.emotes.success} The user has successfully been sent the invitation to apply."
            )
            logging_embed = SersiEmbed(
                title="Moderator Invite Sent",
                description=f"Moderator {interaction.user.mention} ({interaction.user.id}) has sent a Moderator Invite to {user.mention} ({user.id}).",
                footer="Sersi Moderator Invite",
            )
            logging_embed.timestamp = datetime.now(pytz.UTC)
            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )
            await logging_channel.send(embed=logging_embed)
        except (nextcord.HTTPException, nextcord.Forbidden):
            await interaction.followup.send(
                f"{self.config.emotes.fail} The message was not able to be sent. The user may have their DMs closed. Consider sending them a direct message."
            )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["mod-application-next-steps", user_id]:
                if await permcheck(interaction, is_senior_mod):
                    if blacklist_check(interaction.guild.get_member(user_id)):
                        interaction.response.send_message(
                            f"{self.config.emotes.fail} This user is on the staff team blacklist. Please speak to an Administrator."
                        )
                        return

                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Application Advanced by:", value=interaction.user.mention
                    )
                    await interaction.message.edit(embed=updated_form, view=None)

                    advance_embed = nextcord.Embed(
                        title="Your Moderator Application",
                        description="Your moderator application has been advanced to the next steps. Please create a "
                        "Moderation Lead Ticket on The Crossroads.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=advance_embed)

            case ["mod-application-reject", user_id]:
                if await permcheck(interaction, is_senior_mod):
                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Application Rejected by:", value=interaction.user.mention
                    )
                    await interaction.message.edit(embed=updated_form, view=None)

                    rejection_embed = nextcord.Embed(
                        title="Your Moderator Application",
                        description="Your moderator application has been rejected. Thanks for applying, we encourage "
                        "you to try again in the future.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=rejection_embed)

            case ["mod-application-review", user_id]:
                if await permcheck(interaction, is_senior_mod):
                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Review notified by:", value=interaction.user.mention
                    )
                    accept_bttn = Button(
                        custom_id=f"mod-application-next-steps:{user_id}",
                        label="Move To Next Steps",
                        style=nextcord.ButtonStyle.green,
                    )
                    reject_bttn = Button(
                        custom_id=f"mod-application-reject:{user_id}",
                        label="Reject Application",
                        style=nextcord.ButtonStyle.red,
                    )
                    button_view = View(auto_defer=False)
                    button_view.add_item(accept_bttn)
                    button_view.add_item(reject_bttn)
                    await interaction.message.edit(embed=updated_form, view=button_view)

                    review_embed = nextcord.Embed(
                        title="Your Moderator Application",
                        description="Your moderator application has been received and is now under consideration. You "
                        "will receive more information in the coming days.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=review_embed)

            case ["mod-application-start"]:
                await interaction.response.send_modal(ModAppModal(self.config))

            case ["cet-application-next-steps", user_id]:
                if await permcheck(interaction, is_cet):
                    if blacklist_check(interaction.guild.get_member(user_id)):
                        interaction.response.send_message(
                            f"{self.config.emotes.fail} This user is on the staff team blacklist. Please speak to an Administrator."
                        )
                        return

                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Application Advanced by:", value=interaction.user.mention
                    )
                    await interaction.message.edit(embed=updated_form, view=None)

                    advance_embed = nextcord.Embed(
                        title="Your Community Engagement Application",
                        description="Your community engagement application has been advanced to the next steps. "
                        "Please contact the Community Engagement Team Lead on The Crossroads.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=advance_embed)

            case ["cet-application-reject", user_id]:
                if await permcheck(interaction, is_cet):
                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Application Rejected by:", value=interaction.user.mention
                    )
                    await interaction.message.edit(embed=updated_form, view=None)

                    rejection_embed = nextcord.Embed(
                        title="Your Community Engagement Application",
                        description="Your community engagement application has been rejected. Thanks for applying, "
                        "we encourage you to try again in the future.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=rejection_embed)

            case ["cet-application-review", user_id]:
                if await permcheck(interaction, is_cet):
                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Review notified by:", value=interaction.user.mention
                    )
                    accept_bttn = Button(
                        custom_id=f"cet-application-next-steps:{user_id}",
                        label="Move To Next Steps",
                        style=nextcord.ButtonStyle.green,
                    )
                    reject_bttn = Button(
                        custom_id=f"cet-application-reject:{user_id}",
                        label="Reject Application",
                        style=nextcord.ButtonStyle.red,
                    )
                    button_view = View(auto_defer=False)
                    button_view.add_item(accept_bttn)
                    button_view.add_item(reject_bttn)
                    await interaction.message.edit(embed=updated_form, view=button_view)

                    review_embed = nextcord.Embed(
                        title="Your Community Engagement Application",
                        description="Your community engagement application has been received and is now under "
                        "consideration. You will receive more information in the coming days.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=review_embed)

            case ["cet-application-start"]:
                await interaction.response.send_modal(CetAppModal(self.config))


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Applications(bot, kwargs["config"]))
