import nextcord
import sys

from os.path import dirname, realpath
from time import time

from configuration.configuration import Configuration
from database.database import Database
from sersi import Sersi


print(f"Sersi 4.0.0\n\nPython: {sys.version}\nnextcord: {nextcord.__version__}\n")

root_folder = dirname(realpath(__file__))

config      = Configuration.from_yaml_file(f"{root_folder}/data/config.yml")
database    = Database(f"{root_folder}/data/{config.database}")
start_time  = time()

Sersi(config, database, start_time, root_folder).run(config.token)
