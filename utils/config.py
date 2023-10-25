from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class ConfigurationDatafiles(YAMLWizard):
    author_list: str
    keyfile: str
    slurfile: str
    goodwordfile: str
    blacklist: str
    casedetails: str
    casehistory: str
    gifblacklist: str
    secret_dms: str
    secret_mutes: str
    reform_iter: str
    reformation_cases: str
    watchlist: str
    ticketers: str
    video_history: str
    alert_logs: str
    alert_csv: str
    sersi_db: str


@dataclass
class ConfigurationBot(YAMLWizard):
    prefix: str
    status: str
    port: int
    minimum_caps_length: int
    version: str
    git_url: str
    authors: list[str]


@dataclass
class ConfigurationChannels(YAMLWizard):
    # moderator sided channels
    alert: int  # Receives alerts regarding moderation pings and slurs.
    logging: int
    false_positives: int
    mod_logs: int
    ban_appeals: int
    dm_forward: int
    mod_applications: int
    cet_applications: int
    internalfeedback: int
    timeoutappeals: int
    ageverification: int
    compliance_review: int
    dark_mod_review: int
    senior_mod_review: int
    moderator_review: int

    # debugging channels
    errors: int

    # user sided channels
    secret: int
    photography: int
    youtube: int
    video_discussion: int

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
    deleted_messages: int
    role_logs: int
    deleted_messages: int
    deleted_images: int
    edited_messages: int
    joinleave: int
    channel_logs: int
    guild_logs: int
    user_chanes: int
    ban_unban: int
    voice_logs: int
    automod_logs: int


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

    # former moderator role
    honourable_member: int

    adult_access: int
    adult_verified: int


@dataclass
class ConfigurationPermissionRoles(YAMLWizard):
    # The permission roles IDs saved as integers.

    staff: int
    reformist: int
    ticket_support: int
    sersi_contributor: int
    cet: int
    cet_lead: int
    compliance: int

    # AMAB: all mods are bastards ;)
    trial_moderator: int
    moderator: int
    senior_moderator: int
    dark_moderator: int  # AKA: super-duper mega administrators


@dataclass
class ConfigurationEmotes(YAMLWizard):
    # The emote, in "<:name:id>" format, used to declare success.
    success: str

    # The emote, in "<:name:id>" format, used to declare failure.
    fail: str

    inherit: str


@dataclass
class ConfigurationInvites(YAMLWizard):
    # The reinvite for people unbanned from ASC
    adam_something_ban_reinvite: str

    # The invite link to the ban appealing server.
    ban_appeal_server: str


@dataclass
class ConfigurationGuilds(YAMLWizard):
    # The guild ID of the main server.
    main: int
    errors: int


@dataclass(frozen=True)
class Configuration(YAMLWizard):
    datafiles: ConfigurationDatafiles
    bot: ConfigurationBot
    channels: ConfigurationChannels
    ignored_channels: dict[str, int]
    ignored_categories: list[str]
    roles: ConfigurationRoles
    opt_in_roles: dict[str, int]
    permission_roles: ConfigurationPermissionRoles
    punishment_roles: dict[str, int]
    emotes: ConfigurationEmotes
    invites: ConfigurationInvites
    guilds: ConfigurationGuilds
