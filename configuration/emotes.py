from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to emotes.
@dataclass
class ConfigurationEmotes(YAMLWizard):
    # The emote, in "<:name:id>" format, used to declare success.
    success: str

    # The emote, in "<:name:id>" format, used to declare failure.
    fail: str
