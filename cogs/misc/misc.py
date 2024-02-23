import os
import nextcord
import wikipediaapi
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
grandparent_dir = os.path.dirname(parent_dir)
config_path = os.path.join(grandparent_dir, "persistent_data/config.yaml")

CONFIG = Configuration.from_yaml_file(config_path)

WIKI_WIKI = wikipediaapi.Wikipedia(f"{CONFIG.bot.wiki_header}", "en")


class Misc(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Miscellaneous commands",
    )
    async def misc(self, interaction: nextcord.Interaction):
        pass

    @misc.subcommand(description="Don't Ask To Ask, Just Ask")
    async def asktoask(self, interaction: nextcord.Interaction):
        await interaction.send(
            embed=SersiEmbed(
                title="Don't Ask To Ask, Just Ask",
                url="https://dontasktoask.com",
                description="Don't ask permission to ask a question, just ask the question.\nhttps://dontasktoask.com",
            ).set_thumbnail("https://dontasktoask.com/favicon.png")
        )

    @misc.subcommand(description="Search Wikipedia")
    async def wiki(
        self,
        interaction: nextcord.Interaction,
        search: str = nextcord.SlashOption(
            description="Search Wikipedia (Must be English)"
        ),
        ephemeral: bool = nextcord.SlashOption(
            description="Should the response be ephemeral?",
            required=False,
            choices={
                "Yes": True,
                "No": False,
            },
        ),
        language: str = nextcord.SlashOption(
            description="Language to search in. English will always be included.",
            required=False,
            choices={
                "Arabic": "ar",
                "Chinese": "zh",
                "Czech": "cs",
                "Dutch": "nl",
                "French": "fr",
                "German": "de",
                "Greek": "el",
                "Hebrew": "he",
                "Hindi": "hi",
                "Hungarian": "hu",
                "Indonesian": "id",
                "Italian": "it",
                "Japanese": "ja",
                "Korean": "ko",
                "Polish": "pl",
                "Portuguese": "pt",
                "Romanian": "ro",
                "Russian": "ru",
                "Spanish": "es",
                "Swedish": "sv",
                "Turkish": "tr",
                "Ukrainian": "uk",
                "Vietnamese": "vi",
            },
            choice_localizations={
                "Chinese": {
                    nextcord.Locale.zh_CN: "中文",
                    nextcord.Locale.zh_TW: "中文",
                },
                "Czech": {nextcord.Locale.cs: "Čeština"},
                "Dutch": {nextcord.Locale.nl: "Nederlands"},
                "French": {nextcord.Locale.fr: "Français"},
                "German": {nextcord.Locale.de: "Deutsch"},
                "Greek": {nextcord.Locale.el: "Ελληνικά"},
                "Hindi": {nextcord.Locale.hi: "हिन्दी"},
                "Hungarian": {nextcord.Locale.hu: "Magyar"},
                "Indonesian": {nextcord.Locale.id: "Bahasa Indonesia"},
                "Italian": {nextcord.Locale.it: "Italiano"},
                "Japanese": {nextcord.Locale.ja: "日本語"},
                "Korean": {nextcord.Locale.ko: "한국어"},
                "Polish": {nextcord.Locale.pl: "Polski"},
                "Portuguese": {nextcord.Locale.pt_BR: "Português (Brasil)"},
                "Romanian": {nextcord.Locale.ro: "Română"},
                "Russian": {nextcord.Locale.ru: "Русский"},
                "Spanish": {nextcord.Locale.es_ES: "Español"},
                "Swedish": {nextcord.Locale.sv_SE: "Svenska"},
                "Turkish": {nextcord.Locale.tr: "Türkçe"},
                "Ukrainian": {nextcord.Locale.uk: "Українська"},
                "Vietnamese": {nextcord.Locale.vi: "Tiếng Việt"},
            },
        ),
    ):
        if not ephemeral:
            await interaction.response.defer()

        else:
            await interaction.response.defer(ephemeral=True)

        page = WIKI_WIKI.page(search)
        if not page.exists():
            await interaction.followup.send(
                f"{self.config.emotes.fail} Page does not exist or could not be found."
            )
            return

        if language:
            if language in page.langlinks.keys():
                lang_page = page.langlinks[language]

                await interaction.followup.send(
                    embed=SersiEmbed(
                        title=page.title,
                        url=page.fullurl,
                        footer="Wikipedia Search",
                        fields={
                            "Summary en": (
                                f"{page.summary[0:1024]}..."
                                if len(page.summary) > 1024
                                else page.summary
                            ),
                            f"Summary {language}": (
                                f"{lang_page.summary[0:1024]}..."
                                if len(lang_page.summary) > 1024
                                else lang_page.summary
                            ),
                            f"URL {language}": lang_page.fullurl,
                        },
                    ).set_thumbnail(
                        "https://en.wikipedia.org/static/images/project-logos/enwiki.png"
                    )
                )

                return

        await interaction.followup.send(
            embed=SersiEmbed(
                title=page.title,
                url=page.fullurl,
                description=(
                    f"{page.summary[0:1024]}..."
                    if len(page.summary) > 1024
                    else page.summary
                ),
                footer="Wikipedia Search",
            ).set_thumbnail(
                "https://en.wikipedia.org/static/images/project-logos/enwiki.png"
            )
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Misc(bot, kwargs["config"]))
