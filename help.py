import re
import nextcord

from inspect import Parameter
from typing import Mapping, Optional
from nextcord.ext.commands import Cog, Command, Context, HelpCommand, Group

from configuration.configuration import Configuration


class Help(HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

        self.config: Configuration   = options["options"]["config"]
        self.color:  nextcord.Color  = nextcord.Color.from_rgb(237, 91, 6)

        self.regex_command_not_found = re.compile("(No command called )(\"[A-za-z0-9]+\")( found.)")

    async def send_bot_help(self, mapping: Mapping[Optional[Cog], list[Command]]):
        embed: nextcord.Embed = nextcord.Embed(
            title="Sersi - Help",
            description="This is a list of all commands available at the moment.",
            color=self.color
        )

        embed.set_footer(text=f"You may request help regarding a specific command by running {self.config.prefix}{self._command_impl.name} (command).")

        cog: Cog
        for cog in mapping:
            if cog is None:
                continue

            commands: list[Command] = await self.filter_commands(mapping[cog])
            if len(commands) == 0:
                continue

            command_descriptions: str     = ""
            command:              Command
            for command in commands:
                command_descriptions += f"- **{command.name}**: *{command.brief}*\n"

            embed.add_field(name=cog.qualified_name, value=command_descriptions, inline=False)

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog: Cog):
        pass

    async def send_command_help(self, command: Command):
        parameters: str = ""

        if len(command.params) > 0:
            name: str
            for name in command.params:
                parameter: Parameter = command.params[name]
                if parameter.name == "self" or parameter.annotation == Context:
                    continue

                pretty_annotation: str = parameter.annotation.__name__
                match parameter.annotation.__name__:
                    case str.__name__:
                        pretty_annotation = "text"

                    case int.__name__:
                        pretty_annotation = "number"

                parameters += f" {parameter.name} ({pretty_annotation})"

        embed: nextcord.Embed = nextcord.Embed(
            title=f"Sersi - Help - {command.name}",
            description=f"{self.config.prefix}**{command.name}**{parameters}\n\n{command.help}",
            color=self.color
        )

        embed.set_footer(text=f"The command \"{command.name}\" is part of the category \"{command.cog_name}\".")

        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error: str):
        if self.regex_command_not_found.match(error):
            await self.get_destination().send(self.config.emotes.fail + " " + error.replace("\"", "`"))
            return

        # TODO: report other errors to the log

    async def send_group_help(self, group: Group):
        raise NotImplementedError("Group Help not implemented")
        # TODO: implement group help (after.. uhh.. adding some commands with, y'know.. groups.)
