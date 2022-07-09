import nextcord
from nextcord.ext import commands
from configutils import get_config_int, get_config


class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.error_guild = bot.get_guild(977377117895536640)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            sersifail = get_config('EMOTES', "fail")
            channel = ctx.channel.id
            await ctx.send(f"{sersifail} That command does not exist.")
            return

        elif isinstance(error, commands.MissingRequiredArgument):
            sersifail = get_config('EMOTES', "fail")
            channel = ctx.channel.id
            await ctx.send(f"{sersifail} Please provide an argument to use this command.")
            return

        channel = self.error_guild.get_channel(get_config_int('CHANNELS', 'errors'))
        if channel is None:
            await ctx.send(f"Error while executing command: `{error}`")
        else:
            error_embed = nextcord.Embed(
                title="An Error Has Occurred",
                color=nextcord.Color.from_rgb(208, 29, 29))
            error_embed.add_field(name="Server:", value=f"{ctx.guild.name} ({ctx.guild.id})", inline=False)
            error_embed.add_field(name="Channel:", value=f"{ctx.channel.name} ({ctx.channel.id})", inline=False)
            error_embed.add_field(name="Command:", value=ctx.message.content, inline=False)
            error_embed.add_field(name="Error:", value=error, inline=False)
            error_embed.add_field(name="URL:", value=ctx.message.jump_url, inline=False)
            await channel.send(embed=error_embed)

            error_receipt = nextcord.Embed(
                title="An Error Has Occurred",
                description=("An error has occurred. An alert has been sent to my creators."),
                color=nextcord.Color.from_rgb(208, 29, 29))
            error_receipt.set_footer(text=("Sersi Support Server: https://discord.gg/TgrPmDwVwq"))
            await ctx.send(embed=error_receipt)


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
