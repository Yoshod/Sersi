import enum
from datetime import datetime

import nextcord

from utils.base import encode_snowflake
from utils.database import Alert, db_session


class AlertType(enum.Enum):
    Slur = "Slur Detected"
    Ping = "Staff Ping"
    Toxic = "Toxic Message"


async def create_alert_log(message: nextcord.Message, alert_type: AlertType):
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


async def add_response_time(alert: str | int | nextcord.Message):
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
