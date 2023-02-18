import csv
import pickle

import nextcord
from nextcord.ext import commands
from configutils import Configuration
from permutils import permcheck, is_senior_mod


class Alert(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config
        self.fields = [
            "message_url",
            "alert_type",
            "creation_time",
            "time_took_for_response",
        ]

    @commands.command(aliases=["re"])
    async def response_export(self, context):
        if not await permcheck(context, is_senior_mod):
            return

        with open(self.config.datafiles.alert_logs, "rb") as file:
            data: dict[dict] = pickle.load(file)

        dump_data: list[dict] = []
        for entry in data:
            dump_data.append(
                {
                    "message_url": entry,
                    "alert_type": data[entry]["alert_type"],
                    "creation_time": data[entry]["creation_time"],
                    "time_took_for_response": data[entry]["time_took_for_response"],
                }
            )

        with open(self.config.datafiles.alert_csv, "w") as csvfile:
            # creating a csv dict writer object
            writer = csv.DictWriter(csvfile, fieldnames=self.fields)

            # writing headers (field names)
            writer.writeheader()

            # writing data rows
            writer.writerows(dump_data)

        # send file
        await context.reply(
            file=nextcord.File(self.config.datafiles.alert_csv, filename="report.csv")
        )


def setup(bot, **kwargs):
    bot.add_cog(Alert(bot, kwargs["config"]))
