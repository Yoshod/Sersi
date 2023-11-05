import nextcord.ext.commands
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.base import PageView, DualCustodyView
from utils.database import db_session, Slur, Goodword
from utils.config import Configuration
from utils.perms import permcheck, is_mod, is_full_mod, is_dark_mod
from slurdetector import (
    get_goodwords,
    get_slurs,
    rm_goodword,
    rm_slur,
    load_goodwords,
    get_slurs_leet,
    clear_string,
    load_slurs,
    leet,
)


class SlurCommands(nextcord.ext.commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

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

        await interaction.response.defer(ephemeral=False)

        slur = "".join(slur)
        slur = clear_string(slur)

        existing_slur = None
        for s in get_slurs_leet():
            if s in slur:
                existing_slur = s

        if existing_slur is not None:
            await interaction.followup.send(
                f"{self.config.emotes.fail} `{slur}` is in conflict with existing slur `{existing_slur}`; "
                "cannot be added."
            )
            return

        await interaction.followup.send(f"Slur to be added: {slur}")
        with db_session() as session:
            session.add(Slur(slur=slur, added_by=interaction.user.id))
            session.commit()

        load_slurs()  # reloads updated list into memory

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
            f"{self.config.emotes.success} Slur added. Detection will start now."
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

        await interaction.response.defer(ephemeral=False)

        word = "".join(word)
        word = clear_string(word)
        if word in get_goodwords():
            await interaction.followup.send(
                f"{self.config.emotes.fail} `{word}` is already on the whitelist"
            )
            return

        related_slur = None
        for slur in get_slurs():
            for slur_variant in leet(slur):
                if slur_variant in word:
                    related_slur = slur
                    break

        if not related_slur:
            await interaction.followup.send(
                f"{self.config.emotes.fail} `{word}` does not contain any slurs; cannot be added."
            )
            return

        for existing_word in get_goodwords():
            if word in existing_word:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} `{word}` is substring to existing goodword `{existing_word}`; "
                    "cannot be added."
                )
                return
            elif existing_word in word:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} existing goodword `{existing_word}` is substring to `{word}`; "
                    "cannot be added."
                )
                return

        await interaction.followup.send(f"Goodword to be added: {word}")

        with db_session() as session:
            session.add(
                Goodword(goodword=word, slur=related_slur, added_by=interaction.user.id)
            )
            session.commit()

        load_goodwords()

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
            f"{self.config.emotes.success} Goodword added. Detection will start now."
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

        if slur not in get_slurs():
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
            rm_slur(slur)

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

        slurs = [slur for slur in get_slurs() if slur.lower().startswith(input.lower())]
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

        if word not in get_goodwords():
            await interaction.followup.send(
                f"{self.config.emotes.fail} {word} is not on the whitelist."
            )
            return

        rm_goodword(word)

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
            word for word in get_goodwords() if word.lower().startswith(input.lower())
        ]
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
            fetch_function=get_slurs,
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
            fetch_function=get_goodwords,
            author=interaction.user,
            cols=2,
            init_page=page,
        )
        await view.send_followup(interaction)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(SlurCommands(bot, kwargs["config"]))
