import asyncio
import logging
import os
import sys

import nextcord
from dotenv import load_dotenv

from bot import SersiBot
from utils.cogs import load_all_cogs

load_dotenv()

bot = SersiBot()

root_folder = os.path.dirname(os.path.realpath(__file__))

# Ensure the logging directory exists
logging_directory = os.path.join(root_folder, "logging")
os.makedirs(logging_directory, exist_ok=True)

file_handler = logging.FileHandler(os.path.join(logging_directory, "sersi.log"))
file_handler.setLevel(logging.INFO)

# Create a stream handler for the root logger
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)

# Create a formatter and add it to the handlers
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s: %(message)s", datefmt="%d/%m/%y %H:%M:%S"
)
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Get the root logger and add the file and stream handlers to it
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(stream_handler)

# Create a file handler for the error logger
error_file_handler = logging.FileHandler(os.path.join(logging_directory, "error.log"))
error_file_handler.setLevel(logging.ERROR)
error_file_handler.setFormatter(formatter)

# Create the error logger and add the file handler to it
error_logger = logging.getLogger("error_logger")
error_logger.addHandler(error_file_handler)


@bot.event
async def on_ready():
    bot.error_channel = bot.get_channel(int(os.getenv('ERROR_CHANNEL', 0)))
    print(f"We have logged in as {bot.user}")


logging.info("\n\n=======================================")
logging.info("Starting bot...")
logging.info(f"System Version:\n{sys.version}")
logging.info(f"Nextcord Version:\n{nextcord.__version__}")

bot.command_prefix = os.getenv('COMMAND_PREFIX', "s!")
logging.info("Attempting to load cogs...")
asyncio.run(load_all_cogs(bot, root_folder))
logging.info("Loaded cogs; starting to run")


bot.run(os.getenv('DISCORD_TOKEN'))
