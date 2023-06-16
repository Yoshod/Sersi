import nextcord
import yaml

from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.base import sanitize_mention
from utils.config import Configuration
from utils.perms import permcheck, is_sersi_contrib, is_staff
from utils.cogs import reload_all_cogs


class Config(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration, data_folder: str):
        self.bot = bot
        self.config = config
        self.data_folder = data_folder
        self.config_file = f"{data_folder}/config.yaml"

    def set_config(self, config_section, setting, value):
        with open(self.config_file, "r") as file:
            config_dict = yaml.safe_load(file)

        # hard casting any IDs to integers now
        if "channels" in config_section.lower() or "roles" in config_section.lower():
            value = int(value)

        config_dict[config_section][setting] = value

        with open(self.config_file, "w") as file:
            yaml.dump(config_dict, file)

        # self.config = Configuration.from_yaml_file(self.yaml_file)

    async def _reload_bot(self):
        self.config = Configuration.from_yaml_file(self.config_file)
        await reload_all_cogs(
            self.bot, config=self.config, data_folder=self.data_folder
        )

        self.bot.command_prefix = self.config.bot.prefix
        await self.bot.change_presence(activity=nextcord.Game(self.config.bot.status))

    @nextcord.slash_command(
        dm_permission=False, guild_ids=[977377117895536640, 856262303795380224]
    )
    async def config(
        self,
        interaction: nextcord.Interaction,
    ):
        pass

    @config.subcommand(description="Read settings from config")
    async def get_setting(
        self,
        interaction: nextcord.Interaction,
        config_section: str = nextcord.SlashOption(required=False, name="section"),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer()

        with open(self.config_file, "r") as file:
            config = yaml.safe_load(file)

        if config_section:
            if config_section in config:
                config_embed = SersiEmbed(
                    title=config_section,
                )

                for field in config[config_section]:

                    if "channels" in config_section.lower():
                        channel: nextcord.abc.GuildChannel = (
                            interaction.guild.get_channel(config[config_section][field])
                        )
                        if channel is not None:
                            value: str = channel.mention
                        else:
                            value: str = f"`{config[config_section][field]}`"

                    elif "roles" in config_section.lower():
                        role: nextcord.Role = interaction.guild.get_role(
                            config[config_section][field]
                        )
                        if role is not None:
                            value: str = role.mention
                        else:
                            value: str = f"`{config[config_section][field]}`"

                    else:
                        value: str = config[config_section][field]

                    config_embed.add_field(name=f"{field}:", value=value)

                await interaction.followup.send(embed=config_embed)
            else:
                await interaction.send(
                    f"Section {config_section} is not present in configuration!"
                )

        else:
            config_embed = SersiEmbed(
                title="Sersi Configuration",
                description="type /config [section] to display section settings",
            )

            for section in config:
                config_embed.add_field(
                    name=f"{section}:", value="`" + "`\n`".join(config[section]) + "`"
                )

            await interaction.followup.send(embed=config_embed)

    @config.subcommand(
        description="set a setting to a value",
    )
    async def set_setting(
        self,
        interaction: nextcord.Interaction,
        section: str = nextcord.SlashOption(
            description="the section the setting belongs to"
        ),
        setting: str = nextcord.SlashOption(description="the name of the setting"),
        value: str = nextcord.SlashOption(description="the value to set"),
    ):
        if not await permcheck(interaction, is_sersi_contrib):
            return

        await interaction.response.defer()

        section = section.lower()
        with open(self.config_file, "r") as file:
            config = yaml.safe_load(file)

        if "channels" in section.lower() or "roles" in section.lower():
            value = sanitize_mention(value)

        if setting in config[section]:
            prev_value = config[section][setting]
            self.set_config(section, setting, value)

            # logging
            await interaction.guild.get_channel(self.config.channels.logging).send(
                embed=SersiEmbed(
                    title="Configuration setting changed",
                    fields={
                        "Staff Member:": interaction.user.mention,
                        "Section:": section,
                        "Setting:": setting,
                        "Previous Value:": prev_value,
                        "New Value:": value,
                    },
                ).set_author(
                    name=interaction.user, icon_url=interaction.user.display_avatar.url
                )
            )

            await interaction.send(
                f"{self.config.emotes.success} `[{section}] {setting}` has been set to `{value}`"
            )

            await self._reload_bot()
            await interaction.followup.send(
                f"{self.config.emotes.success} Bot reloaded."
            )

        else:

            await interaction.send(
                embed=nextcord.Embed(
                    title="Setting not found.",
                    color=nextcord.Color.from_rgb(237, 91, 6),
                )
            )

    @config.subcommand(description="Reloads all cogs of the bot")
    async def reload(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contrib):
            return

        await interaction.response.defer()
        await self._reload_bot()

        await interaction.followup.send(f"{self.config.emotes.success} Bot reloaded.")


def setup(bot, **kwargs):
    bot.add_cog(Config(bot, kwargs["config"], kwargs["data_folder"]))
