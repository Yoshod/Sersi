from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to cogs.
@dataclass
class ConfigurationCogs(YAMLWizard):
    # A list of cogs that should not be loaded.
    disabled: list[str] | None
