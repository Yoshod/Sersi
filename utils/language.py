import yaml
import os

from utils.database import SessionLocal, Language


def flatten_dict(dictionary: dict, sep='.', prefix='') -> dict[str, str]:
    new_dict = dict()
    for k, v in dictionary.items():
        if isinstance(v, dict):
            new_dict.update(flatten_dict(v, sep, k))
        else:
            new_dict[prefix + sep + k if prefix else k] = v


class LanguageManager:
    strings: dict[str, dict[str, str]]

    def __init__(self, lang_dir="lang"):
        self.strings = {}
        self.lang_dir = lang_dir
        self.load_languages()

    def load_languages(self):
        """Load all language files from the specified directory."""
        for filename in os.listdir(self.lang_dir):
            if not filename.endswith(".yaml"):
                continue
            lang_code = filename[:-5]
            with open(
                os.path.join(self.lang_dir, filename), "r", encoding="utf-8"
            ) as file:
                self.strings[lang_code] = flatten_dict(yaml.safe_load(file))

    def get_string(self, guild_id: int, key: str, **kwargs):
        guild_lang = "en"  # Default to English

        with SessionLocal() as session:
            result = (
                session.query(Language.language).filter_by(guild_id=guild_id).first()
            )
            if result:
                guild_lang = result[0]

        try:
            return self.strings[guild_lang][key].format(**kwargs)
        except (KeyError, TypeError):
            # Fallback to English if string not found in the target language
            print(
                f"Language key '{key}' not found in '{guild_lang}', falling back to English."
            )
            try:
                return self.strings["en"][key].format(**kwargs)
            except (KeyError, TypeError):
                return key.upper()  # Return the key itself if not found anywhere


lang_manager = LanguageManager()
