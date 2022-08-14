from datetime import timedelta
from nextcord import Game, Intents, Message, Status
from nextcord.ext.commands import Bot
from nextcord.ext.commands.errors import ExtensionFailed
from os import listdir
from time import time

from configuration.configuration import Configuration
from database.database import Database
from help import Help
from utilities.cogs import load_cog


class Sersi(Bot):
    def __init__(self, config: Configuration, database: Database, start_time: float, root_folder: str):
        super().__init__(command_prefix=config.prefix, intents=Intents.all())

        self.config      = config
        self.database    = database
        self.start_time  = start_time
        self.root_folder = root_folder

        self.help_command = Help(options={"config": config})

        print("Loading cogs...")

        count = 0
        failed_count = 0
        for filename in listdir("cogs"):
            if not filename.endswith(".py"):
                continue

            if self.config.cogs.disabled is not None and filename[:-3] in self.config.cogs.disabled:
                print(f"-> {filename[:-3]} (skipped!)")
                continue

            try:
                load_cog(self, filename[:-3], self.config, self.database, self.start_time, f"{self.root_folder}/data")
                print(f"-> {filename[:-3]}")
                count += 1
            except ExtensionFailed as ex:
                print(f"-> {filename[:-3]} failed: {ex.original}")
                failed_count += 1

        if failed_count > 0:
            print(f"\nSuccessfully loaded {count} cogs, failed to load {failed_count} cogs.")
        else:
            print(f"\nSuccessfully loaded {count} cogs.")

    async def close(self):
        print("Shutting down.")
        await self.change_presence(status=Status.offline)

        await super().close()

    async def on_ready(self):
        print(f"Logged in as {self.user.name}#{self.user.discriminator} (ID: {self.user.id}).")
        await self.change_presence(activity=Game(self.config.activity))

        print(f"Sersi is now online. Launch time: {timedelta(seconds=int(round(time() - self.start_time)))}")

    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if message.guild is not None and message.content == self.user.mention:
            await message.channel.send(f"Hey there {message.author.mention}, I am **Serversicherheit**, or **Sersi** for short! My role is to help keep {message.guild.name} a safe and enjoyable space.")
            return

        await self.process_commands(message)
