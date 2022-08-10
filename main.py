import time
import nextcord
import os
import sys

from configuration.configuration import Configuration
from database.database import Database
from sersi import Sersi


print(f"Sersi 4.0.0\n\nPython: {sys.version}\nnextcord: {nextcord.__version__}\n")


root_folder = os.path.dirname(os.path.realpath(__file__))

config      = Configuration.from_yaml_file(f"{root_folder}/data/config.yml")
database    = Database(f"{root_folder}/data/{config.database}")
start_time  = time.time()


bot = Sersi(config, database, start_time, root_folder)
bot.run(config.token)
