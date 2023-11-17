import traceback
from enum import Enum

import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.sersi_embed import SersiEmbed
from utils.sersi_exceptions import CommandDisabledException


class ApplicationCommandType(Enum):
    SLASH_COMMAND = 1
    USER = 2
    MESSAGE = 3


class ApplicationCommandOptionType(Enum):
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    FLOAT = 10


class ErrorHandling(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        if bot.is_ready():
            self.error_guild = bot.get_guild(config.guilds.errors)

    async def process_options(
        self, options: list[dict], interaction: nextcord.Interaction
    ) -> tuple[str, dict[str, str]]:
        fields = {}
        subcommand = ""
        for option in options:
            match ApplicationCommandOptionType(option["type"]):
                case (
                    ApplicationCommandOptionType.SUB_COMMAND
                    | ApplicationCommandOptionType.SUB_COMMAND_GROUP
                ):
                    subcommand, fields = await self.process_options(
                        option["options"], interaction
                    )
                    subcommand = (
                        f"{option['name']} {subcommand}"
                        if subcommand
                        else option["name"]
                    )
                case (
                    ApplicationCommandOptionType.STRING
                    | ApplicationCommandOptionType.INTEGER
                    | ApplicationCommandOptionType.FLOAT
                ):
                    fields[option["name"]] = option["value"]
                case ApplicationCommandOptionType.BOOLEAN:
                    if option["value"]:
                        fields[option["name"]] = self.config.emotes.success
                    else:
                        fields[option["name"]] = self.config.emotes.fail
                case (
                    ApplicationCommandOptionType.USER
                    | ApplicationCommandOptionType.CHANNEL
                    | ApplicationCommandOptionType.ROLE
                    | ApplicationCommandOptionType.MENTIONABLE
                ):
                    target = (
                        interaction.guild.get_member(int(option["value"]))
                        or interaction.guild.get_channel(int(option["value"]))
                        or interaction.guild.get_role(int(option["value"]))
                    )

                    if target is None:
                        try:
                            target = await self.bot.fetch_user(int(option["value"]))
                        except nextcord.NotFound:
                            pass

                    if isinstance(target, nextcord.Role):
                        fields[option["name"]] = f"{target.name} (`{target.id}`)"
                    elif isinstance(target, nextcord.TextChannel):
                        fields[
                            option["name"]
                        ] = f"{target.mention} (#{target.name} `{target.id}`)"
                    elif target is not None:
                        fields[
                            option["name"]
                        ] = f"{target.mention} ({target.display_name} `{target.id}`)"
                    else:
                        fields[option["name"]] = f"`{option['value']}`"

        return subcommand, fields

    @commands.Cog.listener()
    async def on_application_command_error(
        self, interaction: nextcord.Interaction, error: Exception
    ):
        if isinstance(error, CommandDisabledException):
            await interaction.response.send_message(
                "This command is currently disabled.", ephemeral=True
            )
            return

        channel = self.error_guild.get_channel(self.config.channels.errors)
        if channel is None:
            return

        embed_fields = {
            "Context:": f"{interaction.channel.mention} (#{interaction.channel.name} `{interaction.channel.id}`)",
            "User:": f"{interaction.user.mention} ({interaction.user.display_name} `{interaction.user.id}`)",
        }

        match ApplicationCommandType(interaction.data.get("type")):
            case ApplicationCommandType.SLASH_COMMAND:
                subcommand, fields = await self.process_options(
                    interaction.data.get("options", []), interaction
                )
                embed_fields["Command:"] = (
                    f"```/{interaction.data.get('name')} {subcommand}```"
                    if subcommand
                    else f"```/{interaction.data.get('name')}```"
                )
                embed_fields.update(fields)
            case ApplicationCommandType.USER:
                target = interaction.guild.get_member(
                    int(interaction.data.get("target_id"))
                )
                embed_fields["Command:"] = f"{interaction.data.get('name')}"
                if target is not None:
                    embed_fields[
                        "Target:"
                    ] = f"{target.mention} ({target.display_name} `{target.id}`)"
                else:
                    embed_fields["Target:"] = f"`{interaction.data.get('target_id')}`"
            case ApplicationCommandType.MESSAGE:
                embed_fields["Command:"] = f"{interaction.data.get('name')}"

                if message := await interaction.channel.fetch_message(
                    int(interaction.data.get("target_id"))
                ):
                    embed_fields.update(
                        {
                            "Message Author:": f"{message.author.mention} ({message.author.display_name} `{message.author.id}`)",
                            "Message Content:": message.content,
                            "Message URL:": f"{message.jump_url}",
                            "Message Sent:": f"<t:{int(message.created_at.timestamp())}:F>",
                        }
                    )
                else:
                    embed_fields[
                        "Message:"
                    ] = f"{interaction.channel.jump_url}/{interaction.data.get('target_id')}"

        await channel.send(
            embed=SersiEmbed(
                title="An Error Has Occurred",
                description="".join(
                    traceback.format_exception(
                        type(error), value=error, tb=error.__traceback__
                    )
                )[:4096],
                fields=embed_fields,
                footer=f"{interaction.guild.name} ({interaction.guild.id})",
                footer_icon=interaction.guild.icon.url,
                colour=nextcord.Color.from_rgb(208, 29, 29),
            )
        )
        await interaction.send(
            "An error has occurred. An alert has been sent to my creators.",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f"{self.config.emotes.fail} That command does not exist.")
            return

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"{self.config.emotes.fail} That member could not be found.")
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f"{self.config.emotes.fail} Please provide an argument to use this command."
            )
            return

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"{self.config.emotes.fail} You are using this command too quickly. Please wait {round(error.retry_after, 2)}s before trying again."
            )
            return

        channel = self.error_guild.get_channel(self.config.channels.errors)
        if channel is None:
            await ctx.send(f"Error while executing command: `{error}`")
        else:
            await channel.send(
                embed=SersiEmbed(
                    title="An Error Has Occurred",
                    fields={
                        "Server:": f"{ctx.guild.name} ({ctx.guild.id})",
                        "Channel:": f"{ctx.channel.name} ({ctx.channel.id})",
                        "Command:": ctx.message.content,
                        "Error:": error,
                        "URL:": ctx.message.jump_url,
                    },
                    colour=nextcord.Color.from_rgb(208, 29, 29),
                )
            )
            await ctx.send(
                embed=SersiEmbed(
                    title="An Error Has Occurred",
                    description="An error has occurred. An alert has been sent to my creators.",
                    colour=nextcord.Color.from_rgb(208, 29, 29),
                    footer="Sersi Support Server: https://discord.gg/TgrPmDwVwq",
                )
            )

    @commands.Cog.listener()
    async def on_ready(self):
        self.error_guild = self.bot.get_guild(self.config.guilds.errors)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(ErrorHandling(bot, kwargs["config"]))
