import random

import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal
from configutils import Configuration
from permutils import is_dark_mod, permcheck, is_senior_mod, is_cet, is_mod
from baseutils import SersiEmbed

from baseutils import SersiEmbed
from configutils import Configuration
from permutils import is_dark_mod, permcheck, is_senior_mod, is_cet, is_slt


class AdultAccessModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Over 18s Access")
        self.config = config

        self.whyjoin = nextcord.ui.TextInput(
            label="Why do you want access to the channel?",
            min_length=2,
            max_length=1024,
            required=True,
            style=nextcord.TextInputStyle.paragraph,
        )
        self.add_item(self.whyjoin)

        self.age = nextcord.ui.TextInput(
            label="How Old Are You", min_length=1, max_length=2, required=True
        )
        self.add_item(self.age)

        self.ageproof = nextcord.ui.TextInput(
            label="If required would you verify your age?",
            min_length=2,
            max_length=3,
            required=True,
        )
        self.add_item(self.ageproof)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        applicant_id: int = interaction.user.id

        # Age Checking
        # Input Verification
        if not self.age.value.isnumeric():
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Please make sure your age is an integer. Please try again.",
                ephemeral=True,
            )
            return

        # Parsing Age to Integer
        age_submitted: int = int(self.age.value)

        # Filtering Age
        if age_submitted == 69:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You're not 69.", ephemeral=True
            )
            return

        if age_submitted < 18:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You are not old enough to have access to the over 18's channels.",
                ephemeral=True,
            )
            young_embed = SersiEmbed(
                title="Underage Over 18s Application",
                description=f"User {interaction.user.name} ({interaction.user.id}) applied to access the Over 18s channels but entered an age of {self.age.value}.",
            )
            channel = interaction.client.get_channel(
                self.config.channels.ageverification
            )
            await channel.send(embed=young_embed)
            return

        # Filtering those that do not want to verify
        if self.ageproof.value.lower() in ["no", "na", "n/a", "non", "nee"]:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} As you are unwilling to verify your age your application has been automatically denied.",
                ephemeral=True,
            )
            refusal_embed = SersiEmbed(
                title="Over 18s Application Refusal to Verify",
                description=f"User {interaction.user.name} ({interaction.user.id}) applied to access the Over 18s channels but entered {self.ageproof.value} when asked if they would prove their age.",
            )
            channel = interaction.client.get_channel(
                self.config.channels.ageverification
            )
            await channel.send(embed=refusal_embed)
            return

        # Setting up Application Embed
        application_embed = SersiEmbed(
            title="Over 18s Channel Application",
            description=f"User {interaction.user.name} ({interaction.user.id})",
            fields={
                self.whyjoin.label: self.whyjoin.value,
                self.age.label: self.age.value,
                self.ageproof.label: self.ageproof.value,
            },
        )

        accept_button = Button(
            custom_id=f"adult-application-approve:{applicant_id}",
            label="Approve",
            style=nextcord.ButtonStyle.green,
        )
        reject_button = Button(
            custom_id=f"adult-application-reject:{applicant_id}",
            label="Reject",
            style=nextcord.ButtonStyle.red,
        )
        review_button = Button(
            custom_id=f"adult-application-verify:{applicant_id}",
            label="Require Proof",
            style=nextcord.ButtonStyle.grey,
        )

        button_view = View(auto_defer=False)
        button_view.add_item(accept_button)
        button_view.add_item(reject_button)
        button_view.add_item(review_button)

        channel = interaction.client.get_channel(self.config.channels.ageverification)
        await channel.send(embed=application_embed, view=button_view)


class AdultAccess(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    async def cb_open_adult_modal(self, interaction):
        await interaction.response.send_modal(AdultAccessModal(self.config))

    @commands.command()
    async def adult_access(self, ctx):
        """Single use Command for the 'Create Application' Embed"""
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        test_embed = SersiEmbed(
            title="Over 18's Channel",
            description="Press the button below to request access to the Over 18's Channel.",
        )
        open_modal = Button(
            custom_id="adult-channel-start",
            label="Request Access",
            style=nextcord.ButtonStyle.blurple,
        )
        open_modal.callback = self.cb_open_adult_modal

        button_view = View(timeout=None)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)

    @commands.command()
    async def adult_verified(self, ctx, member: nextcord.Member):
        """Marks a Member as having had their age verified"""
        if not await permcheck(ctx, is_senior_mod) and not await permcheck(ctx, is_cet):
            return

        adult_access_role = member.guild.get_role(self.config.roles.adult_access)
        adult_verified_role = member.guild.get_role(self.config.roles.adult_verified)
        await member.add_roles(
            adult_access_role,
            adult_verified_role,
            reason=f"Application Approved, verified by {ctx.author.name}",
            atomic=True,
        )

        accept_embed = nextcord.Embed(
            title="Over 18's Channel Application",
            description="Your request to join the Over 18's Channel has been approved. Thanks for verifying!",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        await member.send(embed=accept_embed)

    @commands.command()
    async def adult_bypass(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_dark_mod):
            return

        adult_access_role = member.guild.get_role(self.config.roles.adult_access)
        await member.add_roles(
            adult_access_role,
            reason=f"Application Approved, verified by {ctx.author.name}",
            atomic=True,
        )

        accept_embed = nextcord.Embed(
            title="Over 18's Channel Application",
            description="Your request to join the Over 18's Channel has been approved.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        await member.send(embed=accept_embed)

    @commands.command()
    async def adult_revoke(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_mod) and not await permcheck(ctx, is_cet):
            return

        adult_access_role = member.guild.get_role(self.config.roles.adult_access)
        adult_verified_role = member.guild.get_role(self.config.roles.adult_verified)
        try:
            await member.remove_roles(
                adult_access_role,
                adult_verified_role,
                reason=f"Adult Access Revoked by {ctx.author.name}",
                atomic=True,
            )

        except nextcord.HTTPException:
            await ctx.send(
                "Removing roles failed. Please request a Mega Administrator or Community Engagement Team member "
                "manually remove the roles."
            )

        revoke_embed = nextcord.Embed(
            title="Over 18's Channel Access Revoked",
            description="Your access to the Over 18's Channels have been revoked.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        await member.send(embed=revoke_embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["adult-channel-start"]:
                await interaction.response.send_modal(AdultAccessModal(self.config))

            case ["adult-application-approve", user_id]:
                if await permcheck(interaction, is_slt):
                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Application Approved by:", value=interaction.user.mention
                    )

                    random_number = random.randint(1, 100)
                    if 0 < random_number < 13:
                        updated_form.add_field(
                            name="Verification Required:",
                            value=f"{self.config.emotes.success} Yes",
                        )
                        verification_required = True
                    else:
                        updated_form.add_field(
                            name="Verification Required:",
                            value=f"{self.config.emotes.fail} No",
                        )
                        verification_required = False

                    await interaction.message.edit(embed=updated_form, view=None)

                    # if not random check
                    if not verification_required:
                        adult_role = interaction.guild.get_role(
                            self.config.roles.adult_access
                        )
                        await user.add_roles(
                            adult_role,
                            reason="Application Approved No Verification Required",
                            atomic=True,
                        )
                        accept_embed = nextcord.Embed(
                            title="Over 18's Channel Application",
                            description="Your request to join the Over 18's Channel has been approved.",
                            colour=nextcord.Color.from_rgb(237, 91, 6),
                        )
                        await user.send(embed=accept_embed)

                    # if random check
                    else:
                        verify_embed = nextcord.Embed(
                            title="Over 18's Channel Application",
                            description="Your request to join the Over 18's Channel has been referred. You have been "
                            "randomly selected to verify your age. Please create a Senior Moderator or "
                            "Mega Administrator ticket. You will be required to submit an image which "
                            "comprises of the following:\nPaper which has your discord name and "
                            "discriminator written on it\nAdam Something Central written on it\nThe date "
                            "in DD.MM.YYYY format\nA photo ID placed on the paper. **Blank out everything "
                            "except the date of birth. We do not want or need to see anything other than "
                            "the date of birth.** Ensure all four corners of the ID are visible.\n\n If "
                            "you do not wish to submit photo ID then consider your application rejected.",
                            colour=nextcord.Color.from_rgb(237, 91, 6),
                        )
                        await user.send(embed=verify_embed)

            case ["adult-application-reject", user_id]:
                if await permcheck(interaction, is_slt):
                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Application Rejected by:", value=interaction.user.mention
                    )
                    await interaction.message.edit(embed=updated_form, view=None)

                    deny_embed = nextcord.Embed(
                        title="Over 18's Channel Application",
                        description="Your request to join the Over 18's Channel has been denied. Want to know more? "
                        "Create a Senior Moderator Ticket.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=deny_embed)

            case ["adult-application-verify", user_id]:
                if await permcheck(interaction, is_slt):
                    user = interaction.guild.get_member(int(user_id))

                    updated_form = interaction.message.embeds[0]
                    updated_form.add_field(
                        name="Verification Requested by:",
                        value=interaction.user.mention,
                    )
                    await interaction.message.edit(embed=updated_form, view=None)

                    referred_embed = nextcord.Embed(
                        title="Over 18's Channel Application",
                        description="Your request to join the Over 18's Channel has been referred. You have been "
                        "randomly selected to verify your age. Please create a Senior Moderator or Mega "
                        "Administrator ticket. You will be required to submit an image which comprises of "
                        "the following:\nPaper which has your discord name and discriminator written on "
                        "it\nAdam Something Central written on it\nThe date in DD.MM.YYYY format\nA photo "
                        "ID placed on the paper. **Blank out everything except the date of birth. We do "
                        "not want or need to see anything other than the date of birth.** Ensure all four "
                        "corners of the ID are visible.\n\n If you do not wish to submit photo ID then "
                        "consider your application rejected.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=referred_embed)


def setup(bot, **kwargs):
    bot.add_cog(AdultAccess(bot, kwargs["config"]))
