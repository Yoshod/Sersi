import random
from datetime import datetime, date, timedelta

import nextcord
import pytz
from nextcord.ext import commands
from nextcord.ui import Button, View, Modal
from utils.cases import get_last_warning, create_case_embed, fetch_cases_by_partial_id
from utils.database import db_session, BlacklistCase, WarningCase, RelatedCase
from utils.dialog import confirm, ButtonPreset
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.perms import (
    is_cet,
    is_admin,
    is_mod,
    is_mod_lead,
    is_slt,
    is_staff,
    permcheck,
    blacklist_check,
)

from utils.whois import create_whois_embed, WhoisView


class AdultAccessApproveButton(Button):
    def __init__(self, user_id: int):
        super().__init__(
            custom_id=f"adult-application-approve:{user_id}",
            label="Approve",
            style=nextcord.ButtonStyle.green,
        )


class AdultAccessRejectButton(Button):
    def __init__(self, user_id: int):
        super().__init__(
            custom_id=f"adult-application-reject:{user_id}",
            label="Reject",
            style=nextcord.ButtonStyle.red,
        )


class AdultAccessVerifyButton(Button):
    def __init__(self, user_id: int):
        super().__init__(
            custom_id=f"adult-application-verify:{user_id}",
            label="Require Proof",
            style=nextcord.ButtonStyle.grey,
        )


class AdultAccessWhoisButton(Button):
    def __init__(self, user_id: int):
        super().__init__(
            custom_id=f"adult-application-whois:{user_id}",
            label="Whois",
            style=nextcord.ButtonStyle.blurple,
            row=1,
        )


class AdultAccessView(View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(AdultAccessApproveButton(user_id))
        self.add_item(AdultAccessRejectButton(user_id))
        self.add_item(AdultAccessVerifyButton(user_id))
        self.add_item(AdultAccessWhoisButton(user_id))


class AdultAccessModal(Modal):
    def __init__(self, config: Configuration):
        super().__init__("Over 18s Access")
        self.config = config

        self.whyjoin = nextcord.ui.TextInput(
            label="Why do you want access to the channel?",
            min_length=10,
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

    async def callback(self, interaction: nextcord.Interaction):
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
                description=f"User {interaction.user.mention} ({interaction.user.id}) applied to access the Over 18s "
                f"channels but entered an age of {self.age.value}.",
                footer="Sersi Adult Verification",
            )
            channel = interaction.client.get_channel(
                self.config.channels.ageverification
            )
            await channel.send(embed=young_embed)
            return

        # Filtering those that do not want to verify
        if self.ageproof.value.lower() in ["no", "na", "n/a", "non", "nee"]:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} As you are unwilling to verify your age your application has been "
                f"automatically denied.",
                ephemeral=True,
            )
            refusal_embed = SersiEmbed(
                title="Over 18s Application Refusal to Verify",
                description=f"User {interaction.user.mention} ({interaction.user.id}) applied to access the Over 18s "
                f"channels but entered {self.ageproof.value} when asked if they would prove their age.",
                footer="Sersi Adult Verification",
            )
            channel = interaction.client.get_channel(
                self.config.channels.ageverification
            )
            await channel.send(embed=refusal_embed)
            return

        # Setting up Application Embed
        application_embed = SersiEmbed(
            title="Over 18s Channel Application",
            description=f"User {interaction.user.mention} ({interaction.user.id})",
            fields={
                self.whyjoin.label: self.whyjoin.value,
                self.age.label: self.age.value,
                self.ageproof.label: self.ageproof.value,
            },
        )

        button_view = AdultAccessView(user_id=applicant_id)

        channel = interaction.client.get_channel(self.config.channels.ageverification)
        await channel.send(embed=application_embed, view=button_view)


class AdultAccess(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command(name="adultaccess")
    async def adult_access_embed(self, ctx: commands.Context):
        """Single use Command for the 'Create Application' Embed."""
        if not await permcheck(ctx, is_admin):
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

        button_view = View(auto_defer=False)
        button_view.add_item(open_modal)

        await ctx.send(embed=test_embed, view=button_view)

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Used to handle access to the adult only channels",
    )
    async def adult_access(self, interaction: nextcord.Interaction):
        pass

    @adult_access.subcommand(
        name="bypass",
        description="Used to bypass verification to the adult only channels",
    )
    async def adult_bypass(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member,
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for bypassing user",
            min_length=10,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)
        adult_access_role = user.guild.get_role(self.config.roles.adult_access)
        await user.add_roles(
            adult_access_role,
            reason=f"Application Approved, verified by {interaction.user.name}",
            atomic=True,
        )

        logging_embed = SersiEmbed(
            title="Over 18 Access Bypassed",
            description=f"Member {user.mention} ({user.id}) was bypassed from verifying their age by "
            f"{interaction.user.mention}",
            fields={"Reason:": reason},
            footer="Sersi Adult Verification",
        )

        logging_embed.timestamp = datetime.now(pytz.UTC)
        logging_channel = interaction.guild.get_channel(self.config.channels.logging)
        await logging_channel.send(embed=logging_embed)

        accept_embed = nextcord.Embed(
            title="Over 18's Channel Application",
            description="Your request to join the Over 18's Channel has been approved.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        await user.send(embed=accept_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} User has received access to the Over 18s channels."
        )

    @adult_access.subcommand(
        name="revoke",
        description="Used to revoke a user's access to the adult channels and blacklist them from applying again",
    )
    async def adult_revoke(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for revoking access",
            min_length=10,
            max_length=1024,
        ),
        related_warning: str = nextcord.SlashOption(
            name="related_warning",
            description="The ID of the warning case related to revocation of access",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if is_staff(member):
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You cannot revoke access from a staff member.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        if not blacklist_check(member, "Adult Only Access"):
            with db_session() as session:
                case = BlacklistCase(
                    offender=member.id,
                    moderator=interaction.user.id,
                    blacklist="Adult Only Access",
                    reason=reason,
                )
                session.add(case)

                if related_warning is not None:
                    if (
                        not session.query(WarningCase)
                        .filter_by(id=related_warning)
                        .first()
                    ):
                        await interaction.followup.send(
                            f"{self.config.emotes.fail} {related_warning} is not a valid warning case."
                        )
                        return
                elif last_warning := get_last_warning(member.id):
                    # If the last warning was issued within the last 15 minutes, ask user if the warning is related
                    if last_warning.created > datetime.utcnow() - timedelta(minutes=15):
                        if await confirm(
                            interaction,
                            content=f"Recent warning found for {member.mention}. Is it related?",
                            embed=create_case_embed(
                                last_warning,
                                interaction=interaction,
                                config=self.config,
                            ),
                            true_button=ButtonPreset.YES_PRIMARY,
                            false_button=ButtonPreset.NO_NEUTRAL,
                            ephemeral=True,
                        ):
                            related_warning = last_warning.id

                if related_warning is not None:
                    session.add(
                        RelatedCase(
                            case_id=related_warning,
                            related_id=case.id,
                        )
                    )

                session.commit()

            await interaction.followup.send(
                f"{self.config.emotes.success} User has been blacklisted from applying to the Over 18s channels.",
                ephemeral=True,
            )

        adult_access_role: nextcord.Role = member.guild.get_role(
            self.config.roles.adult_access
        )
        adult_verified_role: nextcord.Role = member.guild.get_role(
            self.config.roles.adult_verified
        )

        if adult_access_role not in member.roles:
            await interaction.followup.send(
                f"{self.config.emotes.fail} User does not have access to the Over 18s channels.",
                ephemeral=True,
            )
            return

        try:
            await member.remove_roles(
                adult_access_role,
                adult_verified_role,
                reason=f"Adult Access Revoked by {interaction.user.name}",
                atomic=True,
            )
        except nextcord.HTTPException:
            await interaction.followup.send(
                f"{self.config.emotes.fail} Removing roles failed. Please request an Administrator or "
                f"Community Engagement Team member to manually remove the roles.",
                ephemeral=True,
            )
            return

        logging_embed = SersiEmbed(
            title="Over 18 Access Revoked",
            description=f"Member {member.mention} ({member.id}) has had their access to the over 18 channels revoked by "
            f"{interaction.user.mention}",
            fields={"Reason:": reason},
            footer="Sersi Adult Verification",
            author=interaction.user,
        )
        logging_channel = interaction.guild.get_channel(self.config.channels.logging)
        await logging_channel.send(embed=logging_embed)

        revoke_embed = nextcord.Embed(
            title="Over 18's Channel Access Revoked",
            description="Your access to the Over 18's Channels have been revoked.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        await member.send(embed=revoke_embed)
        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} no longer has access to any 18+ channels."
        )

    @adult_access.subcommand(
        name="blacklist_remove",
        description="Used to remove a user from the blacklist",
    )
    async def adult_blacklist_remove(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member,
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for removing user from blacklist",
            min_length=10,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod_lead):
            return

        if not blacklist_check(user, "Adult Only Access"):
            await interaction.response.send_message(
                f"{self.config.emotes.fail} User is not blacklisted.",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        with db_session(interaction.user) as session:
            case: BlacklistCase = (
                session.query(BlacklistCase)
                .filter_by(offender=user.id, active=True, blacklist="Adult Only Access")
                .first()
            )

            case.active = False
            case.removed_by = interaction.user.id
            case.removal_reason = reason
            session.commit()

        logging_embed = SersiEmbed(
            title="Over 18 Access Blacklist Removed",
            description=f"Member {user.mention} ({user.id}) has been removed from the blacklist by "
            f"{interaction.user.mention}",
            fields={"Reason:": reason},
            footer="Sersi Adult Verification",
            author=interaction.user,
        )
        logging_channel = interaction.guild.get_channel(self.config.channels.logging)
        await logging_channel.send(embed=logging_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} User has been removed from the blacklist."
        )

    @adult_access.subcommand(
        name="verify",
        description="Used to verify a user as an adult",
    )
    async def adult_verify(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member,
        dd: int = nextcord.SlashOption(
            name="dd",
            description="The day portion of the date of birth",
            required=True,
            min_value=1,
            max_value=31,
        ),
        mm: int = nextcord.SlashOption(
            name="mm",
            description="The month portion of the date of birth",
            required=True,
            min_value=1,
            max_value=12,
        ),
        yyyy: int = nextcord.SlashOption(
            name="yyyy",
            description="The year portion of the date of birth",
            required=True,
            min_value=1950,
            max_value=datetime.now().year,
        ),
    ):
        if not await permcheck(interaction, is_mod_lead) and not await permcheck(
            interaction, is_cet
        ):
            return

        date_of_birth: str = f"{dd}{mm}{yyyy}"

        try:
            birthdate = datetime.strptime(date_of_birth, "%d%m%Y").date()
        except ValueError:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Date of Birth not valid. Please try again or contact CET or a Administrator",
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True)

        today = date.today()

        age = (
            today.year
            - birthdate.year
            - ((today.month, today.day) < (birthdate.month, birthdate.day))
        )

        if age >= 18:
            adult_access_role = user.guild.get_role(self.config.roles.adult_access)
            adult_verified_role = user.guild.get_role(self.config.roles.adult_verified)
            await user.add_roles(
                adult_access_role,
                adult_verified_role,
                reason=f"Application Approved, verified by {interaction.user.name}",
                atomic=True,
            )

            logging_embed = SersiEmbed(
                title="Over 18 Verified",
                description=f"Member {user.mention} ({user.id}) has successfully verified they're above the age of 18.\n",
                fields={
                    "Verified By:": f"{interaction.user.mention} ({interaction.user.id})"
                },
            )
            logging_embed.timestamp = datetime.now(pytz.UTC)
            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )
            await logging_channel.send(embed=logging_embed)

            accept_embed = nextcord.Embed(
                title="Over 18's Channel Application",
                description="Your request to join the Over 18's Channel has been approved. Thanks for verifying!",
                colour=nextcord.Color.from_rgb(237, 91, 6),
            )
            await user.send(embed=accept_embed)

            await interaction.followup.send(
                f"{self.config.emotes.success} User {user.mention} ({user.id}) is {age} and is allowed access. The required roles have been successfully given to the user."
            )

        else:
            await interaction.followup.send(
                f"{self.config.emotes.fail} User {user.mention} ({user.id}) is {age} and is not allowed access."
            )

    @adult_revoke.on_autocomplete("related_warning")
    async def search_warnings(
        self,
        interaction: nextcord.Interaction,
        related_warning: str,
        offender: nextcord.Member,
    ):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        warnings: list[str] = fetch_cases_by_partial_id(
            related_warning, type="Warning", offender=offender.id
        )
        await interaction.response.send_autocomplete(warnings)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["adult-channel-start"]:
                if blacklist_check(interaction.user, "Adult Only Access"):
                    await interaction.response.send_message(
                        f"{self.config.emotes.fail} You have been blacklisted from applying to the Over 18's channels.",
                        ephemeral=True,
                    )
                    return

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
                            inline=False,
                        )
                        verification_required = True
                    else:
                        updated_form.add_field(
                            name="Verification Required:",
                            value=f"{self.config.emotes.fail} No",
                            inline=False,
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

                        logging_embed = SersiEmbed(
                            title="Over 18 Access Given",
                            description=f"Member {user.mention} ({user.id}) was was given 18+ access by "
                            f"{interaction.user.mention} ({interaction.user.id})",
                            footer="Sersi Adult Verification",
                        )
                        logging_embed.timestamp = datetime.now(pytz.UTC)
                        logging_channel = interaction.guild.get_channel(
                            self.config.channels.logging
                        )
                        await logging_channel.send(embed=logging_embed)

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
                            "randomly selected to verify your age. Please create a Moderation Lead or "
                            "Administrator ticket. You will be required to submit an image which "
                            "comprises of the following:\n"
                            "Paper which has your discord name and discriminator written on it\n"
                            "The Crossroads written on it\n"
                            "The date in DD.MM.YYYY format\n"
                            "A photo ID placed on the paper. **Blank out everything except the date of birth. We do "
                            "not want or need to see anything other than the date of birth.** Ensure all four corners "
                            "of the ID are visible.\n"
                            "\n"
                            "If you do not wish to submit photo ID then consider your application rejected.",
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
                        "Create a Moderation Lead Ticket.",
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
                        "randomly selected to verify your age. Please create a Moderation Lead or "
                        "Administrator ticket. You will be required to submit an image which comprises of "
                        "the following:\n"
                        "Paper which has your discord name and discriminator written on it\n"
                        "The Crossroads written on it\n"
                        "The date in DD.MM.YYYY format\n"
                        "A photo ID placed on the paper. **Blank out everything except the date of birth. We do "
                        "not want or need to see anything other than the date of birth.** Ensure all four "
                        "corners of the ID are visible.\n"
                        "\n"
                        "If you do not wish to submit photo ID then consider your application rejected.",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    await user.send(embed=referred_embed)

            case ["adult-application-whois", user_id]:
                if await permcheck(interaction, is_mod):
                    user = interaction.guild.get_member(int(user_id))
                    await interaction.response.defer(ephemeral=True)
                    await interaction.followup.send(
                        embed=await create_whois_embed(self.config, interaction, user),
                        view=WhoisView(user.id),
                        ephemeral=True,
                    )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(AdultAccess(bot, kwargs["config"]))
