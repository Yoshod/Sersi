import enum
from utils.database import db_session, StaffMembers


class Branch(enum.Enum):
    """Staff Branches"""

    ADMIN = "Administration"
    MOD = "Moderation"
    CET = "Community Engagement Team"


class StaffRole(enum.Enum):
    """Staff Role IDs"""

    ADMIN = 1166770861232099369
    COMPLIANCE = 1166770861211123713
    HEAD_MOD = 1166770861211123721
    MOD = 1166770861211123720
    TRIAL_MOD = 1166770861211123719
    CET_LEAD = 1166770861211123712
    CET = 1166770861169197155


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
