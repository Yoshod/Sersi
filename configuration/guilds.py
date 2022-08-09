from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to guilds.
@dataclass
class ConfigurationGuilds(YAMLWizard):
    # The guild ID of the main server.
    main: str
