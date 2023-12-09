import enum
from datetime import datetime

import nextcord

from utils.base import encode_snowflake, encode_button_id
from utils.database import Alert, db_session


class AlertType(enum.Enum):
    Slur = "Slur Detected"
    Ping = "Staff Role Ping"
    Toxic = "Toxic Message"


class AlertView(nextcord.ui.View):
    def __init__(self, alert_type: AlertType, user: nextcord.Member):
        super().__init__(auto_defer=False)
        self.add_item(
            nextcord.ui.Button(
                label="Action Taken",
                custom_id="alert_action_taken",
            )
        )
        if alert_type == AlertType.Slur:
            self.add_item(
                nextcord.ui.Button(
                    label="Acceptable Use",
                    custom_id="alert_acceptable_use",
                )
            )
            self.add_item(
                nextcord.ui.Button(
                    label="False Positive",
                    custom_id="alert_false_positive",
                )
            )
        elif alert_type == AlertType.Ping:
            self.add_item(
                nextcord.ui.Button(
                    label="Action not Necessary",
                    custom_id="alert_action_not_necessary",
                )
            )
            self.add_item(
                nextcord.ui.Button(
                    label="Bad Faith Ping",
                    custom_id="alert_bad_faith_ping",
                )
            )
        self.add_item(
            nextcord.ui.Button(
                label="Dismiss",
                custom_id="alert_dismiss",
                style=nextcord.ButtonStyle.red,
            )
        )

        self.add_item(
            nextcord.ui.Button(
                label="View Notes",
                custom_id=encode_button_id("notes", user=encode_snowflake(user.id)),
                row=1,
            ),
        )

        if alert_type == AlertType.Slur or alert_type == AlertType.Ping:
            self.add_item(
                nextcord.ui.Button(
                    label="Previous Cases",
                    custom_id=encode_button_id(
                        "cases",
                        user=encode_snowflake(user.id),
                        type="Slur Usage"
                        if alert_type == AlertType.Slur
                        else "Ping",
                    ),
                    row=1,
                ),
            )


def create_alert_log(message: nextcord.Message, alert_type: AlertType):
    """Creates an alert log entry in the database."""
    with db_session() as session:
        alert = Alert(
            id=encode_snowflake(message.id),
            alert_type=alert_type.value,
            report_url=message.jump_url,
        )
        session.add(alert)
        session.commit()

        return alert.id


def get_alert_type(alert: str | int | nextcord.Message):
    """Gets the alert type from an alert log entry in the database."""
    if isinstance(alert, nextcord.Message):
        alert_id = encode_snowflake(alert.id)
    elif isinstance(alert, int):
        alert_id = encode_snowflake(alert)
    else:
        alert_id = alert

    with db_session() as session:
        alert = session.query(Alert).filter_by(id=alert_id).first()
        if alert is None:
            return None

        return AlertType(alert.alert_type)


def add_response_time(alert: str | int | nextcord.Message):
    """Adds the response time to an alert log entry in the database."""
    if isinstance(alert, nextcord.Message):
        alert_id = encode_snowflake(alert.id)
    elif isinstance(alert, int):
        alert_id = encode_snowflake(alert)
    else:
        alert_id = alert

    with db_session() as session:
        alert = session.query(Alert).filter_by(id=alert_id).first()
        alert.response_time = datetime.utcnow()
        session.commit()
