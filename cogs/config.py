import nextcord
import yaml

from nextcord.ext import commands
from baseutils import sanitize_mention, ConfirmView
from configutils import Configuration
from permutils import permcheck, is_sersi_contrib, is_staff, is_mod, is_dark_mod


class Config(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration, data_folder: str):
        self.bot = bot
        self.config = config
        self.yaml_file = f"{data_folder}/config.yaml"
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    def set_config(self, section, setting, value):
        with open(self.yaml_file, 'r') as file:
            config_dict = yaml.safe_load(file)

        # hard casting any IDs to integers now
        if 'channels' in section.lower() or 'roles' in section.lower():
            value = int(value)

        config_dict[section][setting] = value

        with open(self.yaml_file, 'w') as file:
            yaml.dump(config_dict, file)

        self.config = Configuration.from_yaml_file(self.yaml_file)

    async def cb_create_proceed(self, interaction):
        section, setting, value = "", "", ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "Section":
                section = field.value
            elif field.name == "Setting":
                setting = field.value
            elif field.name == "Value":
                value = field.value

        self.set_config(section, setting, value)

        embed = nextcord.Embed(
            title="Add new setting",
            description="New setting added to Sersi configuration!",
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

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

    @commands.command(aliases=['set'])
    async def setsetting(self, ctx, section, setting, value):
        section = section.lower()
        with open(self.yaml_file, 'r') as file:
            config = yaml.safe_load(file)

        # sections only modifiable by dark moderators
        if not await permcheck(ctx, is_dark_mod):
            return

        if 'channels' in section.lower() or 'roles' in section.lower():
            value = sanitize_mention(value)

        if setting in config[section]:

            prev_value = config[section][setting]
            self.set_config(section, setting, value)

            # logging
            log_embed = nextcord.Embed(
                title="Configuration setting changed",
                colour=nextcord.Color.from_rgb(237, 91, 6))
            log_embed.add_field(name="Staff Member:", value=ctx.author.mention, inline=False)
            log_embed.add_field(name="Section:", value=section, inline=False)
            log_embed.add_field(name="Setting:", value=setting, inline=False)
            log_embed.add_field(name="Previous Value:", value=prev_value, inline=False)
            log_embed.add_field(name="New Value:", value=value, inline=False)

            channel = ctx.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=log_embed)

            await ctx.send(f"{self.sersisuccess} `[{section}] {setting}` has been set to `{value}`")

            if section == "bot":
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

        self.bot.command_prefix = self.config.prefix
        await self.bot.change_presence(activity=nextcord.Game(self.config.status))
        await ctx.send(f"{self.sersisuccess} Bot reloaded.")

    @commands.command(aliases=['config', 'conf'])
    async def configuration(self, ctx, *args):
        if not is_staff(ctx.author) and not is_sersi_contrib(ctx.author):   # either is fine
            await ctx.reply(f"{self.sersifail} Insufficient permission!")
            return

        with open(self.yaml_file, 'r') as file:
            config = yaml.safe_load(file)

        if len(args) == 4:
            if args[0].upper() == "SET":        # yes this does need to be stacked that way, no you can't just 'and' the two conditions.
                await ctx.invoke(self.bot.get_command('setsetting'), section=args[1], setting=args[2], value=args[3])
                return

        elif len(args) == 1:
            section = args[0].lower()

            if section in config:
                config_embed = nextcord.Embed(
                    title=section,
                    color=nextcord.Color.from_rgb(237, 91, 6))

                for field in config[section]:
                    value = None

                    if 'channels' in section.lower():
                        channel = ctx.guild.get_channel(config[section][field])
                        if channel is not None:
                            value = channel.mention
                        else:
                            value = f"`{config[section][field]}`"

                    elif 'roles' in section.lower():
                        role = ctx.guild.get_role(config[section][field])
                        if role is not None:
                            value = role.mention
                        else:
                            value = f"`{config[section][field]}`"

                    else:
                        value = config[section][field]

                    config_embed.add_field(name=f"{field}:", value=value)

                await ctx.send(embed=config_embed)
                return
            else:
                await ctx.send(f"Section {section} is not present in configuration!")

        elif len(args) != 0:
            await ctx.send(f"Invalid argument: `{args}`")

        config_embed = nextcord.Embed(
            title="Sersi Configuration",
            description="type s!conf|ig|uration [section] to display section settings",
            color=nextcord.Color.from_rgb(237, 91, 6))

        for section in config:
            config_embed.add_field(name=f"{section}:", value='`' + "`\n`".join(config[section]) + '`')

        await ctx.send(embed=config_embed)


def setup(bot, **kwargs):
    bot.add_cog(Config(bot, kwargs["config"], kwargs["data_folder"]))
