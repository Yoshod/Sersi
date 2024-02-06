import enum
from utils.database import db_session, StaffMembers
from utils.config import Configuration

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


def add_staff_to_db(
    staff_id: int,
    branch: Branch,
    role: StaffRole,
    approver: int,
):
    """Adds a staff member to the database."""
    with db_session() as session:
        active_staff = StaffMembers(
            member=staff_id,
            branch=branch.value,
            role=role.value,
            added_by=approver,
        )
        session.add(active_staff)
        session.commit()
