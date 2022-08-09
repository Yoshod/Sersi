from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to permission/staff roles.
@dataclass
class ConfigurationPermissionRoles(YAMLWizard):
    # The role ID of general staff.
    staff: int

    # The role ID of reformation staff.
    reformist: int

    # The role ID of verification help staff.
    ticket_support: int

    # The role ID of contributors/developers.
    sersi_contributor: int

    # The role ID of trial moderators.
    trial_moderator: int

    # The role ID of normal moderators.
    moderator: int

    # The role ID of senior moderators.
    senior_moderator: int

    # The role ID of dark moderators.
    dark_moderator: int
