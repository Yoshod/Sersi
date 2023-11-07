import nextcord
import yaml

from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.base import sanitize_mention
from utils.config import Configuration, Configurator
from utils.perms import permcheck, is_sersi_contributor, is_staff
from utils.cogs import reload_all_cogs


class Config(commands.Cog):
    def __init__(
        self, bot: commands.Bot, config: Configurator | Configuration, data_folder: str
    ):
        self.bot = bot
        self.config = config
        self.data_folder = data_folder
        self.config_file = f"{data_folder}/config.yaml"

    def set_config(self, config_section, setting, value):
        match value:
            case (
                nextcord.TextChannel()
                | nextcord.VoiceChannel()
                | nextcord.CategoryChannel()
                | nextcord.Role()
            ):
                value = value.id

        setattr(getattr(self.config, config_section), setting, value)

        self.config.save()

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        name="config",
        description="Sersi configuration",
    )
    async def configuration(
        self,
        interaction: nextcord.Interaction,
    ):
        pass

    @configuration.subcommand(description="Read settings from config")
    async def list(
        self,
        interaction: nextcord.Interaction,
        config_section: str = nextcord.SlashOption(
            name="section",
            choices=[
                "channels",
                "ignored_channels",
                "ignored_categories",
                "roles",
                "permission_roles",
                "punishment_roles",
                "opt_in_roles",
                "emotes",
                "guilds",
            ],
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer()

        def eval_category(name: str):
            category = nextcord.utils.get(interaction.guild.categories, name=name)
            if category:
                return category.mention
            else:
                return f"`{name}`"

        def eval_channel(id: int):
            channel = interaction.guild.get_channel(id)
            if channel:
                return channel.mention
            else:
                return f"`{id}`"
            
        def eval_guild(id: int):
            guild = self.bot.get_guild(id)
            if guild:
                return f"{guild.name} `{id}`"
            else:
                return f"`{id}`"
        
        def eval_role(id: int):
            role = interaction.guild.get_role(id)
            if role:
                return role.mention
            else:
                return f"`{id}`"

        config_dict = {}
        match config_section:
            case "channels":
                config_dict = {
                    name: eval_channel(id)
                    for name, id in self.config.channels.__dict__.items()
                }
            case "ignored_channels":
                config_dict = {
                    name: eval_channel(id)
                    for name, id in self.config.ignored_channels.items()
                }
            case "ignored_categories":
                config_dict = {
                    name: eval_category(name)
                    for name in self.config.ignored_categories
                }
            case "roles":
                config_dict = {
                    name: eval_role(id)
                    for name, id in self.config.roles.__dict__.items()
                }
            case "permission_roles":
                config_dict = {
                    name: eval_role(id)
                    for name, id in self.config.permission_roles.__dict__.items()
                }
            case "punishment_roles":
                config_dict = {
                    name: eval_role(id)
                    for name, id in self.config.punishment_roles.items()
                }
            case "opt_in_roles":
                config_dict = {
                    name: eval_role(id)
                    for name, id in self.config.opt_in_roles.items()
                }
            case "emotes":
                config_dict = {
                    name: value for name, value in self.config.emotes.__dict__.items()
                }
            case "guilds":
                config_dict = {
                    name: eval_guild(id) for name, id in self.config.guilds.__dict__.items()
                }
            case _:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} Section `{config_section}` not available."
                )
                return

        embeds: list[nextcord.Embed] = []

        for field, value in config_dict.items():
            if not embeds or len(embeds[-1].fields) == 24:
                embeds.append(SersiEmbed(title=config_section))

            embeds[-1].add_field(name=f"{field}:", value=value)

        await interaction.followup.send(embeds=embeds)

    @configuration.subcommand(
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
        if not await permcheck(interaction, is_sersi_contributor):
            return
        
        await interaction.response.send_message("WIP", ephemeral=True)
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

    @configuration.subcommand(description="Reloads bot config from config.yaml")
    async def reload(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        self.config.load()

        await interaction.followup.send(
            f"{self.config.emotes.success} Config reloaded."
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Config(bot, kwargs["config"], kwargs["data_folder"]))
