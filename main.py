import nextcord
from nextcord.ext import commands
from utils.database import create_db_tables

bot = commands.Bot()


@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

    create_db_tables()


bot.run("your token here")
