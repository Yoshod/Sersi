from dataclasses import dataclass
import datetime
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
)


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
