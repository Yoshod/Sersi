import nextcord

from nextcord.ext import commands

from configuration.configuration import Configuration


class ErrorHandling(commands.Cog, name="Error Handling", description="Error management and reporting."):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot    = bot
        self.config = config

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        match type(error):
            case commands.CommandNotFound:
                # The tendency of a typo are much higher than someone trying to run a command that legitimately doesn't exist, thus, we say nothing.
                return

            case commands.MemberNotFound:
                await ctx.send(f"{self.config.emotes.fail} The given member could not be found.")
                return

            case commands.MissingRequiredArgument:
                await ctx.send(f"{self.config.emotes.fail} Missing parameters.")
                return

            case commands.MissingPermissions | commands.CheckFailure | commands.CheckAnyFailure:
                await ctx.send(f"{self.config.emotes.fail} Insufficient permission.")
                return

            case _:
                channel = self.bot.get_channel(self.config.channels.errors)
                if channel is None:
                    print(f"Error while executing command \"{ctx.message.content}\": \"{error}\"") # TODO: use a separate logging implementation
                    return

                embed = nextcord.Embed(title="An Error Has Occurred", color=nextcord.Color.from_rgb(208, 29, 29))

                embed.add_field(name="Server:",  value=f"**{ctx.guild.name}** ({ctx.guild.id})",     inline=True)
                embed.add_field(name="Channel:", value=f"**{ctx.channel.name}** ({ctx.channel.id})", inline=True)
                embed.add_field(name="URL:",     value=f"[Jump URL]({ctx.message.jump_url})",        inline=True)
                embed.add_field(name="Command:", value=ctx.message.content,                          inline=False)
                embed.add_field(name="Error:",   value=f"```\n{error}\n```",                         inline=False)

                await channel.send(embed=embed)

                error_receipt = nextcord.Embed(
                    title="An Error Has Occurred",
                    description=(f"An error has occurred.\nThe error has been reported to the development staff.\n\nJoin the [support server]({self.config.invites.support_server}) for additional help if this error keeps occurring."),
                    color=nextcord.Color.from_rgb(208, 29, 29))

                await ctx.send(embed=error_receipt)


def setup(bot, **kwargs):
    bot.add_cog(ErrorHandling(bot, kwargs["config"]))
