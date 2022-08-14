from nextcord import Color, Embed, TextChannel
from nextcord.ext import commands
from nextcord.ext.commands import Cog, CommandError, Context
from typing import Any

from configuration.configuration import Configuration
from sersi import Sersi


class ErrorHandling(Cog, name="Error Handling", description="Error management and reporting."):
    def __init__(self, bot: Sersi, config: Configuration):
        self.bot    = bot
        self.config = config

    @Cog.listener()
    async def on_command_error(self, context: Context, error: CommandError):
        match type(error):
            case commands.CommandNotFound:
                # Intentional skip
                return

            case commands.MemberNotFound:
                await context.send(f"{self.config.emotes.fail} The given member could not be found.")
                return

            case commands.MissingRequiredArgument:
                # TODO: inform the user of which parameter is missing
                await context.send(f"{self.config.emotes.fail} Missing parameters.")
                return

            case commands.MissingPermissions | commands.CheckFailure | commands.CheckAnyFailure:
                await context.send(f"{self.config.emotes.fail} Insufficient permission.")
                return

            case _:
                channel: TextChannel = self.bot.get_channel(self.config.channels.errors)
                if channel is None:
                    print(f"Error while executing command \"{context.message.content}\": \"{error}\"")  # TODO: use a separate logging implementation
                    return

                embed = Embed(
                    title="An Error Has Occurred",
                    color=Color.from_rgb(208, 29, 29))

                embed.add_field(name="Server:",  value=f"**{context.guild.name}** ({context.guild.id})",     inline=True)
                embed.add_field(name="Channel:", value=f"**{context.channel.name}** ({context.channel.id})", inline=True)
                embed.add_field(name="URL:",     value=f"[Jump URL]({context.message.jump_url})",            inline=True)
                embed.add_field(name="Command:", value=context.message.content,                              inline=False)
                embed.add_field(name="Error:",   value=f"```\n{error}\n```",                                 inline=False)

                await channel.send(embed=embed)

                error_receipt = Embed(
                    title="An Error Has Occurred",
                    description=f"An error has occurred.\nThe error has been reported to the development staff.\n\nJoin the [support server]({self.config.invites.support_server}) for additional help if this error keeps occurring.",
                    color=Color.from_rgb(208, 29, 29))

                await context.send(embed=error_receipt)


def setup(bot: Sersi, **kwargs: dict[Any]):
    bot.add_cog(ErrorHandling(bot, kwargs["config"]))
