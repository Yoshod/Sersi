import nextcord
from nextcord.ext import commands
from configutils import Configuration


class ErrorHandling(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        if bot.is_ready():
            self.error_guild = bot.get_guild(config.guilds.errors)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            sersifail = self.config.emotes.fail
            channel = ctx.channel.id
            await ctx.send(f"{sersifail} That command does not exist.")
            return

        elif isinstance(error, commands.MemberNotFound):
            sersifail = self.config.emotes.fail
            channel = ctx.channel.id
            await ctx.send(f"{sersifail} That member could not be found.")
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            sersifail = self.config.emotes.fail
            channel = ctx.channel.id
            await ctx.send(
                f"{sersifail} Please provide an argument to use this command."
            )
            return

        elif isinstance(error, commands.CommandOnCooldown):
            sersifail = self.config.emotes.fail
            channel = ctx.channel.id
            await ctx.send(
                f"{sersifail} You are using this command too quickly. Please wait {round(error.retry_after, 2)}s before trying again."
            )
            return

        channel = self.error_guild.get_channel(self.config.channels.errors)
        if channel is None:
            await ctx.send(f"Error while executing command: `{error}`")
        else:
            error_embed = nextcord.Embed(
                title="An Error Has Occurred",
                color=nextcord.Color.from_rgb(208, 29, 29),
            )
            error_embed.add_field(
                name="Server:", value=f"{ctx.guild.name} ({ctx.guild.id})", inline=False
            )
            error_embed.add_field(
                name="Channel:",
                value=f"{ctx.channel.name} ({ctx.channel.id})",
                inline=False,
            )
            error_embed.add_field(
                name="Command:", value=ctx.message.content, inline=False
            )
            error_embed.add_field(name="Error:", value=error, inline=False)
            error_embed.add_field(name="URL:", value=ctx.message.jump_url, inline=False)
            await channel.send(embed=error_embed)

            error_receipt = nextcord.Embed(
                title="An Error Has Occurred",
                description="An error has occurred. An alert has been sent to my creators.",
                color=nextcord.Color.from_rgb(208, 29, 29),
            )
            error_receipt.set_footer(
                text="Sersi Support Server: https://discord.gg/TgrPmDwVwq"
            )
            await ctx.send(embed=error_receipt)

    @commands.Cog.listener()
    async def on_ready(self):
        self.error_guild = self.bot.get_guild(self.config.guilds.errors)


def setup(bot, **kwargs):
    bot.add_cog(ErrorHandling(bot, kwargs["config"]))
