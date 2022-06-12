import configparser
import nextcord
from nextcord.ext import commands
from baseutils import *


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setsetting(self, ctx, section, setting, value):

        # sections only modifiable by dark moderators
        if not is_dark_mod(ctx.author):
            await ctx.send(f"<:sersifail:979070135799279698> Only dark moderators can modify settings.")
            return

        section = section.upper()
        set_config(section, setting, value)
        await ctx.send(f"<:sersisuccess:979066662856822844> `[{section}] {setting}` has been set to `{value}`")
        if section == "BOT":
            await ctx.invoke(self.bot.get_command('reloadbot'))

    @commands.command()
    async def reloadbot(self, ctx):
        if not is_mod(ctx.author):
            await ctx.reply("<:sersifail:979070135799279698> Insufficient permission!")
            return

        await self.bot.change_presence(activity=nextcord.Game(get_config("BOT", "status")))
        self.bot.command_prefix = get_config("BOT", "command prefix")
        await ctx.send(f"<:sersisuccess:979066662856822844> Bot reloaded.")

    @commands.command(aliases=['config', 'conf'])
    async def configuration(self, ctx, *args):
        if not is_staff(ctx.author) or not isSersiContrib(ctx.author.roles):
            await ctx.reply("<:sersifail:979070135799279698> Insufficient permission!")
            return

        if len(args) == 4:
            if args[0].upper() == "SET":        # yes this does need to be stacked that way, no you can't just 'and' the two conditions.
                await ctx.invoke(self.bot.get_command('setsetting'), section=args[1], setting=args[2], value=args[3])

        elif len(args) != 0:
            await ctx.send(f"Invalid argument: `{args}`")

        embed_list = []

        config = configparser.ConfigParser()
        config.read("config.ini")

        for section in config.sections():

            config_embed = nextcord.Embed(
                title=section,
                color=nextcord.Color.from_rgb(237, 91, 6))

            for field in config[section]:
                value = None

                if section.lower().startswith('channels'):
                    channel = ctx.guild.get_channel(int(config[section][field]))
                    if channel is not None:
                        value = channel.mention
                    else:
                        value = f"`{config[section][field]}`"

                elif section.lower().startswith('roles'):
                    role = ctx.guild.get_role(int(config[section][field]))
                    if channel is not None:
                        value = role.mention
                    else:
                        value = f"`{config[section][field]}`"

                else:
                    value = config[section][field]

                config_embed.add_field(name=f"{field}:", value=value)

            embed_list.append(config_embed)
        await ctx.send(embeds=embed_list)


def setup(bot):
    bot.add_cog(Config(bot))
