from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to roles.
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
