import yaml
import os
from utils.database import guild_db_manager, Language


class LanguageManager:
    def __init__(self, lang_dir="lang"):
        self.strings = {}
        self.lang_dir = lang_dir
        self.load_languages()

    def load_languages(self):
        """Load all language files from the specified directory."""
        for filename in os.listdir(self.lang_dir):
            if filename.endswith(".yaml"):
                lang_code = filename[:-5]
                with open(
                    os.path.join(self.lang_dir, filename), "r", encoding="utf-8"
                ) as file:
                    self.strings[lang_code] = yaml.safe_load(file)

    def get_string(self, guild_id: int, key, **kwargs):
        keys = key.split(".")
        guild_lang = "en"  # Default to English

        with guild_db_manager.get_session(guild_id) as session:
            result = session.query(Language.language).first()
            if result:
                guild_lang = result[0]

        try:
            string = self.strings[guild_lang]
            for k in keys:
                string = string[k]
            return string.format(**kwargs)
        except (KeyError, TypeError):
            # Fallback to English if string not found in the target language
            print(
                f"Language key '{key}' not found in '{guild_lang}', falling back to English."
            )
            try:
                string = self.strings["en"]
                for k in keys:
                    string = string[k]
                return string.format(**kwargs)
            except (KeyError, TypeError):
                return key  # Return the key itself if not found anywhere


lang_manager = LanguageManager()
