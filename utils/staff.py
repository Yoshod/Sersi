import enum
import os
import nextcord
from utils.base import encode_button_id, encode_snowflake, get_discord_timestamp
from utils.database import db_session, StaffMembers, ModerationRecords, TrialModReviews
from utils.config import Configuration
from datetime import datetime
from utils.sersi_embed import SersiEmbed
import datetime

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config_path = os.path.join(parent_dir, "persistent_data/config.yaml")

CONFIG = Configuration.from_yaml_file(config_path)


class ModerationDataButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.red,
            label="Moderation Data",
            custom_id=encode_button_id("mod_data", user=encode_snowflake(user_id)),
            disabled=False,
        )


class StaffDataButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.red,
            label="Staff Data",
            custom_id=encode_button_id("staff_data", user=encode_snowflake(user_id)),
            disabled=False,
        )


class Branch(enum.Enum):
    """Staff Branches"""

    ADMIN = "Administration"
    MOD = "Moderation"
    CET = "Community Engagement Team"


class StaffRole(enum.Enum):
    """Staff Role IDs"""

    ADMIN = CONFIG.permission_roles.dark_moderator
    COMPLIANCE = CONFIG.permission_roles.compliance
    HEAD_MOD = CONFIG.permission_roles.senior_moderator
    MOD = CONFIG.permission_roles.moderator
    TRIAL_MOD = CONFIG.permission_roles.trial_moderator
    CET_LEAD = CONFIG.permission_roles.cet_lead
    CET = CONFIG.permission_roles.cet


class StaffRoleName(enum.Enum):
    """Staff Role Names"""

    ADMIN = "Administrator"
    COMPLIANCE = "Compliance Officer"
    HEAD_MOD = "Moderation Lead"
    MOD = "Moderator"
    TRIAL_MOD = "Trial Moderator"
    CET_LEAD = "Community Engagement Team Lead"
    CET = "Community Engagement Team Member"


class RemovalType(enum.Enum):
    """Staff Removal Types"""

    RETIRE = "Retirement"
    RETIRE_GOOD_STANDING = "Retirement in Good Standing"
    RETIRE_BAD_STANDING = "Retirement in Bad Standing"
    FAILED_TRIAL = "Failed Trial"
    REMOVED_GOOD_STANDING = "Removed in Good Standing"
    REMOVED_BAD_STANDING = "Removed in Bad Standing"


def add_staff_to_db(
    staff_id: int,
    branch: Branch,
    role: StaffRoleName,
    approver: int,
):
    """Adds a staff member to the database."""
    with db_session() as session:
        staff_member = StaffMembers(
            member=staff_id,
            branch=branch.value,
            role=role.value,
            added_by=approver,
        )
        session.add(staff_member)
        session.commit()


def add_mod_record(staff_id: int, mentor_id: int):
    """Adds a moderation record to the database."""
    with db_session() as session:
        mod_record = ModerationRecords(
            staff_member=staff_id,
            mentor=mentor_id,
        )
        session.add(mod_record)
        session.commit()


def add_staff_legacy(
    staff_id: int,
    branch: str,
    role: int,
    approver: int,
):
    """Adds a staff member to the database for legacy staff members."""
    with db_session() as session:
        staff_member = StaffMembers(
            member=staff_id,
            branch=branch,
            role=role,
            added_by=approver,
            joined=datetime.datetime.now() - datetime.timedelta(days=180),
        )
        session.add(staff_member)
        session.commit()


def add_mod_record_legacy(staff_id: int, mentor_id: int):
    """Adds a moderation record to the database for legacy staff members."""
    with db_session() as session:
        mod_record = ModerationRecords(
            staff_member=staff_id,
            mentor=mentor_id,
            trial_start=datetime.datetime.now() - datetime.timedelta(days=180),
            trial_end=datetime.datetime.now() - datetime.timedelta(days=150),
            trial_passed=True,
        )
        session.add(mod_record)
        session.commit()

    with db_session() as session:
        first_review = TrialModReviews(
            staff_member=staff_id,
            reviewer=mentor_id,
            review_date=datetime.datetime.now() - datetime.timedelta(days=180),
            review_outcome=True,
        )
        second_review = TrialModReviews(
            staff_member=staff_id,
            reviewer=mentor_id,
            review_date=datetime.datetime.now() - datetime.timedelta(days=150),
            review_outcome=True,
        )
        session.add(first_review)
        session.add(second_review)
        session.commit()


def staff_role_change(
    staff_id: int,
    role: StaffRoleName,
    approver: int,
):
    """Changes the role of a staff member."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        staff_member.role = role.value
        staff_member.added_by = approver
        session.commit()


def staff_branch_change(
    staff_id: int,
    branch: Branch,
    role: StaffRoleName,
    approver: int,
):
    """Changes the branch of a staff member."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        staff_member.branch = branch.value
        staff_member.role = role.value
        staff_member.added_by = approver
        session.commit()


def staff_retire(
    removed_id: int,
    remover_id: int,
    removal_type: RemovalType,
    removal_reason: str | None,
):
    """Retires a staff member."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=removed_id).first()
        staff_member.removed_by = remover_id
        staff_member.discharge_type = removal_type.value
        staff_member.discharge_reason = removal_reason
        staff_member.left = datetime.utcnow()
        staff_member.active = False
        session.commit()


def transfer_validity_check(staff_id: int, branch: Branch):
    """Checks if a staff member can be transferred to a new branch."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        try:
            if staff_member.branch == branch.value:
                return False
            return True
        except AttributeError:
            return False


def determine_transfer_type(staff_id: int, branch: Branch):
    """Determines the transfer type of a staff member."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        if staff_member.branch == Branch.MOD.value and branch == Branch.CET:
            return "mod_to_cet"
        elif staff_member.branch == Branch.CET.value and branch == Branch.MOD:
            return "cet_to_mod"

        else:
            raise ValueError(
                f"Invalid branch transfer. {staff_member.branch} to {branch.value}"
            )


def get_staff_embed(staff_id: int, interaction: nextcord.Interaction):
    """Gets an embed of a staff member's information."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        if staff_member:
            embed = SersiEmbed(
                title="Staff Member",
                description=f"**Staff Information**\n"
                f"{CONFIG.emotes.blank}**Member:** {interaction.guild.get_member(staff_member.member).mention} ({staff_member.member})\n"
                f"{CONFIG.emotes.blank}**Branch:** {staff_member.branch}\n"
                f"{CONFIG.emotes.blank}**Role:** {interaction.guild.get_role(staff_member.role).mention}\n"
                f"{CONFIG.emotes.blank}**Added By:** {interaction.guild.get_member(staff_member.added_by).mention} ({staff_member.added_by})\n"
                f"{CONFIG.emotes.blank}**Date Added:** {get_discord_timestamp(staff_member.joined, relative=True)}\n"
                f"{CONFIG.emotes.blank}**Active:** {CONFIG.emotes.success if staff_member.active else CONFIG.emotes.fail}\n",
            )

            return embed
        else:
            return SersiEmbed(
                title="Staff Member",
                description=f"{CONFIG.emotes.fail} There are no records of this user being a staff member.",
            )


def get_moderation_embed(staff_id: int, interaction: nextcord.Interaction):
    """Gets an embed of a staff member's moderation data."""
    pass
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        if not staff_member:
            return SersiEmbed(
                title="Moderation Data",
                description=f"{CONFIG.emotes.fail} There are no records of this user being a staff member.",
            )

        mod_records = (
            session.query(ModerationRecords).filter_by(staff_member=staff_id).first()
        )

        if not mod_records:
            return SersiEmbed(
                title="Moderation Data",
                description=f"{CONFIG.emotes.fail} There are no moderation records for this user.",
            )

        embed = SersiEmbed(
            title="Moderation Data", description=f"**Moderation Data**\n"
        )


def determine_staff_member(staff_id: int):
    """Determines if a user is a staff member."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        if staff_member:
            return staff_member
        else:
            return None


def mentor_check(mentee_id: int, mentor_id: int):
    """Checks if a user is a mentor to another user."""
    with db_session() as session:
        mentor = session.query(ModerationRecords).filter_by(member=mentee_id).first()
        if mentor:
            return mentor.mentor == mentor_id
        else:
            return False
