from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class ConfigurationDatafiles(YAMLWizard):
    author_list:    str
    keyfile:        str
    slurfile:       str
    goodwordfile:   str


@dataclass
class ConfigurationBot(YAMLWizard):
    prefix: str
    status: str


@dataclass
class ConfigurationChannels(YAMLWizard):

    # moderator sided channels
    alert: int  # Receives alerts regarding moderation pings and slurs.
    logging: int
    false_positives: int
    mod_logs: int
    ban_appeals: int
    dm_forward: int

    # debugging channels
    errors: int

    # user sided channels
    secret: int
    photography: int
    youtube: int

    # reformation related channels
    reformation_info: int
    teachers_lounge: int
    reform_public_log: int

    # logging
    logging_category: int
    tamper_logs: int
    admin_ticket_logs: int
    senior_ticket_logs: int
    mod_ticket_logs: int
    verification_ticket_logs: int


@dataclass
class ConfigurationRoles(YAMLWizard):

    # reformation roles
    reformation: int
    reformed: int

    # The role assigned to users under probation.
    probation: int

    # joke roles
    never_mod: int

    # basic human rights role
    civil_engineering_initiate: int

    # newbie roles
    newbie: int


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

    # AMAB: all mods are bastards ;)
    trial_moderator: int
    moderator: int
    senior_moderator: int
    dark_moderator: int    # AKA: super-duper mega administrators


@dataclass
class ConfigurationEmotes(YAMLWizard):
    # The emote, in "<:name:id>" format, used to declare success.
    success: str

    # The emote, in "<:name:id>" format, used to declare failure.
    fail: str


@dataclass
class ConfigurationInvites(YAMLWizard):
    # The reinvite for people unbanned from ASC
    adam_something_ban_reinvite: str

    # The invite link to the ban appealing server.
    ban_appeal_server: str


@dataclass
class ConfigurationGuilds(YAMLWizard):
    # The guild ID of the main server.
    main: str


@dataclass(frozen=True)
class Configuration(YAMLWizard):

    datafiles: ConfigurationDatafiles
    bot: ConfigurationBot
    channels: ConfigurationChannels
    roles: ConfigurationRoles
    opt_ins: ConfigurationOptInRoles
    permission_roles: ConfigurationPermissionRoles
    emotes: ConfigurationEmotes
    invites: ConfigurationInvites
    guilds: ConfigurationGuilds
