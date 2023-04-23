import asyncio

import nextcord
import os
import sys
import datetime
import time
import discordTokens

from nextcord.ext import commands

import configutils
from baseutils import SersiEmbed
from permutils import permcheck, is_sersi_contrib
from cogutils import load_all_cogs

start_time = time.time()
config = configutils.Configuration.from_yaml_file("./persistent_data/config.yaml")
bot = commands.Bot(
    command_prefix=config.bot.prefix,
    activity=nextcord.Game(name=config.bot.status),
    intents=nextcord.Intents.all(),
)
root_folder = os.path.dirname(os.path.realpath(__file__))


### COGS ###


@bot.slash_command()
async def cog(
    interaction: nextcord.Interaction,
    action: str = nextcord.SlashOption(
        description="Action to perform on cog.",
        choices={
            "Load": "load",
            "Unload": "unload",
            "Reload": "reload",
        },
    ),
    category: str = nextcord.SlashOption(
        description="Category of cog.",
    ),
    cog: str = nextcord.SlashOption(
        description="Cog to perform action on.",
    ),
):
    """Load, unload, or reload cogs.

    Permission needed: Sersi contributor"""
    if not await permcheck(interaction, is_sersi_contrib):
        return

    await interaction.response.defer()

    match action:
        case "unload":
            try:
                bot.unload_extension(f"cogs.{category}.{cog}")
                await interaction.followup.send(f"Cog {category}.{cog} unloaded.")
            except commands.errors.ExtensionNotFound:
                await interaction.followup.send("Cog not found.")
            except commands.errors.ExtensionNotLoaded:
                await interaction.followup.send(f"Cog {category}.{cog} was not loaded.")

        case "load":
            try:
                bot.load_extension(
                    f"cogs.{category}.{cog}",
                    extras={
                        "config": config,
                        "data_folder": f"{root_folder}/persistent_data",
                    },
                )
                await interaction.followup.send(f"Cog {category}.{cog} loaded.")
            except commands.errors.ExtensionNotFound:
                await interaction.followup.send("Cog not found.")
            except commands.errors.ExtensionAlreadyLoaded:
                await interaction.followup.send("Cog already loaded.")

        case "reload":
            try:
                bot.unload_extension(f"cogs.{category}.{cog}")
                bot.load_extension(
                    f"cogs.{category}.{cog}",
                    extras={
                        "config": config,
                        "data_folder": f"{root_folder}/persistent_data",
                    },
                )
                await interaction.followup.send(f"Cog {category}.{cog} reloaded.")
            except commands.errors.ExtensionNotFound:
                await interaction.followup.send("Cog not found.")
            except commands.errors.ExtensionNotLoaded:
                try:
                    bot.load_extension(
                        f"cogs.{category}.{cog}",
                        extras={
                            "config": config,
                            "data_folder": f"{root_folder}/persistent_data",
                        },
                    )
                    await interaction.followup.send(f"Cog {category}.{cog} loaded.")
                except commands.errors.ExtensionNotFound:
                    await interaction.followup.send("Cog not found.")
                except commands.errors.ExtensionAlreadyLoaded:
                    await interaction.followup.send("Cog already loaded.")

    await bot.sync_all_application_commands()


@cog.on_autocomplete("category")
async def cog_category_autocomplete(interaction: nextcord.Interaction, category: str):
    categories = [dir for dir in os.listdir("./cogs") if dir != "__pycache__"]
    if not category:
        return categories

    return [c for c in categories if c.startswith(category)]


@cog.on_autocomplete("cog")
async def cog_cog_autocomplete(
    interaction: nextcord.Interaction, cog_name: str, action: str, category: str
):
    bot_cogs = [
        cog_name.removeprefix(f"cogs.{category}.")
        for cog_name in bot.extensions.keys()
        if cog_name.startswith(f"cogs.{category}.")
    ]
    file_cogs = [
        cog_name.removesuffix(".py")
        for cog_name in os.listdir(f"./cogs/{category}")
        if cog_name != "__pycache__"
    ]

    if action == "load":
        available_cogs: list[str] = [cog_name for cog_name in file_cogs if cog_name not in bot_cogs]
    elif action == "unload":
        available_cogs: list[str] = [cog_name for cog_name in bot_cogs]
    elif action == "reload":
        available_cogs: list[str] = [cog_name for cog_name in bot_cogs if cog_name in file_cogs]
    else:
        available_cogs: list[str] = []

    if not cog_name:
        return available_cogs

    return [cog_suggestion for cog_suggestion in available_cogs if cog_suggestion.startswith(cog_name)]


@bot.command()
async def load(ctx: commands.Context, extension: str):
    """Loads Cog

    Loads cog.
    Permission needed: Sersi contributor"""
    if await permcheck(ctx, is_sersi_contrib):
        try:
            bot.load_extension(
                f"cogs.{extension}",
                extras={
                    "config": config,
                    "data_folder": f"{root_folder}/persistent_data",
                },
            )
            await bot.sync_all_application_commands()
            await ctx.reply(f"Cog {extension} loaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionAlreadyLoaded:
            await ctx.reply("Cog already loaded.")
    else:
        await ctx.reply(
            f"{config.emotes.fail} Only Sersi contributors are able to load cogs."
        )


@bot.command()
async def unload(ctx: commands.Context, extension: str):
    """Unload Cog

    Unloads cog.
    Permission needed: Sersi contributor"""
    if await permcheck(ctx, is_sersi_contrib):
        try:
            bot.unload_extension(f"cogs.{extension}")
            await bot.sync_all_application_commands()
            await ctx.reply(f"Cog {extension} unloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            await ctx.reply(f"Cog {extension} was not loaded.")
    else:
        await ctx.reply(
            f"{config.emotes.fail} Only Sersi contributors are able to unload cogs."
        )


@bot.command()
async def reload(ctx: commands.Context, extension: str):
    """Reload Cog

    Reloads cog. If cog wasn't loaded, loads cog.
    Permission needed: Sersi contributor"""
    if await permcheck(ctx, is_sersi_contrib):
        try:
            bot.unload_extension(f"cogs.{extension}")
            bot.load_extension(
                f"cogs.{extension}",
                extras={
                    "config": config,
                    "data_folder": f"{root_folder}/persistent_data",
                },
            )
            await bot.sync_all_application_commands()
            await ctx.reply(f"Cog {extension} reloaded.")
        except commands.errors.ExtensionNotFound:
            await ctx.reply("Cog not found.")
        except commands.errors.ExtensionNotLoaded:
            try:
                bot.load_extension(
                    f"cogs.{extension}",
                    extras={
                        "config": config,
                        "data_folder": f"{root_folder}/persistent_data",
                    },
                )
                await ctx.reply(f"Cog {extension} loaded.")
            except commands.errors.ExtensionNotFound:
                await ctx.reply("Cog not found.")
            except commands.errors.ExtensionAlreadyLoaded:
                await ctx.reply("Cog already loaded.")
    else:
        await ctx.reply(
            f"{config.emotes.fail} Only Sersi contributors are able to reload cogs."
        )


@bot.command()
async def about(ctx: commands.Context):
    """Display basic information about the bot."""
    embed = SersiEmbed(
        title="About Sersi",
        description="Sersi is the custom moderation help bot for Adam Something Central.",
        fields={
            "Version": config.bot.version,
            "Authors:": "\n".join(config.bot.authors),
            "GitHub Repository:": config.bot.git_url,
        },
    )
    await ctx.send(embed=embed)


@bot.command()
async def uptime(ctx: commands.Context):
    """Displays Sersi's uptime"""
    sersi_uptime = str(datetime.timedelta(seconds=int(round(time.time() - start_time))))
    embed = nextcord.Embed(
        title="Sersi Uptime",
        description=f"Sersi has been online for:\n`{sersi_uptime}`",
        color=nextcord.Color.from_rgb(237, 91, 6),
    )
    await ctx.send(embed=embed)


@bot.command()
async def ping(ctx: commands.Context):
    """test the response time of the bot"""
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")


@bot.event
async def on_message_edit(before: nextcord.Message, after: nextcord.Message):
    """treats edited messages like new messages when it comes to scanning"""
    bot.dispatch("message", after)


@bot.listen
async def on_ready():
    await bot.sync_all_application_commands()

    print(f"We have logged in as {bot.user}")


@bot.event
async def on_message(message: nextcord.Message):

    if message.author == bot.user:  # ignores message if message is this bot
        return

    elif bot in message.mentions:
        channel = message.channel
        await channel.send(
            f"Hey there {message.author.mention} I am Serversicherheit, or Sersi for short! My role is to help keep Adam Something Central a safe and enjoyable space."
        )

    await bot.process_commands(message)


print(f"System Version:\n{sys.version}")
print(f"Nextcord Version:\n{nextcord.__version__}")

bot.command_prefix = config.bot.prefix

asyncio.run(
    load_all_cogs(bot, config=config, data_folder=f"{root_folder}/persistent_data")
)

bot.run(discordTokens.getToken())
