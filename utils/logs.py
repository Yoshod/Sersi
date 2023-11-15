import datetime
import enum
import pickle

import nextcord

from utils.config import Configuration


class AlertType(enum.Enum):
    Slur = "slur"
    Ping = "ping"
    Toxic = "toxic"


async def create_alert_log(
    config: Configuration,
    message: nextcord.Message,
    alert_type: AlertType,
    timestamp: datetime.datetime,
):
    pass
    # TODO: implement using database
    # # ['message_url',"alert_type", "creation_time", "time_took_for_response"]
    # try:
    #     with open("files/Alerts/alerts.pkl", "rb") as file:
    #         data: dict[str:dict] = pickle.load(file)
    # except (EOFError, FileNotFoundError):
    #     data: dict[str:dict] = {}

    # data[message.jump_url] = {
    #     "alert_type": alert_type.value,
    #     "creation_time": timestamp,
    #     "time_took_for_response": None,
    # }

    # with open("files/Alerts/alerts.pkl", "wb") as file:
    #     pickle.dump(data, file)


async def update_response(
    config: Configuration, message: nextcord.Message, reacted_time: datetime.datetime
):
    pass
    # TODO: implement using database
    # with open("files/Alerts/alerts.pkl", "rb") as file:
    #     data: dict[str:dict] = pickle.load(file)

    # time_took: datetime.timedelta = (
    #     reacted_time - data[message.jump_url]["creation_time"]
    # )
    # data[message.jump_url]["time_took_for_response"] = time_took.seconds / 60

    # with open("files/Alerts/alerts.pkl", "wb") as file:
    #     pickle.dump(data, file)
