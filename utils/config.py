from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


@dataclass
class ConfigurationBot(YAMLWizard):
    prefix: str
    status: str
    port: int
    minimum_caps_length: int
    version: str
    git_url: str
    authors: list[str]
    dev_mode: bool = False
    wiki_header: str


@dataclass
class ConfigurationChannels(YAMLWizard):
    # moderator sided channels
    alert: int  # Receives alerts regarding moderation pings and slurs.
    logging: int
    false_positives: int
    mod_logs: int
    dm_forward: int
    mod_applications: int
    cet_applications: int
    ageverification: int
    compliance_review: int
    dark_mod_review: int
    senior_mod_review: int
    moderator_review: int
    moderation_votes: int
    staff_votes: int
    cet_votes: int

    # debugging channels
    errors: int

    # user sided channels
    photography: int

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
    cet_ticket_logs: int
    cet_lead_ticket_logs: int
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

    # suggestions
    suggestion_discussion: int
    suggestion_voting: int
    suggestion_review: int


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

    blank: str


@dataclass
class ConfigurationGuilds(YAMLWizard):
    # The guild ID of the main server.
    main: int
    errors: int


@dataclass
class VoteType(YAMLWizard):
    name: str
    action: str

    group: str = "mod"
    duration: int = 72
    threshold: int = 3
    difference: int = 1

    supermajority: bool = False
    comment_required: bool = True
    end_on_threshold: bool = True


@dataclass(frozen=True)
class Configuration(YAMLWizard):
    bot: ConfigurationBot
    channels: ConfigurationChannels
    ignored_channels: dict[str, int]
    ignored_categories: list[str]
    roles: ConfigurationRoles
    opt_in_roles: dict[str, int]
    permission_roles: ConfigurationPermissionRoles
    punishment_roles: dict[str, int]
    level_roles: dict[int, int]
    emotes: ConfigurationEmotes
    guilds: ConfigurationGuilds
    voting: dict[str, VoteType]


class Configurator:
    config: Configuration = None
    path: str

    def __init__(self, path: str):
        self.path = path
        self.load()

    def load(self):
        self.config = Configuration.from_yaml_file(self.path)

    def save(self):
        self.config.to_yaml_file(self.path)

    def __getattr__(self, __name):
        return getattr(self.config, __name)

    def __setattr__(self, __name, __value):
        if self.config and hasattr(self.config, __name):
            raise AttributeError(
                "Overriding base configuration categories is not allowed, modify their contentent instead."
            )
        else:
            super().__setattr__(__name, __value)
