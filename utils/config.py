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
    privacy_policy: str
    wiki_header: str
    minimum_star_count: int
    bot_id: int
    dev_mode: bool = False


@dataclass
class ConfigurationStaffChannels(YAMLWizard):
    alert: int
    false_positives: int
    mod_applications: int
    cet_applications: int
    age_verification: int
    compliance_review: int
    admin_review: int
    mod_lead_review: int
    mod_review: int
    mod_votes: int
    staff_votes: int
    cet_votes: int


@dataclass
class ConfigurationDevChannels(YAMLWizard):
    errors: int
    bug_reports: int
    feature_requests: int


@dataclass
class ConfigurationLoggingChannels(YAMLWizard):
    logging_category: int
    general: int
    mod: int
    tamper: int
    admin_ticket: int
    senior_ticket: int
    mod_ticket: int
    cet_ticket: int
    cet_lead_ticket: int
    deleted_messages: int
    roles: int
    deleted_images: int
    edited_messages: int
    join_leave: int
    channels: int
    guild: int
    user_chanes: int
    ban_unban: int
    voice: int
    automod: int


@dataclass
class ConfigurationReformationChannels(YAMLWizard):
    info: int
    teachers_lounge: int
    public_log: int


@dataclass
class ConfigurationSuggestionsChannels(YAMLWizard):
    discussion: int
    voting: int
    review: int


@dataclass
class ConfigurationMiscChannels(YAMLWizard):
    photography: int
    afk_voice: int
    starboard: int


@dataclass
class ConfigurationChannels(YAMLWizard):
    staff: ConfigurationStaffChannels
    dev: ConfigurationDevChannels
    log: ConfigurationLoggingChannels
    reform: ConfigurationReformationChannels
    suggestions: ConfigurationSuggestionsChannels
    misc: ConfigurationMiscChannels


@dataclass
class ConfigurationStaffRoles(YAMLWizard):
    base: int
    admin: int
    trial_mod: int
    mod: int
    mod_lead: int
    available_mod: int
    cet: int
    cet_lead: int
    compliance: int
    sersi_contributor: int
    honourable_member: int


@dataclass
class ConfigurationAccessRoles(YAMLWizard):
    basic: int
    newbie: int
    adult: int


@dataclass
class ConfigurationReformationRoles(YAMLWizard):
    reformist: int
    inmate: int
    reformed: int


@dataclass
class ConfigurationMiscRoles(YAMLWizard):
    probation: int
    never_mod: int
    adult_verified: int


@dataclass
class ConfigurationRoles(YAMLWizard):
    staff: ConfigurationStaffRoles
    access: ConfigurationAccessRoles
    reform: ConfigurationReformationRoles
    misc: ConfigurationMiscRoles


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


@dataclass
class ConfigurationAutomoderation(YAMLWizard):
    max_mentions: int


@dataclass(frozen=True)
class Configuration(YAMLWizard):
    bot: ConfigurationBot
    channels: ConfigurationChannels
    ignored_channels: dict[str, int]
    ignored_categories: list[str]
    roles: ConfigurationRoles
    opt_in_roles: dict[str, int]
    punishment_roles: dict[str, int]
    level_roles: dict[int, int]
    emotes: ConfigurationEmotes
    guilds: ConfigurationGuilds
    voting: dict[str, VoteType]
    automoderation: ConfigurationAutomoderation


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
