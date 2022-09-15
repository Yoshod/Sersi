from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class ConfigurationGuilds(YAMLWizard):
    # The guild ID of the main server.
    main: str


@dataclass
class ConfigurationInvites(YAMLWizard):
    # The invite link to the support server.
    adam_something_ban_reinvite: str

    # The invite link to the ban appealing server.
    ban_appeal_server: str


@dataclass
class ConfigurationOptInRoles(YAMLWizard):
    # The opt-in roles IDs saved as integers.

    gaming: int
    tech_compsci: int
    food_and_drink: int
    education: int
    art: int
    anime: int
    furry: int
    shillposting: int
    music: int
    photography: int


@dataclass
class ConfigurationPermissionRoles(YAMLWizard):
    # The permission roles IDs saved as integers.

    staff: int
    reformist: int
    ticket_support: int
    sersi_contributor: int
    trial_moderator: int
    moderator: int
    senior_moderator: int
    dark_moderator: int


@dataclass
class ConfigurationEmotes(YAMLWizard):
    # The emote, in "<:name:id>" format, used to declare success.
    success: str

    # The emote, in "<:name:id>" format, used to declare failure.
    fail: str


@dataclass
class ConfigurationRoles(YAMLWizard):
    # The role assigned to users sent into reformation.
    #
    # Any other roles the user had at that point will be removed.
    # They will be added back in case of a successful reformation.
    reformation: int

    # The role assigned to users successfully completing reformation.
    reformed: int

    # The role assigned to users under probation.
    probation: int

    # The role assigned to users which ask for moderation roles in chats.
    never_mod: int

    # The role assigned to any user joining the server and completing verification.
    civil_engineering_initiate: int

    # The role assigned to members who have recently joined.
    #
    # It is removed after 3 days have gone by.
    newbie: int


@dataclass
class ConfigurationCogs(YAMLWizard):
    # A list of cogs that should not be loaded.
    disabled: list[str] | None


@dataclass
class ConfigurationChannels(YAMLWizard):
    # Receives alerts regarding moderation pings and slurs.
    alert: int

    # Receives logged events, used mainly as a secondary audit log, aside from logging actions not audited by Discord's audit log.
    logging: int

    # Receives slur usage deemed as false positives.
    false_positives: int

    # Receives notifications about actions taken by moderators, e.g bans.
    mod_logs: int

    # TODO: find out what this does lol
    dm_forward: int

    # Receives notifications about errors.
    errors: int

    # Receives secret messages.
    secret: int

    # Used in reformation notifications for users sent into reformation to inform them of which channel to check out for more information.
    reformation_info: int

    # Receives notifications regarding members being sent into reformation, intended to start a conversation regarding them in the channel dedicated to discussion between reformist and staff.
    teachers_lounge: int

    # Receives notifications regarding members being sent into reformation, as a public ledger.
    reform_public_log: int

    # Receives notifications about submitted ban appeals.
    ban_appeals: int

    # The channel used for the photograph sharing feature.
    photography: int

    # The channel used for YouTube notifications.
    youtube: int


# Defines the structure of the configuration file.
@dataclass
class Configuration(YAMLWizard):
    # The bot client token.
    token: str
    prefix: str

    # The path, relative to the data folder, that contains the list of authors.
    # Expected to be a Markdown formatted document.
    author_list: str

    # The prefix used for the bot, aside from mentions.
    prefix: str

    # The game displayed as what the bot is playing.
    status: str

    # Configuration related to cogs.
    cogs: ConfigurationCogs

    # Configuration related to roles.
    roles: ConfigurationRoles

    # Configuration related to opt-in roles for server members.
    opt_ins: ConfigurationOptInRoles

    # Configuration related to staff roles.
    permission_roles: ConfigurationPermissionRoles

    # Configuration related to emotes.
    emotes: ConfigurationEmotes

    # Configuration related to invites.
    invites: ConfigurationInvites

    # Configuration related to guilds.
    guilds: ConfigurationGuilds

    channels: ConfigurationChannels
