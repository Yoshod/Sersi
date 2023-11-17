import nextcord

from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration, Configurator
from utils.perms import (
    permcheck,
    is_sersi_contributor,
    is_staff,
    is_dark_mod,
    is_cet_lead,
)


class Config(commands.Cog):
    def __init__(
        self, bot: commands.Bot, config: Configurator | Configuration, data_folder: str
    ):
        self.bot = bot
        self.config = config
        self.data_folder = data_folder
        self.config_file = f"{data_folder}/config.yaml"

    def set_config(self, config_section, setting, value):
        self.config.load()

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
                    name: eval_category(name) for name in self.config.ignored_categories
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
                    name: eval_role(id) for name, id in self.config.opt_in_roles.items()
                }
            case "emotes":
                config_dict = {
                    name: value for name, value in self.config.emotes.__dict__.items()
                }
            case "guilds":
                config_dict = {
                    name: eval_guild(id)
                    for name, id in self.config.guilds.__dict__.items()
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
        description="Select a channel to set in config",
    )
    async def set_channel(
        self,
        interaction: nextcord.Interaction,
        setting: str = nextcord.SlashOption(
            description="Setting to set",
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="Channel to set"
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.set_config("channels", setting, channel)

        await interaction.response.send_message(
            f"{self.config.emotes.success} Channel set to {channel.mention} for `{setting}`."
        )

    @set_channel.on_autocomplete("setting")
    async def set_channel_setting(
        self, interaction: nextcord.Interaction, setting: str
    ):
        if not is_dark_mod(interaction.user):
            return

        await interaction.response.send_autocomplete(
            [
                name
                for name in self.config.channels.__dict__.keys()
                if name.startswith(setting or "")
            ][:25]
        )

    @configuration.subcommand()
    async def ignored(self, interaction: nextcord.Interaction):
        pass

    @ignored.subcommand(description="Select a channel to add to ignored channels")
    async def add_channel(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="Channel to add"
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.config.load()
        if channel.id in self.config.ignored_channels.values():
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Channel {channel.mention} already in ignored channels."
            )
            return
        self.config.ignored_channels[channel.name] = channel.id
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Channel {channel.mention} added to ignored channels."
        )

    @ignored.subcommand(description="Select a channel to remove from ignored channels")
    async def remove_channel(
        self,
        interaction: nextcord.Interaction,
        channel: str = nextcord.SlashOption(
            description="Channel to remove",
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.config.load()
        if channel not in self.config.ignored_channels:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Channel {channel} not in ignored channels."
            )
            return
        self.config.ignored_channels.pop(channel)
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Channel {channel} removed from ignored channels."
        )

    @remove_channel.on_autocomplete("channel")
    async def remove_channel_id(self, interaction: nextcord.Interaction, channel: str):
        if not is_dark_mod(interaction.user):
            return

        await interaction.response.send_autocomplete(
            [
                name
                for name in self.config.ignored_channels
                if name.startswith(channel or "")
            ][:25]
        )

    @ignored.subcommand(description="Select a category to add to ignored categories")
    async def add_category(
        self,
        interaction: nextcord.Interaction,
        category: nextcord.CategoryChannel = nextcord.SlashOption(
            description="Category to add"
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.config.load()
        if category.name in self.config.ignored_categories:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Category {category.mention} already in ignored categories."
            )
            return
        self.config.ignored_categories.append(category.name)
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Category {category.mention} added to ignored categories."
        )

    @ignored.subcommand(
        description="Select a category to remove from ignored categories"
    )
    async def remove_category(
        self,
        interaction: nextcord.Interaction,
        category: str = nextcord.SlashOption(
            description="Category to remove",
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.config.load()
        if category not in self.config.ignored_categories:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Category {category} not in ignored categories."
            )
            return
        self.config.ignored_categories.remove(category)
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Category {category} removed from ignored categories."
        )

    @remove_category.on_autocomplete("category")
    async def remove_category_name(
        self, interaction: nextcord.Interaction, category: str
    ):
        if not is_dark_mod(interaction.user):
            return

        await interaction.response.send_autocomplete(
            [
                name
                for name in self.config.ignored_categories
                if name.startswith(category or "")
            ][:25]
        )

    @configuration.subcommand(description="Select a role to set in config")
    async def set_role(
        self,
        interaction: nextcord.Interaction,
        setting: str = nextcord.SlashOption(
            description="Setting to set",
        ),
        role: nextcord.Role = nextcord.SlashOption(description="Role to set"),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.set_config("roles", setting, role)

        await interaction.response.send_message(
            f"{self.config.emotes.success} Role set to {role.mention} for `{setting}`."
        )

    @set_role.on_autocomplete("setting")
    async def set_role_setting(self, interaction: nextcord.Interaction, setting):
        if not is_dark_mod(interaction.user):
            return

        await interaction.response.send_autocomplete(
            [
                name
                for name in self.config.roles.__dict__.keys()
                if name.startswith(setting or "")
            ][:25]
        )

    @configuration.subcommand(description="Select a role to set as permission role")
    async def set_permission_role(
        self,
        interaction: nextcord.Interaction,
        setting: str = nextcord.SlashOption(
            description="Setting to set",
        ),
        role: nextcord.Role = nextcord.SlashOption(description="Role to set"),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.set_config("permission_roles", setting, role)

        await interaction.response.send_message(
            f"{self.config.emotes.success} Role set to {role.mention} for `{setting}`."
        )

    @set_permission_role.on_autocomplete("setting")
    async def set_permission_role_setting(
        self, interaction: nextcord.Interaction, setting: str
    ):
        if not is_dark_mod(interaction.user):
            return

        await interaction.response.send_autocomplete(
            [
                name
                for name in self.config.permission_roles.__dict__.keys()
                if name.startswith(setting or "")
            ][:25]
        )

    @configuration.subcommand()
    async def punishment_roles(self, interaction: nextcord.Interaction):
        pass

    @punishment_roles.subcommand(
        name="add", description="Select a role to add to punishment roles"
    )
    async def add_punishment_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(description="Role to add"),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.config.load()
        if role.id in self.config.punishment_roles.values():
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Role {role.mention} already in punishment roles."
            )
            return
        self.config.punishment_roles[role.name] = role.id
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Role {role.mention} added to punishment roles."
        )

    @punishment_roles.subcommand(
        name="remove", description="Select a role to remove from punishment roles"
    )
    async def remove_punishment_role(
        self,
        interaction: nextcord.Interaction,
        role: str = nextcord.SlashOption(description="Role to remove"),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        self.config.load()
        if role not in self.config.punishment_roles:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Role {role} not in punishment roles."
            )
            return
        self.config.punishment_roles.pop(role)
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Role {role} removed from punishment roles."
        )

    @remove_punishment_role.on_autocomplete("role")
    async def remove_punishment_role_name(
        self, interaction: nextcord.Interaction, role: str
    ):
        if not is_dark_mod(interaction.user):
            return

        await interaction.response.send_autocomplete(
            [
                name
                for name in self.config.punishment_roles
                if name.startswith(role or "")
            ][:25]
        )

    @configuration.subcommand()
    async def opt_in_roles(self, interaction: nextcord.Interaction):
        pass

    @opt_in_roles.subcommand(
        name="add", description="Select a role to add to opt in roles"
    )
    async def add_opt_in_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(description="Role to add"),
    ):
        if not await permcheck(interaction, is_cet_lead):
            return

        self.config.load()
        if role.id in self.config.opt_in_roles.values():
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Role {role.mention} already in opt in roles."
            )
            return
        self.config.opt_in_roles[role.name] = role.id
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Role {role.mention} added to opt in roles."
        )

    @opt_in_roles.subcommand(
        name="remove", description="Select a role to remove from opt in roles"
    )
    async def remove_opt_in_role(
        self,
        interaction: nextcord.Interaction,
        role: str = nextcord.SlashOption(description="Role to remove"),
    ):
        if not await permcheck(interaction, is_cet_lead):
            return

        self.config.load()
        if role not in self.config.opt_in_roles:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Role {role} not in opt in roles."
            )
            return
        self.config.opt_in_roles.pop(role)
        self.config.save()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Role {role} removed from opt in roles."
        )

    @remove_opt_in_role.on_autocomplete("role")
    async def remove_opt_in_role_name(
        self, interaction: nextcord.Interaction, role: str
    ):
        if not is_cet_lead(interaction.user):
            return

        await interaction.response.send_autocomplete(
            [name for name in self.config.opt_in_roles if name.startswith(role or "")][
                :25
            ]
        )

    @configuration.subcommand(description="Reloads bot config from config.yaml")
    async def reload(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_sersi_contributor):
            return

        self.config.load()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Config reloaded."
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Config(bot, kwargs["config"], kwargs["data_folder"]))
