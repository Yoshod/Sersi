import enum
import os
from datetime import datetime, timedelta

import nextcord
from nextcord.utils import format_dt
from sqlalchemy import or_, and_

from utils.base import (
    encode_button_id,
    encode_snowflake,
    get_discord_timestamp,
)
from utils.database import (
    db_session,
    StaffMembers,
    ModerationRecords,
    Case,
    PeerReview,
    TrialModReviews,
    ModeratorAvailability,
)
from utils.config import Configuration
from utils.perms import is_allowed
from utils.sersi_embed import SersiEmbed

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
            member=staff_id,
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
            joined=datetime.now() - timedelta(days=180),
        )
        session.add(staff_member)
        session.commit()


def add_mod_record_legacy(staff_id: int, mentor_id: int):
    """Adds a moderation record to the database for legacy staff members."""
    with db_session() as session:
        mod_record = ModerationRecords(
            member=staff_id,
            mentor=mentor_id,
            trial_start=datetime.now() - timedelta(days=180),
            trial_end=datetime.now() - timedelta(days=150),
            trial_passed=True,
        )
        session.add(mod_record)
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
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        if not staff_member:
            return SersiEmbed(
                title="Moderation Data",
                description=f"{CONFIG.emotes.fail} There are no records of this user being a staff member.",
            )

        mod_records = (
            session.query(ModerationRecords).filter_by(member=staff_id).first()
        )

        if not mod_records:
            return SersiEmbed(
                title="Moderation Data",
                description=f"{CONFIG.emotes.fail} There are no moderation records for this user.",
            )

        mod_stats = get_moderation_stats(staff_id)

        reviews = get_trial_mod_reviews(staff_id)

        # Here we set the strings which have a chance of being None values
        # If we don't do this we may get varying errors when creating the embed

        number_of_reviews = len(reviews)

        review_string = ""

        if number_of_reviews == 0:
            review_string = f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}No reviews have been conducted for this moderator."

        else:
            for review in reviews:
                result = (
                    CONFIG.emotes.success if reviews[review] else CONFIG.emotes.fail
                )
                review_string += (
                    f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{review}: {result}\n"
                )

        try:
            trial_start_string = get_discord_timestamp(
                mod_records.trial_start, relative=True
            )

        except AttributeError:
            trial_start_string = "N/A"

        try:
            trial_end_string = get_discord_timestamp(
                mod_records.trial_end, relative=True
            )

        except AttributeError:
            trial_end_string = "N/A"

        try:
            most_recent_case = {mod_stats["Most Recent Case"].id}

        except AttributeError:
            most_recent_case = "N/A"

        embed = SersiEmbed(
            title="Moderation Data",
            description=f"**Trial Mod Stats**\n"
            f"{CONFIG.emotes.blank}**Mentor:** {interaction.guild.get_member(mod_records.mentor).mention} ({mod_records.mentor})\n"
            f"{CONFIG.emotes.blank}**Passed Trial Period:** {CONFIG.emotes.success if mod_records.trial_passed else CONFIG.emotes.fail if mod_records.trial_passed is not None else CONFIG.emotes.inherit}\n"
            f"{CONFIG.emotes.blank}**Trial Period Start:** {trial_start_string}\n"
            f"{CONFIG.emotes.blank}**Trial Period End:** {trial_end_string}\n"
            f"{CONFIG.emotes.blank}**Number of Reviews:** {number_of_reviews}\n"
            f"{CONFIG.emotes.blank}**Review Results:**\n"
            f"{review_string}\n"
            f"**Moderation Stats**\n"
            f"{CONFIG.emotes.blank}**Most Recent Case:** `{str(most_recent_case)[2:-2]}`\n"
            f"{CONFIG.emotes.blank}**Warns:** {mod_stats['Warns']}\n"
            f"{CONFIG.emotes.blank}**Timeouts:** {mod_stats['Timeouts']}\n"
            f"{CONFIG.emotes.blank}**Bans:** {mod_stats['Bans']}\n"
            f"{CONFIG.emotes.blank}**Slurs:** {mod_stats['Slurs']}\n"
            f"{CONFIG.emotes.blank}**Reformations:** {mod_stats['Reformations']}\n"
            f"{CONFIG.emotes.blank}**Bad Faith Pings:** {mod_stats['Bad Faith Pings']}\n"
            f"{CONFIG.emotes.blank}**Approved Peer Reviews:** {mod_stats['Approved Peer Reviews']}\n",
        )

        availability_records: list[ModeratorAvailability] = (
            session.query(ModeratorAvailability)
            .filter_by(member=staff_id)
            .filter(
                or_(
                    ModeratorAvailability.valid_until >= datetime.now(),
                    ModeratorAvailability.valid_until.is_(None),
                )
            )
            .order_by(
                ModeratorAvailability.priority.desc(), ModeratorAvailability.start.asc()
            )
            .all()
        )

        embed.description += "**Availability**\n"
        if is_available(interaction.guild.get_member(staff_id)):
            embed.description += f"{CONFIG.emotes.blank}**Currently *Available*** {CONFIG.emotes.success}\n"
        else:
            embed.description += f"{CONFIG.emotes.blank}**Currently *Unavailable*** {CONFIG.emotes.fail}\n"

        availability_record: ModeratorAvailability = (
            session.query(ModeratorAvailability)
            .filter_by(member=staff_id, window_type="Duration")
            .filter(ModeratorAvailability.valid_until > datetime.now())
            .order_by(ModeratorAvailability.priority.desc())
            .first()
        )

        if availability_record is not None:
            word = "Available" if availability_record.available else "Unavailable"
            timestamp = get_discord_timestamp(
                availability_record.valid_until, relative=True
            )
            embed.description += (
                f"{CONFIG.emotes.blank}**Forced {word} Until:** {timestamp}\n"
            )

        availability_records: list[ModeratorAvailability] = (
            session.query(ModeratorAvailability)
            .filter_by(member=staff_id, window_type="Timeslot")
            .order_by(ModeratorAvailability.start.asc())
            .all()
        )

        for record in availability_records:
            start = datetime(3000, 1, 1, (record.start // 60) % 24, record.start % 60)
            end = datetime(3000, 1, 1, (record.end // 60) % 24, record.end % 60)
            embed.description += f"{CONFIG.emotes.blank}**{record.window_identifier} Availability:** {format_dt(start, 't')} - {format_dt(end, 't')}\n"

        return embed


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


def get_trial_mod_reviews(staff_id: int):
    """Gets all trial moderator reviews for a staff member."""
    with db_session() as session:
        reviews = session.query(TrialModReviews).filter_by(member=staff_id).all()

        review_records = {}

        for i, review in enumerate(reviews):
            review_records[f"Review {i+1}"] = review.review_passed

        return review_records


def get_moderation_stats(staff_id: int):
    """Gets moderation stats for a staff member."""
    with db_session() as session:
        all_cases = session.query(Case).filter_by(moderator=staff_id).all()
        approved_reviews = 0
        total_reviews = 0

        for case in all_cases:
            case_id = case.id
            with db_session() as session:
                peer_reviews = (
                    session.query(PeerReview).filter_by(case_id=case_id).all()
                )
                for review in peer_reviews:
                    if review.review_outcome == "Approved":
                        approved_reviews += 1
                    total_reviews += 1

        if total_reviews == 0:
            approved_percentage = "This moderator has not had any peer reviews."
        else:
            approved_percentage = (approved_reviews / total_reviews) * 100

        cases = {
            "Most Recent Case": session.query(Case)
            .filter_by(moderator=staff_id)
            .order_by(Case.created.desc())
            .first(),
            "Warns": session.query(Case)
            .filter_by(moderator=staff_id, type="Warning")
            .count(),
            "Timeouts": session.query(Case)
            .filter_by(moderator=staff_id, type="Timeout")
            .count(),
            "Bans": session.query(Case)
            .filter_by(moderator=staff_id, type="Ban")
            .count(),
            "Slurs": session.query(Case)
            .filter_by(moderator=staff_id, type="Slur Usage")
            .count(),
            "Reformations": session.query(Case)
            .filter_by(moderator=staff_id, type="Reformation")
            .count(),
            "Bad Faith Pings": session.query(Case)
            .filter_by(moderator=staff_id, type="Ping")
            .count(),
            "Approved Peer Reviews": approved_percentage,
            "Total Cases": len(all_cases),
        }

        return cases


def promotion_validity_check(staff_id: int):
    """Checks if a Trial Moderator has passed at least 80% of their trial mod reviews."""
    with db_session() as session:
        mod_reviews = session.query(TrialModReviews).filter_by(member=staff_id).all()
        passed_reviews = 0
        total_reviews = len(mod_reviews)

        for review in mod_reviews:
            if review.review_passed:
                passed_reviews += 1

        if total_reviews % 2 != 0:
            return False

        if total_reviews < 2:
            return False

        return (passed_reviews / total_reviews) >= 0.65


def get_moderation_leaderboard_embed(
    interaction: nextcord.Interaction,
    case_type: str | None = None,
):
    """Gets a moderation leaderboard embed."""
    # The first thing we should do is get the IDs of all the moderation staff
    with db_session() as session:
        staff_members = session.query(StaffMembers).all()
        mod_ids = [staff.member for staff in staff_members]

    # Now we can get the moderation stats for each staff member
    mod_stats = {}
    for staff_id in mod_ids:
        mod_stats[staff_id] = get_moderation_stats(staff_id)

    # Now we determine the case type to display if one is specified

    match case_type:
        case "Warns":
            sorted_mods = sorted(
                mod_stats, key=lambda x: mod_stats[x]["Warns"], reverse=True
            )

        case "Timeouts":
            sorted_mods = sorted(
                mod_stats, key=lambda x: mod_stats[x]["Timeouts"], reverse=True
            )

        case "Bans":
            sorted_mods = sorted(
                mod_stats, key=lambda x: mod_stats[x]["Bans"], reverse=True
            )

        case "Slurs":
            sorted_mods = sorted(
                mod_stats, key=lambda x: mod_stats[x]["Slurs"], reverse=True
            )

        case "Reformations":
            sorted_mods = sorted(
                mod_stats, key=lambda x: mod_stats[x]["Reformations"], reverse=True
            )

        case "Bad Faith Pings":
            sorted_mods = sorted(
                mod_stats, key=lambda x: mod_stats[x]["Bad Faith Pings"], reverse=True
            )

        case "Approved Peer Reviews":
            try:
                sorted_mods = sorted(
                    mod_stats,
                    key=lambda x: float(mod_stats[x]["Approved Peer Reviews"]),
                    reverse=True,
                )
            except ValueError:
                sorted_mods = [
                    mod
                    for mod in mod_stats
                    if mod_stats[mod]["Approved Peer Reviews"]
                    != "This moderator has not had any peer reviews."
                ]
                sorted_mods = sorted(
                    sorted_mods,
                    key=lambda x: float(mod_stats[x]["Approved Peer Reviews"]),
                    reverse=True,
                )

        case None:
            sorted_mods = sorted(
                mod_stats, key=lambda x: mod_stats[x]["Total Cases"], reverse=True
            )

    # Now we can create the embed
    embed = SersiEmbed(
        title="Moderation Leaderboard",
        description="The moderation leaderboard displays the top 10 moderation staff members by the specified metric.",
    )

    for i, staff_id in enumerate(sorted_mods[:10]):
        member = interaction.guild.get_member(staff_id)
        if not member:
            member = "Unknown Member"
        else:
            member = member.display_name

        if case_type:
            case_value = mod_stats[staff_id][case_type]
        else:
            case_value = mod_stats[staff_id]["Total Cases"]

        embed.add_field(
            name=f"{i+1}. {member}",
            value=f"{case_type}: {case_value}",
            inline=False,
        )

    return embed


async def set_availability_status(
    member: nextcord.Member,
    set_as_available: bool,
):
    """Sets the availability status of a staff member."""
    guild = member.guild

    if set_as_available:
        await member.add_roles(guild.get_role(CONFIG.roles.available_mod))

    else:
        await member.remove_roles(guild.get_role(CONFIG.roles.available_mod))


def check_staff_availability(staff_member: int | nextcord.Member):
    """Checks if a staff member is inside their availability window."""
    if isinstance(staff_member, nextcord.Member):
        staff_id = staff_member.id
    else:
        staff_id = staff_member

    with db_session() as session:
        current_time = datetime.now()
        weekday = current_time.isoweekday()
        hour = current_time.hour
        minute = current_time.minute

        offset = (weekday * 24 + hour) * 60 + minute

        moderator_availability: ModeratorAvailability = (
            (
                session.query(ModeratorAvailability)
                .filter_by(member=staff_id, window_type="Duration")
                .filter(ModeratorAvailability.valid_until > current_time)
            )
            .union(
                session.query(ModeratorAvailability)
                .filter_by(member=staff_id, window_type="Timeslot")
                .filter(
                    or_(
                        and_(
                            ModeratorAvailability.start <= offset,
                            ModeratorAvailability.end >= offset,
                        ),
                        and_(  # If the window spans sunday to monday
                            or_(
                                ModeratorAvailability.start < 1440,
                                ModeratorAvailability.end > 11520,
                            ),
                            or_(
                                ModeratorAvailability.start % 10080 <= offset % 10080,
                                ModeratorAvailability.end % 10080 >= offset % 10080,
                            ),
                        ),
                    ),
                )
            )
            .order_by(ModeratorAvailability.priority.desc())
            .first()
        )

        if moderator_availability is None:
            return False

        return moderator_availability.available


def is_available(member: nextcord.Member):
    """Checks if a staff member has the availability role."""
    return is_allowed(member, [CONFIG.roles.available_mod])


def get_available_mods(guild: nextcord.Guild):
    """Counts the number of available moderators in a guild."""
    available_mods: list[nextcord.Member] = []

    with db_session() as session:
        staff_members = (
            session.query(StaffMembers)
            .filter(
                or_(
                    StaffMembers.branch == "Moderation",
                    StaffMembers.branch == "Administration",
                ),
            )
            .all()
        )

        mod_ids = [str(staff.member) for staff in staff_members if staff.left is None]

        for staff_id in mod_ids:
            member = guild.get_member(int(staff_id))
            if not member:
                continue

            if guild.get_role(CONFIG.roles.available_mod) in member.roles:
                available_mods.append(member)

    return available_mods


def get_staff_record(staff_id: int):
    """Gets a staff member's record."""
    with db_session() as session:
        staff_member = session.query(StaffMembers).filter_by(member=staff_id).first()
        return staff_member
