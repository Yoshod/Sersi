from dataclasses import dataclass
from dataclass_wizard import YAMLWizard


# Holds configuration data related to the role IDs for opt-in channels.
@dataclass
class ConfigurationOptInRoles(YAMLWizard):
    # The opt-in role related to the gaming channel.
    gaming: str

    # The opt-in role related to the technology and computer science channel.
    tech_compsci: str

    # The opt-in role related to the food and drinks channel.
    food_and_drink: str

    # The opt-in role related to the education channel.
    education: str

    # The opt-in role related to the art, creativity and writing channel.
    art: str

    # The opt-in role related to the anime channel.
    anime: str

    # The opt-in role related to the furry channel.
    furry: str

    # The opt-in role related to the advertising channel.
    shillposting: str

    # The opt-in role related to the music channel.
    music: str

    # The opt-in role related to the photography channel.
    photography: str
