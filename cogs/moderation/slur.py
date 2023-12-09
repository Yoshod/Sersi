import nextcord
from nextcord.ext import commands

from utils.alerts import AlertType, AlertView, create_alert_log
from utils.base import ignored_message, limit_string
from utils.cases import slur_history, slur_virgin
from utils.config import Configuration
from utils.detection import SlurDetector, highlight_matches
from utils.sersi_embed import SersiEmbed


class Slur(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        self.slur_detector = SlurDetector()

    def _get_previous_cases(
        self, user: nextcord.User | nextcord.Member, slurs: list[str]
    ) -> str:
        if slur_virgin(user):
            return f"{self.config.emotes.fail} The user is a first time offender."

        cases = slur_history(user, slurs)

        if not cases:
            return (
                f"{self.config.emotes.success} The user has a history of using slurs that were not detected "
                f"in this message."
            )

        prev_offences = (
            f"{self.config.emotes.success} The user has a history of using a slur detected in "
            "this message:"
        )
        for slur_case in cases:
            prev_offences += f"\n`{slur_case.id}` {slur_case.slur_used} <t:{int(slur_case.created.timestamp())}:R>"

        return prev_offences

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
            return

        slur_matches = self.slur_detector.find_slurs(message.content)
        if not slur_matches:
            return

        slurs = slur_matches.keys()
        highlited = highlight_matches(message.content, sum(slur_matches.values(), []))

        embed = SersiEmbed(
            title="Slur(s) Detected in Message",
            description=limit_string(highlited, 4096),
            fields=[
                {
                    "User:": message.author.mention,
                    "Channel:": message.channel.mention,
                    "Message:": message.jump_url,
                },
                {"Slurs Found:": ", ".join(slurs)},
                {
                    "Previous Slur Uses:": self._get_previous_cases(
                        message.author, slurs
                    ),
                },
            ],
        ).set_author(
            name=message.author.display_name,
            icon_url=str(message.author.avatar.url),
        )

        alert = await self.bot.get_channel(self.config.channels.alert).send(
            embed=embed, view=AlertView(AlertType.Slur, message.author)
        )

        create_alert_log(alert, AlertType.Slur)

    @commands.Cog.listener()
    async def on_presence_update(self, before: nextcord.Member, after: nextcord.Member):
        if not after.status:
            return

        slur_matches = self.slur_detector.find_slurs(after.status)
        if not slur_matches:
            return

        slurs = slur_matches.keys()
        highlited = highlight_matches(after.status, sum(slur_matches.values(), []))

        embed = SersiEmbed(
            title="Member changed their status to contain slurs",
            description="A slur has been detected. Moderation action is advised.",
            footer="Sersi Slur Detection Alert",
            fields=[
                {
                    "User:": after.mention,
                    "Status:": highlited,
                    "Slurs Found:": ", ".join(set(slurs)),
                },
                {"Previous Slur Uses:": self._get_previous_cases(after, slurs)},
            ],
        ).set_author(
            name=after.display_name,
            icon_url=str(after.avatar.url),
        )

        alert = await self.bot.get_channel(self.config.channels.alert).send(
            embed=embed, view=AlertView(AlertType.Slur, after)
        )

        create_alert_log(alert, AlertType.Slur)

    @commands.Cog.listener()
    async def on_user_update(self, before: nextcord.User, after: nextcord.User):
        if not after.name:
            return

        slur_matches = self.slur_detector.find_slurs(after.name)
        if not slur_matches:
            return

        slurs = slur_matches.keys()
        highlited = highlight_matches(after.name, sum(slur_matches.values(), []))

        embed = SersiEmbed(
            title="User changed their username to contain slurs",
            description="A slur has been detected. Moderation action is advised.",
            footer="Sersi Slur Detection Alert",
            fields=[
                {
                    "User:": after.mention,
                    "Username:": highlited,
                    "Slurs Found:": ", ".join(set(slurs)),
                },
                {"Previous Slur Uses:": self._get_previous_cases(after, slurs)},
            ],
        ).set_author(
            name=after.display_name,
            icon_url=str(after.avatar.url),
        )

        alert = await self.bot.get_channel(self.config.channels.alert).send(
            embed=embed, view=AlertView(AlertType.Slur, after.id)
        )

        create_alert_log(alert, AlertType.Slur)

    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        if not after.nick:
            return

        slur_matches = self.slur_detector.find_slurs(after)
        if not slur_matches:
            return

        slurs = slur_matches.keys()
        highlited = highlight_matches(after.nick, sum(slur_matches.values(), []))

        embed = SersiEmbed(
            title="Member changed their nickname to contain slurs",
            description="A slur has been detected. Moderation action is advised.",
            footer="Sersi Slur Detection Alert",
            fields=[
                {
                    "User:": after.mention,
                    "Nickname:": highlited,
                    "Slurs Found:": ", ".join(set(slurs)),
                },
                {"Previous Slur Uses:": self._get_previous_cases(after, slurs)},
            ],
        ).set_author(
            name=after.display_name,
            icon_url=str(after.avatar.url),
        )

        alert = await self.bot.get_channel(self.config.channels.alert).send(
            embed=embed, view=AlertView(AlertType.Slur, after)
        )

        create_alert_log(alert, AlertType.Slur)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Slur(bot, kwargs["config"]))
