import nextcord
from nextcord.ext import commands

from utils.alerts import AlertType, AlertView, create_alert_log
from utils.base import ignored_message, limit_string, get_page
from utils.cases import slur_history, slur_virgin
from utils.config import Configuration
from utils.database import db_session, Slur, Goodword
from utils.detection import SlurDetector, highlight_matches, clear_string
from utils.perms import permcheck, is_mod, is_full_mod, is_dark_mod
from utils.sersi_embed import SersiEmbed
from utils.views import PageView, DualCustodyView


def fetch_slurs(*args, page: int = None, per_page: int = 10) -> list[str]:
    with db_session() as session:
        slur_list: list[Slur] = session.query(Slur).all()

    if not slur_list:
        return None, 0, 0

    return get_page([slur.slur for slur in slur_list], page, per_page)


def fetch_goodwords(*args, page: int = None, per_page: int = 10) -> list[str]:
    with db_session() as session:
        goodword_list: list[Goodword] = session.query(Goodword).all()

    if not goodword_list:
        return None, 0, 0

    return get_page([goodword.goodword for goodword in goodword_list], page, per_page)


class SlurDetection(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        self.slur_detector = SlurDetector()

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def slur_detection(self, interaction: nextcord.Interaction):
        pass

    @slur_detection.subcommand(
        description="Add a new slur to the list of slurs.",
    )
    async def add_slur(
        self,
        interaction: nextcord.Interaction,
        slur: str = nextcord.SlashOption(
            description="The slur to add to the list of slurs.",
            required=True,
        ),
    ):
        """Add a new slur to the list of slurs."""
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        slur = clear_string(slur)

        if existing_slurs := self.slur_detector.find_slurs(slur):
            await interaction.followup.send(
                f"{self.config.emotes.fail} `{slur}` is in conflict with existing slur(s) "
                f"`{'`, `'.join(existing_slurs)}`. cannot be added."
            )
            return

        with db_session() as session:
            session.add(Slur(slur=slur, added_by=interaction.user.id))
            session.commit()

        self.slur_detector.add_slur(slur)

        # logging
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Slur Added",
                description="A new slur has been added to the filter.",
                fields={
                    "Added By:": f"{interaction.user.mention} ({interaction.user.id})",
                    "Slur Added:": slur,
                },
            )
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} Slur `{slur}` added. Detection will start now.",
        )

    @slur_detection.subcommand(
        description="Add a new goodword into the whitelist.",
    )
    async def add_goodword(
        self,
        interaction: nextcord.Interaction,
        word: str = nextcord.SlashOption(
            description="The word to whitelist.",
            required=True,
        ),
    ):
        """Add a new goodword into the whitelist."""
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        word = clear_string(word)
        if word in self.slur_detector.goodwords:
            await interaction.followup.send(
                f"{self.config.emotes.fail} `{word}` is already on the whitelist"
            )
            return

        related = next(iter(self.slur_detector.find_slurs(word).keys()), None)

        if not related:
            await interaction.followup.send(
                f"{self.config.emotes.fail} `{word}` does not contain any detected slurs, cannot be added."
            )
            return

        with db_session() as session:
            session.add(
                Goodword(
                    goodword=word, slur=related, added_by=interaction.user.id
                )
            )
            session.commit()

        self.slur_detector.add_goodword(related, word)

        # logging
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Goodword Added",
                description="A new goodword has been added to the whitelist.",
                fields={
                    "Added By:": f"{interaction.user.mention} ({interaction.user.id})",
                    "Goodword Added:": word,
                },
            )
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} Goodword `{word}` for slur `{related}` added. Detection will start now.",
        )

    @slur_detection.subcommand(
        description="Remove a slur from the list of slurs.",
    )
    async def remove_slur(
        self,
        interaction: nextcord.Interaction,
        slur: str = nextcord.SlashOption(
            description="The slur to remove from the list of slurs.",
            required=True,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="(Administrator only!) Reason to bypass dual custody",
            min_length=8,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_full_mod):
            return

        await interaction.response.defer(ephemeral=False)

        if slur not in self.slur_detector.slurs:
            await interaction.followup.send(
                f"{self.config.emotes.fail} {slur} is not on the slur list."
            )
            return

        @DualCustodyView.query(
            title="Slur Removal",
            prompt="Following slur will be removed from slur detection:",
            perms=is_full_mod,
            embed_args={"Slur": slur},
            bypass=True if bypass_reason else False,
        )
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            with db_session() as session:
                session.query(Slur).filter_by(slur=slur).delete()
                session.commit()

            self.slur_detector.remove_slur(slur)

            # logging
            embed_fields = {
                "Slur Removed:": slur,
                "Removed By:": f"{interaction.user.mention} ({interaction.user.id})",
            }
            if bypass_reason and is_dark_mod(interaction.user):
                embed_fields["Dual Custody Bypass Reason"] = bypass_reason
            else:
                embed_fields[
                    "Confirming Moderator:"
                ] = f"{confirming_moderator.mention} ({confirming_moderator.id})"

            channel = self.bot.get_channel(self.config.channels.logging)
            embed_var = SersiEmbed(
                title="Slur Removed",
                description="A slur has been removed from the filter.",
                fields=embed_fields,
            )
            if bypass_reason:
                await interaction.followup.send(embed=embed_var)
            await channel.send(embed=embed_var)

        await execute(self.bot, self.config, interaction)

    @remove_slur.on_autocomplete("slur")
    async def get_slurs(self, interaction: nextcord.Interaction, input: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        slurs = [
            slur
            for slur in self.slur_detector.slurs
            if slur.lower().startswith(input.lower())
        ][:25]
        await interaction.response.send_autocomplete(slurs)

    @slur_detection.subcommand(
        description="Remove a goodword from the whitelist.",
    )
    async def remove_goodword(
        self,
        interaction: nextcord.Interaction,
        word: str = nextcord.SlashOption(
            description="The word to remove from the whitelist.",
            required=True,
        ),
    ):
        """Remove a goodword from the whitelist."""
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        if word not in self.slur_detector.goodwords:
            await interaction.followup.send(
                f"{self.config.emotes.fail} {word} is not on the whitelist."
            )
            return

        with db_session() as session:
            gw = session.query(Goodword).filter_by(goodword=word).first()
            slur = gw.slur
            session.delete(gw)
            session.commit()

        self.slur_detector.remove_goodword(slur, word)

        # logging
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Goodword Removed",
                description="A goodword has been removed from the filter.",
                fields={
                    "Removed By:": f"{interaction.user.mention} ({interaction.user.id})",
                    "Goodword Removed:": word,
                },
            )
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} Goodword {word} is no longer in the list"
        )

    @remove_goodword.on_autocomplete("word")
    async def get_goodwords(self, interaction: nextcord.Interaction, input: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        goodwords = [
            word
            for word in self.slur_detector.goodwords
            if word.lower().startswith(input.lower())
        ][:25]
        await interaction.response.send_autocomplete(goodwords)

    @slur_detection.subcommand(description="List currently detected slurs.")
    async def list_slurs(
        self,
        interaction: nextcord.Interaction,
        page: int = nextcord.SlashOption(
            description="The page of slurs to display.",
            required=False,
            default=1,
        ),
    ):
        """List currently detected slurs."""
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        embed = SersiEmbed(title="List of currently detected slurs")

        view = PageView(
            config=self.config,
            base_embed=embed,
            fetch_function=fetch_slurs,
            author=interaction.user,
            cols=2,
            init_page=page,
        )
        await view.send_followup(interaction)

    @slur_detection.subcommand(description="List currently whitelisted goodwords.")
    async def list_goodwords(
        self,
        interaction: nextcord.Interaction,
        page: int = nextcord.SlashOption(
            description="The page of goodwords to display.",
            required=False,
            default=1,
        ),
    ):
        """List currently whitelisted goodwords."""
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        embed = SersiEmbed(
            title="List of goodwords currently whitelisted from slur detection"
        )

        view = PageView(
            config=self.config,
            base_embed=embed,
            fetch_function=fetch_goodwords,
            author=interaction.user,
            cols=2,
            init_page=page,
        )
        await view.send_followup(interaction)

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
    bot.add_cog(SlurDetection(bot, kwargs["config"]))
