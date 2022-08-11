import datetime
import nextcord
import time

from nextcord.ext import commands
from nextcord.ext.commands.errors import ExtensionAlreadyLoaded, ExtensionFailed, ExtensionNotFound

from configuration.configuration import Configuration
from database.database import Database
from sersi import Sersi
from utilities.cogs import load_cog, unload_cog
from utilities.permissions import is_a_sersi_contributor


class Management(commands.Cog, name="Management", description="Bot management and information related commands."):
    def __init__(self, bot: Sersi, config: Configuration, database: Database, start_time: float, data_folder: str):
        self.bot         = bot
        self.config      = config
        self.database    = database
        self.start_time  = start_time
        self.data_folder = data_folder

    @commands.command(brief="Loads a cog.", help="Loads a cog from the cog folder.")
    @is_a_sersi_contributor()
    async def load(self, ctx: commands.Context, extension: str):
        try:
            load_cog(self.bot, extension, self.config, self.database, self.start_time, self.data_folder)
            await ctx.reply(f"{self.config.emotes.success} The cog `{extension}` was loaded successfully.")
        except ExtensionAlreadyLoaded:
            await ctx.reply(f"{self.config.emotes.fail} The cog `{extension}` was already loaded.")
        except ExtensionFailed:
            await ctx.reply(f"{self.config.emotes.fail} The cog `{extension}` failed to load.")
        except ExtensionNotFound:
            await ctx.reply(f"{self.config.emotes.fail} The cog `{extension}` could not be found.")

    @commands.command(brief="Unloads a loaded cog.", help="Unloads a previously loaded cog.")
    @is_a_sersi_contributor()
    async def unload(self, ctx: commands.Context, extension: str):
        try:
            unload_cog(self.bot, extension)
            await ctx.reply(f"{self.config.emotes.success} The cog `{extension}` was unloaded successfully.")
        except ExtensionFailed:
            await ctx.reply(f"{self.config.emotes.fail} The cog `{extension}` failed to unload.")
        except ExtensionNotFound:
            await ctx.reply(f"{self.config.emotes.fail} The cog `{extension}` could not be found.")

    @commands.command(brief="Reloads a cog.", help="Reloads a previously loaded cog.")
    @is_a_sersi_contributor()
    async def reload(self, ctx: commands.Context, extension: str):
        try:
            unload_cog(self.bot, extension)
            load_cog(self.bot, extension, self.config, self.database, self.start_time, self.data_folder)
            await ctx.reply(f"{self.config.emotes.success} The cog `{extension}` was reloaded successfully.")
        except ExtensionFailed:
            await ctx.reply(f"{self.config.emotes.fail} The cog `{extension}` failed to reload.")
        except ExtensionNotFound:
            await ctx.reply(f"{self.config.emotes.fail} The cog `{extension}` could not be found.")

    @commands.command(
        brief="Executes Python code.",
        help="Executes python code, with the given script, management cog, command context, bot instance and configuration exposed to the script."
    )
    @is_a_sersi_contributor()
    async def eval(self, ctx: commands.Context, *, script: str):
        # TODO: protect against accidental (or malicious) token printing

        try:
            script_injected = "    " + script.replace('\n', '\n    ')

            _locals = locals()
            exec(f"async def __ex():\n{script_injected}", {
                "cog":     self,
                "ctx":     ctx,
                "script":  script,
                "bot":     self.bot,
                "config":  self.config,
                "db":      self.database}, _locals)

            result = await _locals['__ex']()
        except Exception as ex:
            embed = nextcord.Embed(
                title="Evaluation Failure",
                description=f"Script:\n```\n{script}\n```\nException:\n**{ex.__class__.__name__}**:\n```\n{ex.args}\n```",
                color=nextcord.Color.from_rgb(208, 29, 29)
            )

            await ctx.send(embed=embed)
            return

        embed = nextcord.Embed(
            title="Evaluation",
            description=f"Script:\n```\n{script}\n```\nResult:\n```\n{result}\n```",
            color=nextcord.Color.from_rgb(208, 29, 29)
        )

        await ctx.send(embed=embed)
        return

    @commands.command(brief="Checks the uptime of the bot.", help="Checks the current uptime, in hours:minutes:seconds, of the bot.")
    async def uptime(self, ctx):
        embed = nextcord.Embed(
            title="Sersi Uptime",
            description=f"Uptime: `{datetime.timedelta(seconds=int(round(time.time() - self.start_time)))}`",
            color=nextcord.Color.from_rgb(237, 91, 6))

        await ctx.send(embed=embed)

    @commands.command(brief="Checks the ping of the bot.", help="Checks the current ping of the bot, in milliseconds.")
    async def ping(self, ctx):
        await ctx.send(f"Pong! Ping: **{round(self.bot.latency * 1000)}ms**")


def setup(bot, **kwargs):
    bot.add_cog(Management(bot, kwargs["config"], kwargs["database"], kwargs["start_time"], kwargs["data_folder"]))
