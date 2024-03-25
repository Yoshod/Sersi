import calendar
from datetime import datetime, timedelta, date
import os
import nextcord
from nextcord import SlashOption
from nextcord.ext import commands, tasks
from nextcord.utils import format_dt
import sqlalchemy

from utils.base import (
    decode_button_id,
    encode_snowflake,
    decode_snowflake,
    convert_to_timedelta,
    ignored_message,
)
from utils.sersi_embed import SersiEmbed
from utils.views import ConfirmView, DualCustodyView
from utils.config import Configuration
from utils.dialog import confirm, ButtonPreset
from utils.perms import (
    is_mod,
    permcheck,
    is_staff,
    is_mod_lead,
    is_slt,
    is_admin,
    is_cet_lead,
    blacklist_check,
    is_trial_mod,
)
from utils.database import (
    db_session,
    BlacklistCase,
    CaseApproval,
    VoteDetails,
    VoteRecord,
    TrialModReviews,
    ModerationRecords,
    StaffMembers,
    ModeratorAvailability,
)
from utils.voting import VoteView, vote_planned_end
from utils.staff import (
    StaffRole,
    Branch,
    add_staff_to_db,
    staff_retire,
    RemovalType,
    staff_branch_change,
    transfer_validity_check,
    determine_transfer_type,
    get_staff_embed,
    get_moderation_embed,
    determine_staff_member,
    add_mod_record,
    mentor_check,
    add_staff_legacy,
    add_mod_record_legacy,
    promotion_validity_check,
    set_availability_status,
    check_staff_availability,
    is_available,
)

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

grandparent_dir = os.path.dirname(parent_dir)

config_path = os.path.join(grandparent_dir, "persistent_data/config.yaml")

CONFIG = Configuration.from_yaml_file(config_path)


class Staff(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        if self.bot.is_ready():
            self.check_availability.start()

    def cog_unload(self):
        self.check_availability.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.check_availability.start()

    async def remove_all_permission_roles(self, member: nextcord.Member):
        for role in vars(self.config.permission_roles):
            role_object: nextcord.Role = member.guild.get_role(
                vars(self.config.permission_roles)[role]
            )
            if role_object is None:
                continue
            try:
                await member.remove_roles(role_object)
            except nextcord.errors.HTTPException:
                continue

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def staff(self, interaction: nextcord.Interaction):
        pass

    @staff.subcommand(name="add")
    async def add_to_staff(self, interaction: nextcord.Interaction):
        pass

    @staff.subcommand(name="remove")
    async def remove_from_staff(self, interaction: nextcord.Interaction):
        pass

    @staff.subcommand(name="blacklist")
    async def blacklist(self, interaction: nextcord.Interaction):
        pass

    @add_to_staff.subcommand(
        description="Makes a server member a Trial Moderator",
    )
    async def trial_moderator(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to make a Trial Moderator"
        ),
        mentor: nextcord.Member = SlashOption(
            description="Mentor for the new Trial Moderator"
        ),
    ):
        if not await permcheck(interaction, is_mod_lead):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is blacklisted from the Staff Team. Speak to an Administrator."
            )
            return

        try:
            if (
                not determine_staff_member(mentor.id).branch == Branch.MOD.value
                and not determine_staff_member(mentor.id).branch == Branch.ADMIN.value
            ):
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} The mentor is not on the Moderation Team."
                )
                return

        except AttributeError:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} The mentor is not on the Staff Team."
            )
            return

        if member.id == mentor.id:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} A trial moderator cannot mentor themselves."
            )
            return

        trial_moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.trial_moderator
        )
        staff: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.staff
        )
        await member.add_roles(trial_moderator, reason="Sersi command", atomic=True)
        await member.add_roles(staff, reason="Sersi command", atomic=True)

        await interaction.send(
            f"{self.config.emotes.success} {member.mention} was given the {trial_moderator.name} role."
        )

        # logging
        add_staff_to_db(member.id, Branch.MOD, StaffRole.TRIAL_MOD, interaction.user.id)
        add_mod_record(member.id, mentor.id)

        log_embed = SersiEmbed(
            title="New Trial Moderator added.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                f"New {trial_moderator.name}:": member.mention,
            },
            footer="Sersi Add Trial Mod",
        ).set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @add_to_staff.subcommand(
        description="Promotes a Trial Moderator to Moderator",
    )
    async def promote(self, interaction: nextcord.Interaction, member: nextcord.Member):
        if not permcheck(interaction, is_mod_lead):
            return

        await interaction.response.defer()

        if not promotion_validity_check(member.id):
            await interaction.followup.send(
                f"{self.config.emotes.fail} This user has not met the criteria to be promoted to a Moderator."
            )
            return

        trial_moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.trial_moderator
        )
        moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.moderator
        )

        if trial_moderator not in member.roles:
            await interaction.followup.send(
                f"{self.config.emotes.fail} Moderators need to be trial modertors first"
            )
            return

        await member.remove_roles(trial_moderator, reason="Sersi command", atomic=True)
        await member.add_roles(moderator, reason="Sersi command", atomic=True)

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} was given the {moderator.name} role.\n"
            "Remember: You're not truly a moderator until your first ban. ;)",
        )

        # logging
        log_embed = SersiEmbed(
            title="Trial Moderator matured into a full Moderator.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                "New Moderator:": member.mention,
            },
            footer="Sersi Add Trial Mod",
        ).set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @add_to_staff.subcommand(description="Reinstates a retired Moderator")
    async def reinstate_moderator(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        if not permcheck(interaction, is_mod_lead):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is blacklisted from the Staff Team. Speak to an Administrator."
            )
            return

        honourable_member: nextcord.Role = interaction.guild.get_role(
            self.config.roles.honourable_member
        )
        moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.moderator
        )
        staff: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.staff
        )

        if honourable_member not in member.roles:
            await interaction.followup.send(
                f"{self.config.emotes.fail} This user is not an Honourable Member and therefore cannot be reinstated as a Moderator."
            )
            return

        await interaction.response.defer()

        await member.remove_roles(
            honourable_member, reason="Sersi command", atomic=True
        )
        await member.add_roles(moderator, reason="Sersi command", atomic=True)
        await member.add_roles(staff, reason="Sersi command", atomic=True)

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} was given the {moderator.name} role.\n"
            "Welcome back to the team! :)",
        )

        # logging
        log_embed = SersiEmbed(
            title="Honourable Member reinstated as a Moderator.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                "New Moderator:": member.mention,
            },
            footer="Sersi Add Trial Mod",
            author=interaction.user,
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )
        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @add_to_staff.subcommand(description="Adds a new member to the CE-Team")
    async def community_engagement(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        if not permcheck(interaction, is_cet_lead):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is blacklisted from the Staff Team. Speak to an Administrator."
            )
            return

        cet: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.cet
        )
        staff: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.staff
        )
        await member.add_roles(cet, reason="Sersi command", atomic=True)
        await member.add_roles(staff, reason="Sersi command", atomic=True)

        await interaction.send(
            f"{self.config.emotes.success} {member.mention} was given the {cet.name} role."
        )

        # logging
        log_embed = SersiEmbed(
            title="New CE-Team Member added.",
            fields={
                "Responsible CETL:": interaction.user.mention,
                f"New {cet.name}:": member.mention,
            },
            footer="Sersi Add CET Mod",
        ).set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

    @add_to_staff.subcommand(description="Transfer a staff member to another branch")
    async def transfer(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        branch: str = SlashOption(
            description="Branch to transfer the member to",
            choices={
                "Administration": "Administration",
                "Moderation": "Moderation",
                "Community Engagement Team": "Community Engagement Team",
            },
        ),
        role: str = SlashOption(
            description="Role to assign to the member",
            choices={
                "Administrator": "Administrator",
                "Compliance Officer": "Compliance Officer",
                "Moderation Lead": "Moderation Lead",
                "Moderator": "Moderator",
                "Trial Moderator": "Trial Moderator",
                "CET Lead": "Community Engagement Team Lead",
                "CET": "Community Engagement Team Member",
            },
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer()

        branches = {
            "Administration": Branch.ADMIN,
            "Moderation": Branch.MOD,
            "Community Engagement Team": Branch.CET,
        }

        roles = {
            "Administrator": StaffRole.ADMIN,
            "Compliance Officer": StaffRole.COMPLIANCE,
            "Moderation Lead": StaffRole.HEAD_MOD,
            "Moderator": StaffRole.MOD,
            "Trial Moderator": StaffRole.TRIAL_MOD,
            "Community Engagement Team Lead": StaffRole.CET_LEAD,
            "Community Engagement Team Member": StaffRole.CET,
        }

        if not transfer_validity_check(member.id, branches[branch]):
            interaction.followup.send(
                f"{self.config.emotes.fail} The user is already in the specified branch or is not a staff member."
            )
            return

        transfer_type = determine_transfer_type(member.id, branches[branch])

        staff_branch_change(
            member.id, branches[branch], roles[role], interaction.user.id
        )

        match transfer_type:
            case "mod_to_cet":
                await member.add_roles(
                    interaction.guild.get_role(self.config.permission_roles.cet)
                )

                try:
                    await member.remove_roles(
                        interaction.guild.get_role(
                            self.config.permission_roles.moderator
                        )
                    )
                except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                    pass

                try:  # remove trial mod role
                    await member.remove_roles(
                        interaction.guild.get_role(
                            self.config.permission_roles.trial_moderator
                        )
                    )

                except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                    pass

                try:  # remove moderation lead role
                    await member.remove_roles(
                        interaction.guild.get_role(
                            self.config.permission_roles.senior_moderator
                        )
                    )

                except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                    pass

            case "cet_to_mod":
                await member.add_roles(
                    interaction.guild.get_role(self.config.permission_roles.moderator)
                )

                try:
                    await member.remove_roles(
                        interaction.guild.get_role(self.config.permission_roles.cet)
                    )
                except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                    pass

                try:  # remove cet lead role
                    await member.remove_roles(
                        interaction.guild.get_role(
                            self.config.permission_roles.cet_lead
                        )
                    )

                except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                    pass

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} has been transferred to the {branch} branch."
        )

        # logging
        log_embed: nextcord.Embed = SersiEmbed(
            title="Staff member has been transferred.",
            fields={
                "Responsible Administrator:": interaction.user.mention,
                "Transferred Staff Member:": member.mention,
                "New Branch:": branches[branch].value,
                "New Role:": roles[role].value,
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @remove_from_staff.subcommand(
        description="Discharge from Server Staff.",
    )
    async def discharge(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            required=True,
            description="User you wish to discharge and blacklist from Server Staff",
        ),
        reason: str = SlashOption(
            required=True,
            description="Reason for discharging the user;",
            min_length=8,
            max_length=1024,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="ADMINISTRATOR ONLY! Reason to bypass dual custody",
            min_length=8,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_slt):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is already blacklisted from the staff team."
            )
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
            await self.remove_all_permission_roles(member)

            staff_retire(
                member, RemovalType.REMOVED_BAD_STANDING, interaction.user.id, reason
            )

            embed_fields = {
                "Discharged Member:": member.mention,
                "Reason:": reason,
                "Responsible Member:": interaction.user.mention,
            }
            if bypass_reason and is_admin(interaction.user):
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

            with db_session(interaction.user) as session:
                case: BlacklistCase = BlacklistCase(
                    offender=member.id,
                    moderator=interaction.user.id,
                    blacklist="Staff",
                    reason=reason,
                )
                session.add(case)

                if confirming_moderator != interaction.user:
                    session.add(
                        CaseApproval(
                            case_id=case.id,
                            approver=confirming_moderator.id,
                            approved=True,
                        )
                    )
                session.commit()

        await execute(self.bot, self.config, interaction)

    @remove_from_staff.subcommand(
        description="Used to Retire from the staff team",
    )
    async def retire(
        self,
        interaction: nextcord.Interaction,
        reason: str = SlashOption(
            required=True,
            description="Reason for retiring from the staff team;",
            min_length=8,
            max_length=1024,
        ),
        member: nextcord.Member = SlashOption(
            required=False,
            description="Who to retire; Specify yourself to retire yourself.",
        ),
    ):
        if member is None:
            member = interaction.user

        if member == interaction.user:
            if not await permcheck(interaction, is_staff):
                return
        else:
            if not await permcheck(interaction, is_slt):
                return

        await interaction.response.defer()

        await self.remove_all_permission_roles(member)

        staff_retire(member, RemovalType.RETIRE, interaction.user.id, reason)

        try:
            await member.add_roles(
                interaction.guild.get_role(self.config.roles.honourable_member)
            )
        except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
            pass

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} has retired from the mod team. Thank you for your service!"
        )

        # logging
        log_embed: nextcord.Embed = SersiEmbed(
            title="Moderator has (been) retired.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                "Retired Moderator:": member.mention,
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @blacklist.subcommand(description="Add a user to the Staff Blacklist")
    async def add(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Who to blacklist.",
        ),
        reason: str = SlashOption(
            description="The reason you are blacklisting this user."
        ),
    ):
        if not await permcheck(interaction, is_slt):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is already blacklisted from the Staff Team."
            )

        if member == interaction.user:
            interaction.response.send_message(
                f"{self.config.emotes.fail} You cannot blacklist yourself."
            )
            return

        interaction.response.defer()

        with db_session(interaction.user) as session:
            case: BlacklistCase = BlacklistCase(
                offender=member.id,
                moderator=interaction.user.id,
                blacklist="Staff",
                reason=reason,
            )
            session.add(case)
            session.commit()

        interaction.followup.send(
            f"{self.config.emotes.success} The user has now been blacklisted from the Staff Team."
        )
        return

    @blacklist.subcommand(description="Remove a user to the Staff Blacklist")
    async def remove(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Who to blacklist.",
        ),
        reason: str = SlashOption(
            description="The reason you are removing this user from the blacklist."
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        if not blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is not on the Staff Team blacklist."
            )

        interaction.response.defer()

        with db_session(interaction.user) as session:
            case: BlacklistCase = (
                session.query(BlacklistCase)
                .filter_by(offender=member.id, active=True, blacklist="Staff")
                .first()
            )
            case.active = False
            case.removed_by = interaction.user.id
            case.removal_reason = reason
            session.commit()

        interaction.followup.send(
            f"{self.config.emotes.success} The user is no longer blacklisted from the Staff Team."
        )
        return

    @staff.subcommand(
        description="Revoke a user's Honourable Member status and blacklist them from the Staff Team"
    )
    async def revoke_honoured_member(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to revoke Honourable Member status from",
        ),
        reason: str = SlashOption(
            description="Reason for revoking Honourable Member status",
            min_length=10,
            max_length=1024,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="ADMINISTRATOR ONLY! Reason to bypass vote",
            min_length=10,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        honourable_member: nextcord.Role = interaction.guild.get_role(
            self.config.roles.honourable_member
        )

        if honourable_member not in member.roles:
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is not an Honourable Member."
            )
            return

        if blacklist_check(member):
            member.remove_roles(
                honourable_member, reason="Blacklisted from staff", atomic=True
            )
            interaction.response.send_message(
                f"{self.config.emotes.success} This user is already blacklisted from the Staff Team"
                " and has been removed from the Honourable Member role immediately."
            )
            return

        interaction.response.defer(ephemeral=True)

        if bypass_reason and permcheck(interaction, is_admin):
            await member.remove_roles(
                honourable_member, reason="Blacklisted from staff", atomic=True
            )
            interaction.followup.send(
                f"{self.config.emotes.success} {member.mention} has been removed from the Honourable Member role."
            )

            # logging
            log_embed = SersiEmbed(
                title="Honoured Member status revoked.",
                fields={
                    "Responsible Administrator:": interaction.user.mention,
                    "Removed Honoured Member:": member.mention,
                    "Reason:": reason,
                    "Bypass Reason:": bypass_reason,
                },
            ).set_author(
                name=interaction.user, icon_url=interaction.user.display_avatar.url
            )

            await interaction.guild.get_channel(self.config.channels.logging).send(
                embed=log_embed
            )
            await interaction.guild.get_channel(self.config.channels.mod_logs).send(
                embed=log_embed
            )

            return

        # start the vote to revoke honoured member role
        vote_embed = SersiEmbed(
            title=f"Revoke Honourable Member Status of {member.name}",
            description=f"{member.mention} has been nominated to have their Honourable Member status revoked. \n"
            f"__Reason stated by {interaction.user.mention}:__ \n\n{reason}",
            author=interaction.user,
        )

        vote_channel = self.config.channels.staff_votes

        vote_message = await interaction.guild.get_channel(vote_channel).send(
            embed=vote_embed
        )

        vote_type = self.config.voting["honour-revoke"]
        with db_session(interaction.user) as session:
            case: BlacklistCase = BlacklistCase(
                id=encode_snowflake(interaction.id),
                offender=member.id,
                moderator=interaction.user.id,
                active=False,
                blacklist="Staff",
                reason=reason,
                scrubbed=True,
            )
            session.add(case)

            vote: VoteDetails = VoteDetails(
                vote_type="honour-revoke",
                vote_url=vote_message.jump_url,
                case_id=case.id,
                started_by=interaction.user.id,
                planned_end=vote_planned_end(vote_type),
            )
            session.add(vote)
            session.commit()

            await vote_message.edit(view=VoteView(vote_type, vote))

        await interaction.followup.send(
            f"{self.config.emotes.success} Vote to revoke Honourable Member status has been started."
        )

    @staff.subcommand(description="Complete a weekly review for a trial moderator")
    async def trial_mod_review(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to review",
        ),
        review_type: str = SlashOption(
            description="Type of review",
            choices=[
                "First Review",
                "Second Review",
                "Third Review",
                "Fourth Review",
                "Fifth Review",
                "Sixth Review",
            ],
        ),
        outcome: bool = SlashOption(
            description="Outcome of the review",
            choices={"Passed": True, "Failed": False},
        ),
        comment: str = SlashOption(
            description="Comments on the review",
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if not determine_staff_member(member.id).role == StaffRole.TRIAL_MOD.value:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} This user is not a Trial Moderator."
            )
            return

        if not mentor_check(member.id, interaction.user.id):
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You are not the mentor of this user."
            )
            return

        interaction.response.defer(ephemeral=True)

        try:
            with db_session(interaction.user) as session:
                record_review = TrialModReviews(
                    member=member.id,
                    review_type=review_type,
                    review_passed=outcome,
                    review_comment=comment,
                    reviewer=interaction.user.id,
                )
                session.add(record_review)
                session.commit()

        except sqlalchemy.exc.IntegrityError:
            await interaction.followup.send(
                f"{self.config.emotes.fail} This user has already had a {review_type} review."
            )
            return

        await interaction.followup.send(
            f"{self.config.emotes.success} Review has been recorded."
        )

        review_embed = SersiEmbed(
            title=f"Trial Mod Review: {review_type}",
            description=f"Your {review_type} review has been completed by {interaction.user.mention}.",
            fields={
                "Outcome:": f"{'Passed' if outcome else 'Failed'}",
                "Comments:": comment,
            },
        )

        await member.send(embed=review_embed)

    @add_to_staff.subcommand(description="Add legacy staff member to the database")
    async def legacy_staff(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to add to the database",
        ),
        branch: str = SlashOption(
            description="Branch the member was in",
            choices=["Administration", "Moderation", "Community Engagement Team"],
        ),
        role: str = SlashOption(
            description="Role the member had",
            choices={
                "Administrator": str(CONFIG.permission_roles.dark_moderator),
                "Compliance Officer": str(CONFIG.permission_roles.compliance),
                "Moderation Lead": str(CONFIG.permission_roles.senior_moderator),
                "Moderator": str(CONFIG.permission_roles.moderator),
                "Trial Moderator": str(CONFIG.permission_roles.trial_moderator),
                "CET Lead": str(CONFIG.permission_roles.cet_lead),
                "CET": str(CONFIG.permission_roles.cet),
            },
        ),
        added_by: nextcord.Member = SlashOption(
            description="Who added the member to the database",
        ),
        mentor: nextcord.Member = SlashOption(
            description="Who mentored the member",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer()

        add_staff_legacy(member.id, branch, int(role), added_by.id)

        if mentor:
            add_mod_record_legacy(member.id, mentor.id)

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} has been added to the database."
        )

    @staff.subcommand(description="Modify records")
    async def modify(
        self,
        interaction: nextcord.Interaction,
    ):
        pass

    @modify.subcommand(description="Modify Trial Mod Reviews")
    async def trial_review(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to modify",
        ),
        review_type: str = SlashOption(
            description="Type of review",
            choices=[
                "First Review",
                "Second Review",
                "Third Review",
                "Fourth Review",
                "Fifth Review",
                "Sixth Review",
            ],
        ),
        outcome: bool = SlashOption(
            description="Outcome of the review",
            choices={"Passed": True, "Failed": False},
            required=False,
        ),
        comment: str = SlashOption(
            description="Comments on the review",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod_lead):
            return

        await interaction.response.defer(ephemeral=True)

        if outcome is None and comment is None:
            await interaction.followup.send(
                f"{self.config.emotes.fail} You must provide a new outcome or comment to modify the review."
            )
            return

        with db_session(interaction.user) as session:
            review: TrialModReviews = (
                session.query(TrialModReviews)
                .filter_by(member=member.id, review_type=review_type)
                .first()
            )

            if not review:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} No review found for this user."
                )
                return

            if outcome is not None:
                review.review_passed = outcome

            if comment is not None:
                review.review_comment = comment

            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Review has been modified."
        )

    @modify.subcommand(description="Modify Moderation Records")
    async def mod_record(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to modify",
        ),
        mentor: nextcord.Member = SlashOption(
            description="Mentor to modify",
            required=False,
        ),
        trial_start_day: int = SlashOption(
            description="Day the trial started",
            required=False,
        ),
        trial_start_month: int = SlashOption(
            description="Month the trial started",
            required=False,
        ),
        trial_start_year: int = SlashOption(
            description="Year the trial started",
            required=False,
        ),
        trial_end_day: int = SlashOption(
            description="Day the trial ended",
            required=False,
        ),
        trial_end_month: int = SlashOption(
            description="Month the trial ended",
            required=False,
        ),
        trial_end_year: int = SlashOption(
            description="Year the trial ended",
            required=False,
        ),
        trial_passed: bool = SlashOption(
            description="Whether the trial was passed",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod_lead):
            return

        await interaction.response.defer(ephemeral=True)

        if any(
            date is not None
            for date in [trial_end_day, trial_end_month, trial_end_year]
        ):
            if not all(
                date is not None
                for date in [trial_end_day, trial_end_month, trial_end_year]
            ):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} If you provide a trial end date, you must provide the day, month, and year."
                )
                return

        if any(
            date is not None
            for date in [trial_start_day, trial_start_month, trial_start_year]
        ):
            if not all(
                date is not None
                for date in [trial_start_day, trial_start_month, trial_start_year]
            ):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} If you provide a trial start date, you must provide the day, month, and year."
                )
                return

        try:
            trial_start = date(trial_start_year, trial_start_month, trial_start_day)

            if trial_start > date.today():
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The trial start date cannot be in the future."
                )
                return

        except ValueError:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The trial start date is invalid."
            )
            return
        except TypeError:
            trial_start = None

        try:
            trial_end = date(trial_end_year, trial_end_month, trial_end_day)

            if trial_end > date.today():
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The trial end date cannot be in the future."
                )
                return

        except ValueError:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The trial end date is invalid."
            )
            return
        except TypeError:
            trial_end = None

        if trial_end and trial_start and (trial_end - trial_start).days < 14:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The trial must be at least 14 days long."
            )
            return

        if trial_end and trial_start and trial_end < trial_start:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The trial end date cannot be before the trial start date."
            )
            return

        with db_session(interaction.user) as session:
            record: ModerationRecords = (
                session.query(ModerationRecords).filter_by(member=member.id).first()
            )

            if mentor:
                record.mentor = mentor.id

            if trial_start:
                record.trial_start = trial_start

            if trial_end and record.trial_end is not None:
                record.trial_end = trial_end

            if trial_passed is not None and record.trial_passed is not None:
                record.trial_passed = trial_passed

            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Record has been modified."
        )

    @modify.subcommand(description="Modify Staff Records")
    async def staff_record(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to modify",
        ),
        branch: str = SlashOption(
            description="Branch the member was in",
            choices=["Administration", "Moderation", "Community Engagement Team"],
            required=False,
        ),
        role: str = SlashOption(
            description="Role the member had",
            choices={
                "Administrator": str(StaffRole.ADMIN.value),
                "Compliance Officer": str(StaffRole.COMPLIANCE.value),
                "Moderation Lead": str(StaffRole.HEAD_MOD.value),
                "Moderator": str(StaffRole.MOD.value),
                "Trial Moderator": str(StaffRole.TRIAL_MOD.value),
                "CET Lead": str(StaffRole.CET_LEAD.value),
                "CET": str(StaffRole.CET.value),
            },
            required=False,
        ),
        added_by: nextcord.Member = SlashOption(
            description="Who added the member to the database",
            required=False,
        ),
        active: bool = SlashOption(
            description="Whether the member is active",
            required=False,
        ),
        left_day: int = SlashOption(
            description="Day the member left",
            required=False,
        ),
        left_month: int = SlashOption(
            description="Month the member left",
            required=False,
        ),
        left_year: int = SlashOption(
            description="Year the member left",
            required=False,
        ),
        removed_by: nextcord.Member = SlashOption(
            description="Who removed the member",
            required=False,
        ),
        discharge_type: str = SlashOption(
            description="Type of discharge",
            choices={
                "Removed Bad Standing": RemovalType.REMOVED_BAD_STANDING.value,
                "Removed Good Standing": RemovalType.REMOVED_GOOD_STANDING.value,
                "Retire": RemovalType.RETIRE.value,
                "Retire Good Standing": RemovalType.RETIRE_GOOD_STANDING.value,
                "Retire Bad Standing": RemovalType.RETIRE_BAD_STANDING.value,
                "Failed Trial": RemovalType.FAILED_TRIAL.value,
            },
            required=False,
        ),
        discharge_reason: str = SlashOption(
            description="Reason for discharge",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        if (
            any(date is None for date in [left_day, left_month, left_year])
            and discharge_type
        ):
            await interaction.followup.send(
                f"{self.config.emotes.fail} If you provide a discharge date, you must provide the day, month, and year."
            )
            return

        if discharge_type and not discharge_reason:
            await interaction.followup.send(
                f"{self.config.emotes.fail} You must provide a reason for the discharge."
            )
            return

        try:
            left_date = date(left_year, left_month, left_day)

            if left_date > date.today():
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The discharge date cannot be in the future."
                )
                return

        except ValueError:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The discharge date is invalid."
            )
            return
        except TypeError:
            left_date = None

        with db_session(interaction.user) as session:
            record: StaffMembers = (
                session.query(StaffMembers).filter_by(member=member.id).first()
            )

            if branch:
                record.branch = branch

            if role:
                record.role = int(role)

            if added_by:
                record.added_by = added_by.id

            if active is not None:
                record.active = active

            if left_date:
                record.left = left_date

            if removed_by:
                record.removed_by = removed_by.id

            if discharge_type:
                record.discharge_type = discharge_type

            if discharge_reason:
                record.discharge_reason = discharge_reason

            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Record has been modified."
        )

    @staff.subcommand(description="Change personal settings")
    async def personal_settings(
        self,
        interaction: nextcord.Interaction,
        timezone: int = SlashOption(
            description="Your timezone offset in hours (e.g. UTC+1, UTC-5, etc.)",
            choices={f"UTC{offset:+d}": offset for offset in range(-12, 13)},
            required=False,
        ),
        dynamic_availability: int = SlashOption(
            description="How long to wait after last interaction on the server to become unavailable (minutes), 0 to disable",
            min_value=0,
            max_value=60,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session(interaction.user) as session:
            settings = (
                session.query(StaffMembers)
                .filter_by(member=interaction.user.id)
                .first()
            ).settings

            if timezone is not None and timezone != settings.timezone:
                if await confirm(
                    interaction,
                    title="Time zone change",
                    description=(
                        f"You are changing your time zone from UTC{settings.timezone:+d} to UTC{timezone:+d}. "
                        "Do you want to adjust your availability timeslots to match the new time zone?"
                    ),
                    true_button=ButtonPreset.YES_PRIMARY,
                    false_button=ButtonPreset.NO_NEUTRAL,
                    ephemeral=True,
                ):
                    adjustment = (timezone - settings.timezone) * 60
                    timeslots = (
                        session.query(ModeratorAvailability)
                        .filter_by(member=interaction.user.id, window_type="Timeslot")
                        .all()
                    )
                    for slot in timeslots:
                        slot.start += adjustment
                        slot.end += adjustment

                settings.timezone = timezone
                session.commit()

            if dynamic_availability is not None:
                settings.dynamic_availability = dynamic_availability
                if dynamic_availability == 0:
                    session.query(ModeratorAvailability).filter_by(
                        member=interaction.user.id, window_identifier="Last Seen"
                    ).delete()

            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Your settings have been updated.",
            ephemeral=True,
        )

    @staff.subcommand(description="Moderator Availability")
    async def availability(self, interaction: nextcord.Interaction):
        pass

    @availability.subcommand(description="Set availability timeslot(s)")
    async def set_timeslot(
        self,
        interaction: nextcord.Interaction,
        timeslot: str = SlashOption(
            description="Timeslot to set availability for",
            choices=[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
                "Weekdays",
                "Weekend",
                "All",
            ],
        ),
        start_time: int = SlashOption(
            description="Start time in 24-hour format",
            min_value=0,
            max_value=2359,
        ),
        end_time: int = SlashOption(
            description="End time in 24-hour format, value lower than start time will be considered as next day",
            min_value=0,
            max_value=2359,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        if start_time == end_time:
            await interaction.followup.send(
                f"{self.config.emotes.fail} Start and end times cannot be the same."
            )
            return

        if start_time > end_time:
            end_time += 2400

        match timeslot:
            case "All":
                days = calendar.day_name
            case "Weekend":
                days = calendar.day_name[5:7]
            case "Weekdays":
                days = calendar.day_name[0:5]
            case _:
                days = [timeslot]

        DAYS_ORDINAL = dict(zip(calendar.day_name, range(1, 8)))

        with db_session(interaction.user) as session:
            timezone = (
                session.query(StaffMembers)
                .filter_by(member=interaction.user.id)
                .first()
            ).settings.timezone

            for day in days:
                base_offset = DAYS_ORDINAL[day] * 1440 - timezone * 60
                session.merge(
                    ModeratorAvailability(
                        member=interaction.user.id,
                        window_identifier=day,
                        window_type="Timeslot",
                        priority=0,
                        start=base_offset + (start_time // 100) * 60 + start_time % 100,
                        end=base_offset + (end_time // 100) * 60 + end_time % 100,
                    )
                )
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Availability has been set."
        )

    @availability.subcommand(
        description="Force available status for certain time duration"
    )
    async def force_available(
        self,
        interaction: nextcord.Interaction,
        available_duration: int = SlashOption(
            description="Duration to be available for",
        ),
        available_timespan: str = SlashOption(
            description="Timespan to be available for",
            choices={
                "Minutes": "m",
                "Hours": "h",
            },
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        available_timedelta = convert_to_timedelta(
            available_timespan, available_duration
        )

        with db_session(interaction.user) as session:
            session.merge(
                ModeratorAvailability(
                    member=interaction.user.id,
                    window_identifier="Forced Available",
                    window_type="Duration",
                    priority=9999,  # IT'S OVER 9000 !!!
                    valid_until=datetime.now() + available_timedelta,
                )
            )
            session.commit()

            await set_availability_status(interaction.user, True)

        if available_timedelta >= timedelta(hours=16):
            await interaction.followup.send(
                f"{self.config.emotes.success} You have been forced to be available for {available_timedelta}. Please remember to take breaks."
            )

        else:
            await interaction.followup.send(
                f"{self.config.emotes.success} You have been forced to be available for {available_timedelta}."
            )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Forced Availability Set",
                description=f"{interaction.user.mention} has been forced to be available for {available_timedelta}.",
            )
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=SersiEmbed(
                title="Forced Availability Set",
                description=f"{interaction.user.mention} has been forced to be available for {available_timedelta}.",
            )
        )

    @availability.subcommand(
        description="Set unavailable status for certain time duration"
    )
    async def set_unavailable(
        self,
        interaction: nextcord.Interaction,
        unavailable_duration: int = SlashOption(
            description="Duration to be unavailable for",
        ),
        unavailable_timespan: str = SlashOption(
            description="Timespan to be unavailable for",
            choices={
                "Minutes": "m",
                "Hours": "h",
                "Days": "d",
                "Weeks": "w",
            },
        ),
        available_on_message: bool = SlashOption(
            description="Whether to become available during leave if you have recently messaged",
            required=False,
            choices={"Yes": True, "No": False},
        ),
        window_name: str = SlashOption(
            description="Window name (short), allows for multiple concurrent unavailable statuses",
            required=False,
            min_length=8,
            max_length=32,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        unavailable_timedelta = convert_to_timedelta(
            unavailable_timespan, unavailable_duration
        )

        window_name = window_name or "Forced Unavailable"

        with db_session(interaction.user) as session:
            if window := (
                session.query(ModeratorAvailability)
                .filter_by(
                    member=interaction.user.id,
                    window_identifier=window_name,
                )
                .first()
            ):
                if window.window_type != "Duration" or window.available:
                    interaction.followup.send(
                        f"{self.config.emotes.fail} Window `{window_name}` is not available for use as an unavailability window."
                    )
                elif window.valid_until > datetime.now():
                    if not await confirm(
                        interaction,
                        title="Unavailability window collision",
                        description=f"An unavailability window with the name `{window_name}` already exists and is valid until {format_dt(window.valid_until, style='R')}. Do you want to overwrite it?",
                        true_button=ButtonPreset.YES_DANGER,
                        false_button=ButtonPreset.NO_NEUTRAL,
                        ephemeral=True,
                    ):
                        return

            session.merge(
                ModeratorAvailability(
                    member=interaction.user.id,
                    window_identifier=window_name,
                    window_type="Duration",
                    priority=200 if available_on_message else 50,
                    available=False,
                    valid_until=datetime.now() + unavailable_timedelta,
                )
            )
            session.commit()

        if not check_staff_availability(interaction.user):
            await set_availability_status(interaction.user, False)

        await interaction.followup.send(
            f"{self.config.emotes.success} You have been forced to be unavailable for {unavailable_timedelta}.",
            ephemeral=True,
        )

        if unavailable_timedelta >= timedelta(days=3):
            unavailability_log_embed = SersiEmbed(
                title="Long Forced Unavailability Set",
                description=f"{interaction.user.mention} has been forced to be unavailable for {unavailable_timedelta}.",
            )

            interaction.guild.get_channel(self.config.channels.moderator_review).send(
                embed=unavailability_log_embed,
            )

            if is_trial_mod(interaction.user):
                with db_session() as session:
                    mod_record: ModerationRecords = (
                        session.query(ModerationRecords)
                        .filter_by(member=interaction.user.id)
                        .first()
                    )

                    mentor = interaction.guild.get_member(mod_record.mentor)

                    if mentor:
                        await mentor.send(
                            f"{interaction.user.mention} has been forced to be unavailable for {unavailable_timedelta}."
                        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Forced Unavailability Set",
                description=f"{interaction.user.mention} has been forced to be unavailable for {unavailable_timedelta}.",
            )
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=SersiEmbed(
                title="Forced Unavailability Set",
                description=f"{interaction.user.mention} has been forced to be unavailable for {unavailable_timedelta}.",
            )
        )

    @availability.subcommand(
        description="Set expire forced availability or unavailability"
    )
    async def expire_window(
        self,
        interaction: nextcord.Interaction,
        window: str = SlashOption(
            description="Window identifier (reason) for the forced availability or unavailability",
            min_length=8,
            max_length=32,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session(interaction.user) as session:
            availability_record = (
                session.query(ModeratorAvailability)
                .filter_by(
                    member=interaction.user.id,
                    window_identifier=window,
                    window_type="Duration",
                )
                .first()
            )
            if not availability_record:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} No forced availability or unavailability found for this window name."
                )
                return

            session.delete(availability_record)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} Forced availability or unavailability has been expired."
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Forced Availability/Unavailability Expired",
                description=f"{interaction.user.mention} has expired their forced availability or unavailability.",
            )
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=SersiEmbed(
                title="Forced Availability/Unavailability Expired",
                description=f"{interaction.user.mention} has expired their forced availability or unavailability.",
            )
        )

    @expire_window.on_autocomplete("window")
    async def expire_forced_autocomplete(
        self, interaction: nextcord.Interaction, window: str
    ):
        if not await permcheck(interaction, is_mod):
            return

        with db_session(interaction.user) as session:
            windows: ModeratorAvailability = (
                session.query(ModeratorAvailability.window_identifier)
                .filter_by(member=interaction.user.id, window_type="Duration")
                .filter(
                    ModeratorAvailability.valid_until > datetime.now(),
                    ModeratorAvailability.window_identifier.ilike(f"%{window or ''}%"),
                )
                .all()
            )

        await interaction.response.send_message([window[0] for window in windows])

    @commands.Cog.listener()
    async def on_honoured_member_revoke(self, details: VoteDetails):
        if details.outcome != "Accepted":
            return

        guild = self.bot.get_guild(self.config.guilds.main)

        with db_session(self.bot.user) as session:
            case: BlacklistCase = (
                session.query(BlacklistCase).filter_by(id=details.case_id).first()
            )
            case.active = True
            case.scrubbed = False
            session.commit()

            yes_voters = [
                guild.get_member(vote[0]).mention
                for vote in session.query(VoteRecord.voter)
                .filter_by(vote_id=details.vote_id, vote="yes")
                .all()
            ]

            member = guild.get_member(case.offender)
        honourable_member = guild.get_role(self.config.roles.honourable_member)

        await member.remove_roles(
            honourable_member, reason="Honoured member removal vote", atomic=True
        )

        # logging
        log_embed = SersiEmbed(
            title="Honoured Member status revoked.",
            description=f"{member.mention} has been removed from the Honourable Member role "
            f"due to a successful vote and blacklisted from staff.",
            fields={
                "Removed Honoured Member:": member.mention,
                "Reason:": case.reason,
                "Voters:": "- " + "\n- ".join(yes_voters),
            },
        )

        await guild.get_channel(self.config.channels.logging).send(embed=log_embed)
        await guild.get_channel(self.config.channels.mod_logs).send(embed=log_embed)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.guild is not None:
            self.bot.loop.create_task(self.update_mod_last_seen(interaction.user))

        if interaction.data is None or interaction.data.get("custom_id") is None:
            return
        if not interaction.data["custom_id"].startswith(
            "staff_data"
        ) and not interaction.data["custom_id"].startswith("mod_data"):
            return

        if not await permcheck(interaction, is_mod):
            return

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        match action:
            case "staff_data":
                embed = get_staff_embed(decode_snowflake(kwargs["user"]), interaction)

            case "mod_data":
                embed = get_moderation_embed(
                    decode_snowflake(kwargs["user"]), interaction
                )

            case "disciplinary_data":
                pass

        await interaction.followup.send(embed=embed, ephemeral=True)

    async def update_mod_last_seen(self, member: nextcord.Member):
        if not is_mod(member):
            return

        with db_session(self.bot.user) as session:
            staff: StaffMembers = (
                session.query(StaffMembers).filter_by(member=member.id).first()
            )

            if staff is None:
                return

            timeout = staff.settings.dynamic_availability
            if not timeout:
                return

            session.merge(
                ModeratorAvailability(
                    member=member.id,
                    window_identifier="Last Seen",
                    window_type="Duration",
                    valid_until=datetime.now() + timedelta(minutes=timeout),
                    priority=100,
                    available=True,
                )
            )
            session.commit()

            if not is_available(member):
                await set_availability_status(member, True)

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(
            self.config, message, ignore_channels=False, ignore_categories=False
        ):
            return
        await self.update_mod_last_seen(message.author)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: nextcord.Reaction, user: nextcord.Member):
        if ignored_message(
            self.config, reaction.message, ignore_channels=False, ignore_categories=False
        ):
            return
        await self.update_mod_last_seen(user)

    @commands.Cog.listener()
    async def on_reaction_remove(
        self, reaction: nextcord.Reaction, user: nextcord.Member
    ):
        if ignored_message(
            self.config, reaction.message, ignore_channels=False, ignore_categories=False
        ):
            return
        await self.update_mod_last_seen(user)
    
    @commands.Cog.listener()
    async def on_guild_audit_log_entry_creation(self, entry: nextcord.AuditLogEntry):
        if not isinstance(entry.target, nextcord.Member):
            return
        if not is_mod(entry.user) or entry.target == entry.user:
            return
        
        await self.update_mod_last_seen(entry.user)

    @tasks.loop(minutes=1)
    async def check_availability(self):
        with db_session(self.bot.user) as session:
            moderation: list[StaffMembers] = (
                session.query(StaffMembers)
                .filter_by(active=True)
                .filter(StaffMembers.branch.in_([Branch.MOD.value, Branch.ADMIN.value]))
                .all()
            )

            guild = self.bot.get_guild(self.config.guilds.main)

            for mod in moderation:
                member = guild.get_member(mod.member)
                if member is None:
                    continue

                if check_staff_availability(member):
                    if not is_available(member):
                        await set_availability_status(member, True)
                else:
                    if is_available(member):
                        await set_availability_status(member, False)

    @commands.Cog.listener()
    async def on_role_add(self, member: nextcord.Member, role: nextcord.Role):
        if role.id != self.config.roles.available_mod:
            return

        logging_embed = SersiEmbed(
            title=f"{member.display_name} is now Available.",
            description=f"{member.mention} has been set to be available.",
            thumbnail_url=member.display_avatar.url,
        )

        guild = self.bot.get_guild(self.config.guilds.main)

        await guild.get_channel(self.config.channels.logging).send(embed=logging_embed)

    @commands.Cog.listener()
    async def on_role_remove(self, member: nextcord.Member, role: nextcord.Role):
        if role.id != self.config.roles.available_mod:
            return

        logging_embed = SersiEmbed(
            title=f"{member.display_name} is now Unavailable.",
            description=f"{member.mention} has been set to be unavailable.",
            thumbnail_url=member.display_avatar.url,
        )

        guild = self.bot.get_guild(self.config.guilds.main)

        await guild.get_channel(self.config.channels.logging).send(embed=logging_embed)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Staff(bot, kwargs["config"]))
