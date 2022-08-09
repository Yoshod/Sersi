from dataclasses import dataclass
from dataclass_wizard import YAMLWizard

from configuration.channels import ConfigurationChannels
from configuration.emotes import ConfigurationEmotes
from configuration.guilds import ConfigurationGuilds
from configuration.invites import ConfigurationInvites
from configuration.opt_in_roles import ConfigurationOptInRoles
from configuration.permission_roles import ConfigurationPermissionRoles
from configuration.roles import ConfigurationRoles


# Defines the structure of the configuration file.
@dataclass
class Configuration(YAMLWizard):
    # The bot client token.
    token: str

    # The path/address to the database (server).
    database: str

    # The port on which to run the web server. NOTE: This is being considered for deprecation.
    port: int

    # The path, relative to the data folder, that contains the list of authors.
    # Expected to be a Markdown formatted document.
    author_list: str

    # The prefix used for the bot, aside from mentions.
    prefix: str

    # The game displayed as what the bot is playing.
    activity: str

    # Configuration related to channels.
    channels: ConfigurationChannels

    # Configuration related to roles.
    roles: ConfigurationRoles

    # Configuration related to opt-in roles for server members.
    opt_ins: ConfigurationOptInRoles

    # Configuration related to staff roles.
    staff_roles: ConfigurationPermissionRoles

    # Configuration related to emotes.
    emotes: ConfigurationEmotes

    # Configuration related to invites.
    invites: ConfigurationInvites

    # Configuration related to guilds.
    guilds: ConfigurationGuilds
