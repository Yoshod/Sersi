import configparser
import nextcord
import re

from nextcord.ext import commands
from nextcord.ui import Button, View
from baseutils import *


class Config(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cb_create_proceed(self, interaction):
        if not interaction.user == interaction.message.reference.cached_message.author:
            return

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

    async def cb_cancel(self, interaction):
        if not interaction.user == interaction.message.reference.cached_message.author:
            return

        await interaction.message.delete()
        await interaction.message.reference.cached_message.reply("Action canceled!")

    @commands.command()
    async def setsetting(self, ctx, section, setting, value):
        section = section.upper()

        # sections only modifiable by dark moderators
        if not is_dark_mod(ctx.author) and section in ["CHANNELS", "ROLES", "BOT"]:
            await ctx.send(f"<:sersifail:979070135799279698> Only dark moderators can modify settings in this section!")
            return

        if not is_mod(ctx.author):
            await ctx.reply(f"<:sersifail:979070135799279698> Only moderators can modify configuration")
            return

        if setting_present(section, setting):

            if 'channels' in section.lower() or 'roles' in section.lower():
                value = re.sub(r"[^0-9]*", "", value)

            set_config(section, setting, value)

            await ctx.send(f"<:sersisuccess:979066662856822844> `[{section}] {setting}` has been set to `{value}`")

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

            btn_confirm = Button(label="Proceed")
            btn_confirm.callback = self.cb_create_proceed
            btn_cancel = Button(label="Cancel")
            btn_cancel.callback = self.cb_cancel

            btn_view = View()
            btn_view.add_item(btn_confirm)
            btn_view.add_item(btn_cancel)

            await ctx.reply(embed=dialog_embed, view=btn_view)

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
        if not is_staff(ctx.author) or not is_sersi_contrib(ctx.author):
            await ctx.reply("<:sersifail:979070135799279698> Insufficient permission!")
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
