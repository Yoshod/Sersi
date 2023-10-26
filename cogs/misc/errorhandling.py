import nextcord
from nextcord.ext import commands


from utils.config import Configuration
from utils.sersi_embed import SersiEmbed


class ErrorHandling(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        if bot.is_ready():
            self.error_guild = bot.get_guild(config.guilds.errors)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
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
