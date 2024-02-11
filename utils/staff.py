import enum
from utils.database import db_session, StaffMembers
from utils.config import Configuration
from datetime import datetime

CONFIG = Configuration()


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
    CET_LEAD = "CET Lead"
    CET = "CET"


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
    role: StaffRole,
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


def staff_role_change(
    staff_id: int,
    role: StaffRole,
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
    role: StaffRole,
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
        if staff_member.branch == branch.value:
            return False
        return True


def determine_transfer_type(staff_id: int, branch: Branch):
    """Determines the transfer type of a staff member."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        if staff_member.branch == Branch.MOD.value and branch == Branch.CET:
            return "mod_to_cet"
        if staff_member.branch == Branch.CET.value and branch == Branch.MOD:
            return "cet_to_mod"
