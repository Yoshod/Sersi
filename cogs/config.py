import configparser
import nextcord
import re

from nextcord.ext import commands
from baseutils import ConfirmView
from configutils import get_config, get_config_int, setting_present, set_config
from permutils import permcheck, is_sersi_contrib, is_staff, is_mod, is_dark_mod


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')

    async def cb_create_proceed(self, interaction):
        section, setting, value = "", "", ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "Section":
                section = field.value
            elif field.name == "Setting":
                setting = field.value
            elif field.name == "Value":
                value = field.value

        set_config(section, setting, value)

        embed = nextcord.Embed(
            title="Add new setting",
            description="New setting added to Sesi configuration!",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embed.add_field(name="Section", value=section)
        embed.add_field(name="Setting", value=setting)
        embed.add_field(name="Value", value=value)
        await interaction.message.edit(embed=embed, view=None)

        # logging
        log_embed = nextcord.Embed(
            title="New Configuration Setting Added",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        log_embed.add_field(name="Staff Member:", value=interaction.user.mention, inline=False)
        log_embed.add_field(name="Section:", value=section, inline=False)
        log_embed.add_field(name="Setting:", value=setting, inline=False)
        log_embed.add_field(name="Value:", value=value, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

    @commands.command(aliases=['set'])
    async def setsetting(self, ctx, section, setting, value):
        section = section.upper()

        # sections only modifiable by dark moderators
        if not await permcheck(ctx, is_dark_mod):
            return

        if setting_present(section, setting):

            if 'channels' in section.lower() or 'roles' in section.lower():
                value = re.sub(r"[^0-9]*", "", value)

            prev_value = get_config(section, setting, value)
            set_config(section, setting, value)

            # logging
            log_embed = nextcord.Embed(
                title="Configuration setting changed",
                colour=nextcord.Color.from_rgb(237, 91, 6))
            log_embed.add_field(name="Staff Member:", value=ctx.author.mention, inline=False)
            log_embed.add_field(name="Section:", value=section, inline=False)
            log_embed.add_field(name="Setting:", value=setting, inline=False)
            log_embed.add_field(name="Previous Value:", value=prev_value, inline=False)
            log_embed.add_field(name="New Value:", value=value, inline=False)

            channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
            await channel.send(embed=log_embed)

            await ctx.send(f"{self.sersisuccess} `[{section}] {setting}` has been set to `{value}`")

            if section == "BOT":
                await ctx.invoke(self.bot.get_command('reloadbot'))

        else:
            dialog_embed = nextcord.Embed(
                title="Add new setting",
                description="Specified setting does not exist, do you wish to create it?",
                color=nextcord.Color.from_rgb(237, 91, 6))
            dialog_embed.add_field(name="Section", value=section)
            dialog_embed.add_field(name="Setting", value=setting)
            dialog_embed.add_field(name="Value", value=value)

            await ConfirmView(self.cb_create_proceed).send_as_reply(ctx, embed=dialog_embed)

    @commands.command()
    async def reloadbot(self, ctx):
        if not await permcheck(ctx, is_mod):
            return

        await self.bot.change_presence(activity=nextcord.Game(get_config("BOT", "status")))
        self.bot.command_prefix = get_config("BOT", "command prefix")
        await ctx.send(f"{self.sersisuccess} Bot reloaded.")

    @commands.command(aliases=['config', 'conf'])
    async def configuration(self, ctx, *args):
        if not is_staff(ctx.author) or not is_sersi_contrib(ctx.author):
            await ctx.reply(f"{self.sersifail} Insufficient permission!")
            return

        if len(args) == 4:
            if args[0].upper() == "SET":        # yes this does need to be stacked that way, no you can't just 'and' the two conditions.
                await ctx.invoke(self.bot.get_command('setsetting'), section=args[1], setting=args[2], value=args[3])
                return

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

                if 'channels' in section.lower():
                    channel = ctx.guild.get_channel(int(config[section][field]))
                    if channel is not None:
                        value = channel.mention
                    else:
                        value = f"`{config[section][field]}`"

                elif 'roles' in section.lower():
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
