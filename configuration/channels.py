from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to channels.
@dataclass
class ConfigurationChannels(YAMLWizard):
    # Receives alerts regarding moderation pings and slurs.
    alert: int

    # Receives logged events, used mainly as a secondary audit log, aside from logging actions not audited by Discord's audit log.
    logging: int

    # Receives slur usage deemed as false positives.
    false_positives: int

    # Receives notifications about actions taken by moderators, e.g bans.
    mod_log: int

    # TODO: find out what this does lol
    dm_forward: int

    # Receives notifications about errors.
    errors: int

    # Receives secret messages.
    secret: int

    # Used in reformation notifications for users sent into reformation to inform them of which channel to check out for more information.
    reform_info: int

    # Receives notifications regarding members being sent into reformation, intended to start a conversation regarding them in the channel dedicated to discussion between reformist and staff.
    reform_teachers: int

    # Receives notifications regarding members being sent into reformation, as a public ledger.
    reform_public_log: int

    # Receives notifications about submitted ban appeals.
    ban_appeals: int

    # The channel used for the photograph sharing feature.
    photography: int

    # The channel used for YouTube notifications.
    youtube: int
