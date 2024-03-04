from dataclasses import dataclass
import datetime
import nextcord
from sqlalchemy import or_
from utils.sersi_embed import SersiEmbed

from utils.database import (
    BanCase,
    ReformationCase,
    TimeoutCase,
    WarningCase,
    db_session,
    Case,
    PeerReview,
    Alert,
    Ticket,
    SlurUsageCase,
    StaffMembers,
    ModeratorAvailability,
)

from utils.staff import count_available_mods
from utils.config import Configuration


@dataclass
class ModerationReport:
    total_cases: int
    total_warnings: int
    total_timeouts: int
    total_bans: int
    total_ban_votes: int
    total_reformations: int
    total_reviews: int
    total_approved_reviews: int
    total_alerts: int
    average_completion_time: int
    total_slur_alerts: int
    total_slur_cases: int
    total_ping_alerts: int
    tickets_created: int
    tickets_closed: int


async def get_moderation_report(
    start_date: datetime.datetime, end_date: datetime.datetime
):
    with db_session() as session:
        total_cases = (
            session.query(Case)
            .filter(Case.created >= start_date)
            .filter(Case.created <= end_date)
            .count()
        )
        total_warnings = (
            session.query(WarningCase)
            .filter(WarningCase.created >= start_date)
            .filter(WarningCase.created <= end_date)
            .count()
        )
        total_timeouts = (
            session.query(TimeoutCase)
            .filter(TimeoutCase.created >= start_date)
            .filter(TimeoutCase.created <= end_date)
            .count()
        )
        total_bans = (
            session.query(BanCase)
            .filter(BanCase.created >= start_date)
            .filter(BanCase.created <= end_date)
            .count()
        )

        total_ban_votes = (
            session.query(BanCase)
            .filter(BanCase.created >= start_date)
            .filter(BanCase.created <= end_date)
            .filter(
                or_(
                    BanCase.ban_type == "urgent",
                    BanCase.ban_type == "reformation failed",
                )
            )
            .count()
        )
        total_reformations = (
            session.query(ReformationCase)
            .filter(ReformationCase.created >= start_date)
            .filter(ReformationCase.created <= end_date)
            .count()
        )
        total_reviews = (
            session.query(PeerReview)
            .filter(PeerReview.timestamp >= start_date)
            .filter(PeerReview.timestamp <= end_date)
            .count()
        )
        total_approved_reviews = (
            session.query(PeerReview)
            .filter(PeerReview.timestamp >= start_date)
            .filter(PeerReview.timestamp <= end_date)
            .filter(PeerReview.review_outcome == "Approved")
            .count()
        )
        total_alerts = (
            session.query(Alert)
            .filter(Alert.creation_time >= start_date)
            .filter(Alert.creation_time <= end_date)
            .count()
        )
        total_slur_alerts = (
            session.query(Alert)
            .filter(Alert.creation_time >= start_date)
            .filter(Alert.creation_time <= end_date)
            .filter(Alert.alert_type == "Slur Detected")
            .count()
        )
        total_slur_cases = (
            session.query(Case)
            .filter(Case.created >= start_date)
            .filter(Case.created <= end_date)
            .filter(Case.type == "Slur Usage")
            .count()
        )
        total_ping_alerts = (
            session.query(Alert)
            .filter(Alert.creation_time >= start_date)
            .filter(Alert.creation_time <= end_date)
            .filter(Alert.alert_type == "Staff Role Ping")
            .count()
        )
        tickets_created = (
            session.query(Ticket)
            .filter(Ticket.created >= start_date)
            .filter(Ticket.created <= end_date)
            .count()
        )
        tickets_closed = (
            session.query(Ticket)
            .filter(Ticket.closed >= start_date)
            .filter(Ticket.closed <= end_date)
            .count()
        )

        all_alerts = (
            session.query(Alert)
            .filter(Alert.creation_time >= start_date)
            .filter(Alert.creation_time <= end_date)
            .filter(Alert.response_time is not None)
            .all()
        )

        if all_alerts:
            completion_times = []
            for alert in all_alerts:
                completion_times.append(
                    (alert.response_time - alert.creation_time).total_seconds()
                )

            average_completion_time = int(sum(completion_times) / len(completion_times))

        else:
            average_completion_time = 0

    return ModerationReport(
        total_cases=total_cases,
        total_warnings=total_warnings,
        total_timeouts=total_timeouts,
        total_bans=total_bans,
        total_ban_votes=total_ban_votes,
        total_reformations=total_reformations,
        total_reviews=total_reviews,
        total_approved_reviews=total_approved_reviews,
        total_alerts=total_alerts,
        total_slur_alerts=total_slur_alerts,
        total_slur_cases=total_slur_cases,
        total_ping_alerts=total_ping_alerts,
        average_completion_time=average_completion_time,
        tickets_created=tickets_created,
        tickets_closed=tickets_closed,
    )


def get_moderation_report_embed(
    report: ModerationReport,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    report_type: str,
):
    return SersiEmbed(
        title=report_type,
        description=f"**Start Date:** {start_date.strftime('%d/%m/%Y')}\n**End Date:** {end_date.strftime('%d/%m/%Y')}",
        fields={
            "Total Cases": report.total_cases,
            "Total Warnings": report.total_warnings,
            "Total Timeouts": report.total_timeouts,
            "Total Bans": report.total_bans,
            "Total Ban Votes": report.total_ban_votes,
            "Total Reformations": report.total_reformations,
            "Total Reviews": report.total_reviews,
            "Total Approved Reviews": report.total_approved_reviews,
            "Total Alerts": report.total_alerts,
            "Average Alert Response Time": f"{str(datetime.timedelta(seconds=report.average_completion_time))}",
            "Total Slur Alerts": report.total_slur_alerts,
            "Total Ping Alerts": report.total_ping_alerts,
            "Tickets Created": report.tickets_created,
            "Tickets Closed": report.tickets_closed,
        },
    )


def get_slur_report(start_date: datetime.datetime, end_date: datetime.datetime):
    with db_session() as session:
        total_slur_alerts = (
            session.query(Alert)
            .filter(Alert.creation_time >= start_date)
            .filter(Alert.creation_time <= end_date)
            .filter(Alert.alert_type == "Slur Detected")
            .count()
        )
        total_slur_cases = (
            session.query(Case)
            .filter(Case.created >= start_date)
            .filter(Case.created <= end_date)
            .filter(Case.type == "Slur Usage")
            .count()
        )

        # Next we should create a list of the 10 most used slurs and their counts

        slurs = [slur.slur_used for slur in session.query(SlurUsageCase).all()]

        slur_counts = {}
        for slur in slurs:
            if slur in slur_counts:
                slur_counts[slur] += 1
            else:
                slur_counts[slur] = 1

        # Now we should sort the slur counts and get the top 10
        sorted_slurs = sorted(slur_counts.items(), key=lambda x: x[1], reverse=True)

        slur_offenders = [
            case.offender
            for case in session.query(Case).filter(Case.type == "Slur Usage").all()
        ]

        # Now we should create a list of the 10 users with the most slur cases
        user_counts = {}
        for user in slur_offenders:
            if user in user_counts:
                user_counts[user] += 1
            else:
                user_counts[user] = 1

        sorted_users = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)

        # Now we format the user IDs into mentions surrounding the ID with <@ and >
        formatted_users = []
        for user in sorted_users:
            formatted_users.append(f"<@{user[0]}> - {user[1]} cases")

    return total_slur_alerts, total_slur_cases, sorted_slurs[:10], formatted_users


def get_slur_report_embed(
    total_slur_alerts: int,
    total_slur_cases: int,
    top_slurs: list,
    top_users: list,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
):
    return SersiEmbed(
        title="Slur Report",
        description=f"**Start Date:** {start_date.strftime('%d/%m/%Y')}\n**End Date:** {end_date.strftime('%d/%m/%Y')}",
        fields={
            "Total Slur Alerts": total_slur_alerts,
            "Total Slur Cases": total_slur_cases,
            "Top 10 Slurs": "\n".join(
                [f"{slur[0]} - {slur[1]} uses" for slur in top_slurs]
            ),
            "Top 10 Offenders": "\n".join(top_users),
        },
    )


def get_availabillity_report_unused():  # This function is currently unused as I cannot be arsed to implement it fully
    raise NotImplementedError()

    available_mod_count, available_mod_ids = count_available_mods()

    with db_session() as session:
        total_mods = (
            session.query(StaffMembers)
            .filter(
                or_(
                    StaffMembers.branch == "Moderation",
                    StaffMembers.branch == "Administration",
                ),
                StaffMembers.left is None,
            )
            .all()
        )

        total_mods_availability_setup = session.query(ModeratorAvailability).all()

        availability_times_overall = {
            datetime.time(0, 0): 0,
            datetime.time(1, 0): 0,
            datetime.time(2, 0): 0,
            datetime.time(3, 0): 0,
            datetime.time(4, 0): 0,
            datetime.time(5, 0): 0,
            datetime.time(6, 0): 0,
            datetime.time(7, 0): 0,
            datetime.time(8, 0): 0,
            datetime.time(9, 0): 0,
            datetime.time(10, 0): 0,
            datetime.time(11, 0): 0,
            datetime.time(12, 0): 0,
            datetime.time(13, 0): 0,
            datetime.time(14, 0): 0,
            datetime.time(15, 0): 0,
            datetime.time(16, 0): 0,
            datetime.time(17, 0): 0,
            datetime.time(18, 0): 0,
            datetime.time(19, 0): 0,
            datetime.time(20, 0): 0,
            datetime.time(21, 0): 0,
            datetime.time(22, 0): 0,
            datetime.time(23, 0): 0,
        }

        availability_times_monday = availability_times_overall.copy()
        availability_times_tuesday = availability_times_overall.copy()
        availability_times_wednesday = availability_times_overall.copy()
        availability_times_thursday = availability_times_overall.copy()
        availability_times_friday = availability_times_overall.copy()
        availability_times_saturday = availability_times_overall.copy()
        availability_times_sunday = availability_times_overall.copy()

        for mod in total_mods_availability_setup:
            start_time_mon = datetime.datetime.strptime(mod.monday_start, "%H%M").time()
            end_time_mon = datetime.datetime.strptime(mod.monday_end, "%H%M").time()

            start_time_tue = datetime.datetime.strptime(
                mod.tuesday_start, "%H%M"
            ).time()
            end_time_tue = datetime.datetime.strptime(mod.tuesday_end, "%H%M").time()

            start_time_wed = datetime.datetime.strptime(
                mod.wednesday_start, "%H%M"
            ).time()
            end_time_wed = datetime.datetime.strptime(mod.wednesday_end, "%H%M").time()

            start_time_thu = datetime.datetime.strptime(
                mod.thursday_start, "%H%M"
            ).time()
            end_time_thu = datetime.datetime.strptime(mod.thursday_end, "%H%M").time()

            start_time_fri = datetime.datetime.strptime(mod.friday_start, "%H%M").time()
            end_time_fri = datetime.datetime.strptime(mod.friday_end, "%H%M").time()

            start_time_sat = datetime.datetime.strptime(
                mod.saturday_start, "%H%M"
            ).time()
            end_time_sat = datetime.datetime.strptime(mod.saturday_end, "%H%M").time()

            start_time_sun = datetime.datetime.strptime(mod.sunday_start, "%H%M").time()
            end_time_sun = datetime.datetime.strptime(mod.sunday_end, "%H%M").time()

            for time in availability_times_monday:
                if start_time_mon <= time <= end_time_mon:
                    availability_times_monday[time] += 1

            for time in availability_times_tuesday:
                if start_time_tue <= time <= end_time_tue:
                    availability_times_tuesday[time] += 1

            for time in availability_times_wednesday:
                if start_time_wed <= time <= end_time_wed:
                    availability_times_wednesday[time] += 1

            for time in availability_times_thursday:
                if start_time_thu <= time <= end_time_thu:
                    availability_times_thursday[time] += 1

            for time in availability_times_friday:
                if start_time_fri <= time <= end_time_fri:
                    availability_times_friday[time] += 1

            for time in availability_times_saturday:
                if start_time_sat <= time <= end_time_sat:
                    availability_times_saturday[time] += 1

            for time in availability_times_sunday:
                if start_time_sun <= time <= end_time_sun:
                    availability_times_sunday[time] += 1

            for time in availability_times_overall:
                if start_time_mon <= time <= end_time_mon:
                    availability_times_overall[time] += 1
                if start_time_tue <= time <= end_time_tue:
                    availability_times_overall[time] += 1
                if start_time_wed <= time <= end_time_wed:
                    availability_times_overall[time] += 1
                if start_time_thu <= time <= end_time_thu:
                    availability_times_overall[time] += 1
                if start_time_fri <= time <= end_time_fri:
                    availability_times_overall[time] += 1
                if start_time_sat <= time <= end_time_sat:
                    availability_times_overall[time] += 1
                if start_time_sun <= time <= end_time_sun:
                    availability_times_overall[time] += 1

    return (
        available_mod_count,
        available_mod_ids,
        total_mods,
        total_mods_availability_setup,
        availability_times_monday,
        availability_times_tuesday,
        availability_times_wednesday,
        availability_times_thursday,
        availability_times_friday,
        availability_times_saturday,
        availability_times_sunday,
        availability_times_overall,
    )


def get_availability_report(guild: nextcord.Guild):
    available_mod_count, available_mod_ids = count_available_mods(guild)

    with db_session() as session:
        total_mods = (
            session.query(StaffMembers)
            .filter(
                or_(
                    StaffMembers.branch == "Moderation",
                    StaffMembers.branch == "Administration",
                ),
            )
            .all()
        )

        total_mods_availability_setup = session.query(ModeratorAvailability).all()

        all_mod_ids = [str(mod.member) for mod in total_mods if mod.left is None]
        all_mods_with_availability_setup = [
            str(mod.member) for mod in total_mods_availability_setup
        ]

        mods_without_availability_setup = list(
            set(all_mod_ids) - set(all_mods_with_availability_setup)
        )

    availability_report = {
        "available_mod_count": available_mod_count,
        "available_mod_ids": available_mod_ids,
        "all_mod_ids": all_mod_ids,
        "mods_without_availability_setup": mods_without_availability_setup,
    }
    return availability_report


def get_availability_report_embed(
    config: Configuration,
    availability_report: dict,
):

    available_mods_string = ""
    for mod in availability_report["available_mod_ids"]:
        available_mods_string += f"{config.emotes.blank}{config.emotes.blank}<@{mod}>\n"

    mods_without_availability_setup_string = ""
    for mod in availability_report["mods_without_availability_setup"]:
        mods_without_availability_setup_string += (
            f"{config.emotes.blank}{config.emotes.blank}<@{mod}>\n"
        )

    return SersiEmbed(
        title="Moderator Availability Report",
        description=f"**Moderator Availability**:\n{config.emotes.blank}**Total Moderators**: {str(len(availability_report['all_mod_ids']))}\n{config.emotes.blank}**Available Moderators**: {availability_report['available_mod_count']}\n{config.emotes.blank}**Currently Available**:\n{available_mods_string.rstrip()}\n{config.emotes.blank}**Availability Not Setup**:\n{mods_without_availability_setup_string.rstrip()}",
    )
