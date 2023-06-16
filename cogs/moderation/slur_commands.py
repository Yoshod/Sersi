import nextcord.ext.commands
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.base import PageView, DualCustodyView
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
)


class SlurCommands(nextcord.ext.commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command(aliases=["addsl"])
    async def addslur(self, ctx, *, slur=""):
        """Add a new slur to the list of slurs."""
        if not await permcheck(ctx, is_mod):
            return

        elif slur == "":
            await ctx.send(f"{ctx.author.mention} please provide a word to blacklist.")
            return
        slur = "".join(slur)
        slur = clear_string(slur)

        existing_slur = None
        for s in get_slurs_leet():
            if s in slur:
                existing_slur = s

        if existing_slur is not None:
            await ctx.send(
                f"{self.config.emotes.fail} `{slur}` is in conflict with existing slur `{existing_slur}`; "
                "cannot be added."
            )
            return

        if slur in get_slurs_leet():
            await ctx.send(
                f"{self.config.emotes.fail} `{slur}` is already on the list of slurs"
            )
            return

        await ctx.send(f"Slur to be added: {slur}")
        with open(self.config.datafiles.slurfile, "a") as file:
            file.write(slur)
            file.write("\n")
        load_slurs()  # reloads updated list into memory

        # logging
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Slur Added",
                description="A new slur has been added to the filter.",
                fields={
                    "Added By:": f"{ctx.message.author.mention} ({ctx.message.author.id})",
                    "Slur Added:": slur,
                },
            )
        )

        await ctx.send(
            f"{self.config.emotes.success} Slur added. Detection will start now."
        )

    @commands.command(aliases=["addgw"])
    async def addgoodword(self, ctx, *, word=""):
        """Add a new goodword into the whitelist."""
        if not await permcheck(ctx, is_mod):
            return

        elif word == "":
            await ctx.send(f"{ctx.author.mention} please provide a word to whitelist.")
            return
        word = "".join(word)
        word = clear_string(word)
        if word in get_goodwords():
            await ctx.send(
                f"{self.config.emotes.fail} `{word}` is already on the whitelist"
            )
            return

        word_contains_slur = False
        for slur in get_slurs_leet():
            if slur in word:
                word_contains_slur = True

        if not word_contains_slur:
            await ctx.send(
                f"{self.config.emotes.fail} `{word}` does not contain any slurs; cannot be added."
            )
            return

        for existing_word in get_goodwords():
            if word in existing_word:
                await ctx.send(
                    f"{self.config.emotes.fail} `{word}` is substring to existing goodword `{existing_word}`; "
                    "cannot be added."
                )
                return
            elif existing_word in word:
                await ctx.send(
                    f"{self.config.emotes.fail} existing goodword `{existing_word}` is substring to `{word}`; "
                    "cannot be added."
                )
                return

        await ctx.send(f"Goodword to be added: {word}")

        with open(self.config.datafiles.goodwordfile, "a") as file:
            file.write(word)
            file.write("\n")

        load_goodwords()  # reloads updated list into memory

        # logging
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Goodword Added",
                description="A new goodword has been added to the filter.",
                fields={
                    "Added By:": f"{ctx.message.author.mention} ({ctx.message.author.id})",
                    "Goodword Added:": word,
                },
            )
        )
        await ctx.send(
            f"{self.config.emotes.success} Goodword added. Detection will start now."
        )

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
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
            description="(Mega Administrator only!) Reason to bypass dual custody",
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
    async def list_slurs(self, interaction: nextcord.Interaction, input: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        slurs = [slur for slur in get_slurs() if slur.lower().startswith(input.lower())]
        await interaction.response.send_autocomplete(slurs)

    @commands.command(aliases=["rmgw", "rmgoodword", "removegw"])
    async def removegoodword(self, ctx, word):
        """Remove a goodword from the whitelist."""
        if not await permcheck(ctx, is_mod):
            return

        rm_goodword(word)

        # logging
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Goodword Removed",
                description="A goodword has been removed from the filter.",
                fields={
                    "Removed By:": f"{ctx.message.author.mention} ({ctx.message.author.id})",
                    "Goodword Removed:": word,
                },
            )
        )

        await ctx.send(
            f"{self.config.emotes.success} Goodword {word} is no longer in the list"
        )

    @commands.command(aliases=["lssl", "listsl", "lsslurs"])
    async def listslurs(self, ctx, page=1):
        """List currently detected slurs.

        List slurs currently being detected by the bot, 100 slurs listed per page.
        """
        if not await permcheck(ctx, is_mod):
            return

        embed = SersiEmbed(title="List of currently detected slurs")

        view = PageView(
            config=self.config,
            base_embed=embed,
            fetch_function=get_slurs,
            author=ctx.author,
            cols=2,
            init_page=int(page),
        )
        await view.send_embed(ctx.channel)

    @commands.command(aliases=["lsgw", "lsgoodwords", "listgw"])
    async def listgoodwords(self, ctx, page=1):
        """List current goodwords.

        Currently, whitelisted from slur detection, 100 words listed per page.
        """
        if not await permcheck(ctx, is_mod):
            return

        embed = SersiEmbed(
            title="List of goodwords currently whitelisted from slur detection"
        )

        view = PageView(
            config=self.config,
            base_embed=embed,
            fetch_function=get_goodwords,
            author=ctx.author,
            cols=2,
            init_page=int(page),
        )
        await view.send_embed(ctx.channel)


def setup(bot, **kwargs):
    bot.add_cog(SlurCommands(bot, kwargs["config"]))
