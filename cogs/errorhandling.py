import nextcord
import sys
from nextcord.ext import commands
from baseutils import *


class ErrorHandling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error_details = []
        error_details.append(ctx.guild.name)
        error_details.append(ctx.guild.id)
        error_details.append(ctx.channel.name)
        error_details.append(ctx.channel.id)
        error_details.append(ctx.message.jump_url)
        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'errors'))
        if channel is None:
            await ctx.send(f"Error while executing command: `{error}`")
        else:
            (errno, value, traceback) = sys.exc_info()
            error_embed = nextcord.Embed(
                title="An Error Has Occurred",
                color=nextcord.Color.from_rgb(208, 29, 29))
            error_embed.add_field(name="Server:", value=(f"{error_details[0]} ({error_details[1]})"), inline=False)
            error_embed.add_field(name="Channel:", value=(f"{error_details[2]} ({error_details[3]})"), inline=False)
            error_embed.add_field(name="Errno:", value=errno, inline=False)
            error_embed.add_field(name="Value:", value=value, inline=False)
            error_embed.add_field(name="Traceback:", value=traceback, inline=False)
            error_embed.add_field(name="URL:", value=error_details[4], inline=False)
            await channel.send(f"Error while executing command: `{error}`", embed=error_embed)

            channel = ctx.channel.id
            error_receipt = nextcord.Embed(
                title="An Error Has Occurred",
                description=("An error has occurred. An alert has been sent to my creators."),
                color=nextcord.Color.from_rgb(208, 29, 29))
            error_receipt.set_footer(text=("Sersi Support Server: https://discord.gg/TgrPmDwVwq"))
            await ctx.send(embed=error_receipt)


def setup(bot):
    bot.add_cog(ErrorHandling(bot))
