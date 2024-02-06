import enum
from utils.database import db_session, StaffMembers, ActiveStaff, FormerStaff


class Branch(enum.Enum):
    """Staff Branches"""

    ADMIN = "Administration"
    MOD = "Moderation"
    CET = "Community Engagement Team"


class StaffRole(enum.Enum):
    """Staff Roles"""

    ADMIN = "Administrator"
    COMPLIANCE = "Compliance Officer"
    HEAD_MOD = "Moderation Lead"
    MOD = "Moderator"
    TRIAL_MOD = "Trial Moderator"
    CET_LEAD = "Community Engagement Team Lead"
    CET = "Community Engagement Team Member"


def add_staff_to_db(
    staff_id: int,
    branch: Branch,
    role: StaffRole,
    approver: int,
):
    """Adds a staff member to the database."""
    with db_session() as session:
        staff = StaffMembers(member=staff_id)
        session.add(staff)

        active_staff = ActiveStaff(
            member=staff_id,
            branch=branch.value,
            role=role.value,
            added_by=approver,
        )
        session.add(active_staff)
        session.commit()
