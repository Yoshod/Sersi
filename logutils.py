import datetime
import enum
import pickle

import nextcord

from configutils import Configuration


class AlertType(enum.Enum):
    Slur = "slur"
    Ping = "ping"


async def create_alert_log(
        config: Configuration,
        message: nextcord.Message,
        alert_type: AlertType,
        timestamp: datetime.datetime,
):
    # ['message_url',"alert_type", "creation_time", "time_took_for_response"]
    try:
        with open(config.datafiles.alert_logs, "rb") as file:
            data: dict[str:dict] = pickle.load(file)
    except (EOFError, FileNotFoundError):
        data: dict[str:dict] = {}

    data[message.jump_url] = {
        "alert_type": alert_type.value,
        "creation_time": timestamp,
        "time_took_for_response": None,
    }

    with open(config.datafiles.alert_logs, "wb") as file:
        pickle.dump(data, file)


async def update_response(
        config: Configuration, message: nextcord.Message, reacted_time: datetime.datetime
):
    with open(config.datafiles.alert_logs, "rb") as file:
        data: dict[str:dict] = pickle.load(file)

    time_took: datetime.timedelta = (
            reacted_time - data[message.jump_url]["creation_time"]
    )
    data[message.jump_url]["time_took_for_response"] = time_took.seconds / 60

    with open(config.datafiles.alert_logs, "wb") as file:
        pickle.dump(data, file)
