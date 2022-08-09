from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to invites.
@dataclass
class ConfigurationInvites(YAMLWizard):
    # The invite link to the support server.
    support_server: str

    # The invite link to the ban appealing server.
    ban_appeals: str
