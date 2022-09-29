import nextcord
import pickle

from nextcord.ext import commands
from nextcord.ui import Button, View

from baseutils import DualCustodyView, PageView, sanitize_mention
from configutils import Configuration
from permutils import permcheck, is_mod, is_full_mod, cb_is_mod
from slurdetector import load_slurdetector, load_slurs, load_goodwords, get_slurs, get_slurs_leet, get_goodwords, clear_string, rm_slur, rm_goodword, detect_slur
from caseutils import case_history, slur_case


class Slur(commands.Cog):

    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail
        load_slurdetector()

    async def cb_action_taken(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedLogVar = nextcord.Embed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

        case_data = []
        for field in new_embed.fields:
            if field.name in ["User:", "Slurs Found:"]:
                case_data.append(field.value)

        member = interaction.guild.get_member(int(sanitize_mention(case_data[0])))

        unique_id = case_history(self.config, member.id, "Slur Usage")
        slur_case(self.config, unique_id, case_data[1], interaction.message.jump_url, member.id, interaction.user.id)

    async def cb_acceptable_use(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Usage Deemed Acceptable By", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedLogVar = nextcord.Embed(
            title="Acceptable Use Pressed",
            description="Usage of a slur has been deemed acceptable by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_false_positive(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Deemed As False Positive By:", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)
        channel = self.bot.get_channel(self.config.channels.false_positives)

        embedVar = nextcord.Embed(
            title="Marked as false positive",
            color=nextcord.Color.from_rgb(237, 91, 6))

        for field in new_embed.fields:
            if field.name in ["Context:", "Slurs Found:"]:
                embedVar.add_field(name=field.name, value=field.value, inline=False)

        embedVar.add_field(name="Report URL:", value=interaction.message.jump_url, inline=False)
        await channel.send(embed=embedVar)

        # Logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedLogVar = nextcord.Embed(
            title="False Positive Pressed",
            description="Detected slur has been deemed a false positive by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

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
            await ctx.send(f"{self.sersifail} `{slur}` is in conflict with existing slur `{existing_slur}`; cannot be added.")
            return

        if slur in get_slurs_leet():
            await ctx.send(f"{self.sersifail} `{slur}` is already on the list of slurs")
            return

        await ctx.send(f"Slur to be added: {slur}")
        with open(self.config.datafiles.slurfile, "a") as file:
            file.write(slur)
            file.write("\n")
        load_slurs()    # reloads updated list into memory

        # logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedVar = nextcord.Embed(
            title="Slur Added",
            description="A new slur has been added to the filter.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedVar.add_field(name="Added By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
        embedVar.add_field(name="Slur Added:", value=slur, inline=False)
        await channel.send(embed=embedVar)
        await ctx.send(f"{self.sersisuccess} Slur added. Detection will start now.")

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
            await ctx.send(f"{self.sersifail} `{word}` is already on the whitelist")
            return

        word_contains_slur = False
        for slur in get_slurs_leet():
            if slur in word:
                word_contains_slur = True

        if not word_contains_slur:
            await ctx.send(f"{self.sersifail} `{word}` does not contain any slurs; cannot be added.")
            return

        for existing_word in get_goodwords():
            if word in existing_word:
                await ctx.send(f"{self.sersifail} `{word}` is substring to existing goodword `{existing_word}`; cannot be added.")
                return
            elif existing_word in word:
                await ctx.send(f"{self.sersifail} existing goodword `{existing_word}` is substring to `{word}`; cannot be added.")
                return

        await ctx.send(f"Goodword to be added: {word}")

        with open(self.config.datafiles.goodwordfile, "a") as file:
            file.write(word)
            file.write("\n")
        load_goodwords()    # reloads updated list into memory

        # logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedVar = nextcord.Embed(
            title="Goodword Added",
            description="A new goodword has been added to the filter.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedVar.add_field(name="Added By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
        embedVar.add_field(name="Goodword Added:", value=word, inline=False)
        await channel.send(embed=embedVar)
        await ctx.send(f"{self.sersisuccess} Goodword added. Detection will start now.")

    async def cb_rmslur_confirm(self, interaction):
        mod_id, slur = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "Slur":
                slur = field.value
            if field.name == "Moderator ID":
                mod_id = int(field.value)
        moderator = interaction.guild.get_member(mod_id)

        rm_slur(slur)

        # logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embed_var = nextcord.Embed(
            title="Slur Removed",
            description="A slur has been removed from the filter.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embed_var.add_field(name="Removed By:", value=f"{moderator.mention} ({moderator.id})", inline=False)
        embed_var.add_field(name="Confirming Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        embed_var.add_field(name="Slur Removed:", value=slur, inline=False)
        await channel.send(embed=embed_var)
        await interaction.message.edit(f"{self.sersisuccess} Slur {slur} is no longer in the list", embed=None, view=None)

    @commands.command(aliases=["rmsl", "rmslur", "removesl"])
    async def removeslur(self, ctx, slur):
        """Remove a slur from the list of slurs."""
        if not await permcheck(ctx, is_mod):
            return

        dialog_embed = nextcord.Embed(
            title="Remove Slur",
            description="Following slur will be removed from slur detection:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="Slur", value=slur)
        dialog_embed.add_field(name="Moderator", value=ctx.author.mention)
        dialog_embed.add_field(name="Moderator ID", value=ctx.author.id)

        channel = self.bot.get_channel(self.config.channels.alert)
        view = DualCustodyView(self.cb_rmslur_confirm, ctx.author, is_full_mod)
        await view.send_dialogue(channel, embed=dialog_embed)

        await ctx.reply(f"Removal of `{slur}` from slur detection was sent for approval by another moderator")

    @commands.command(aliases=["rmgw", "rmgoodword", "removegw"])
    async def removegoodword(self, ctx, word):
        """Remove a goodword from the whitelist."""
        if not await permcheck(ctx, is_mod):
            return

        rm_goodword(word)

        # logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedVar = nextcord.Embed(
            title="Goodword Removed",
            description="A goodword has been removed from the filter.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedVar.add_field(name="Removed By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
        embedVar.add_field(name="Goodword Removed:", value=word, inline=False)
        await channel.send(embed=embedVar)
        await ctx.send(f"{self.sersisuccess} Goodword {word} is no longer in the list")

    @commands.command(aliases=["lssl", "listsl", "lsslurs"])
    async def listslurs(self, ctx, page=1):
        """List currently detected slurs.

        List slurs currently being detected by the bot, 100 slurs listed per page.
        """
        if not await permcheck(ctx, is_mod):
            return

        embed = nextcord.Embed(
            title="List of currently detected slurs",
            color=nextcord.Color.from_rgb(237, 91, 6))

        view = PageView(
            config=self.config,
            base_embed=embed,
            fetch_function=get_slurs,
            author=ctx.author,
            cols=2,
            init_page=int(page))
        await view.send_embed(ctx.channel)

    @commands.command(aliases=["lsgw", "lsgoodwords", "listgw"])
    async def listgoodwords(self, ctx, page=1):
        """List current goodwords.

        Currently whitlested from slur detection, 100 words listed per page.
        """
        if not await permcheck(ctx, is_mod):
            return

        embed = nextcord.Embed(
            title="List of goodwords currently whitelisted from slur detection",
            color=nextcord.Color.from_rgb(237, 91, 6))

        view = PageView(
            config=self.config,
            base_embed=embed,
            fetch_function=get_goodwords,
            author=ctx.author,
            cols=2,
            init_page=int(page))
        await view.send_embed(ctx.channel)

    # events
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.message.Message):
        detected_slurs = detect_slur(message.content)

        if message.channel.category.name == "Administration Centre":  # ignores message if sent inside of the administration centre
            return

        if message.author == self.bot.user:  # ignores message if message is by bot
            return

        elif len(detected_slurs) > 0:  # checks slur heat
            channel = self.bot.get_channel(self.config.channels.alert)
            slurembed = nextcord.Embed(
                title="Slur(s) Detected",
                description="A slur has been detected. Moderation action is advised.",
                color=nextcord.Color.from_rgb(237, 91, 6)
            )
            slurembed.add_field(name="Channel:", value=message.channel.mention, inline=False)
            slurembed.add_field(name="User:", value=message.author.mention)

            if len(message.content) < 1024:
                slurembed.add_field(name="Context:", value=message.content, inline=False)
            else:
                slurembed.add_field(name="Context:", value="`MESSAGE TOO LONG`", inline=False)

            slurembed.add_field(name="Slurs Found:", value=", ".join(set(detected_slurs)), inline=False)
            slurembed.add_field(name="URL:", value=message.jump_url, inline=False)
            slurembed.set_footer(text="Sersi Slur Detection Alert")

            with open(self.config.datafiles.casehistory, "rb") as file:
                case_history = pickle.load(file)  # --> dict of list; one dict entry per user ID

            user_history = case_history.get(message.author.id, [])  # -> list of user offenses, empty list if none

            slur_virgin = True  # noone was there to stop me naming a variable like this
            previous_offenses = []

            for case in user_history:
                if case[1] == "Slur Usage":
                    slur_virgin = False

                    # check if slur was done before
                    uid = case[0]
                    with open(self.config.datafiles.casedetails, "rb") as file:
                        case_details = pickle.load(file)
                        slur_used = case_details[uid][1]

                        previous_slurs = slur_used.split(", ")

                        if any(new_slur in previous_slurs for new_slur in detected_slurs):  # slur has been said before by user
                            report_url = case_details[uid][2]
                            previous_offenses.append(f"`{uid}` [Jump!]({report_url})")

            if not slur_virgin and not previous_offenses:  # user has said slurs before, however not that particular one
                slurembed.add_field(name="Previous Slur Uses:",
                                    value=f"{self.config.emotes.success} The user has a history of using slurs that were not detected in this message.",
                                    inline=False
                                    )

            elif previous_offenses:  # user has said that slur before
                prev_offenses = "\n".join(previous_offenses)
                if len(prev_offenses) < 1024:
                    slurembed.add_field(name="Previous Slur Uses:",
                                        value=f"{self.config.emotes.success} The user has a history of using a slur detected in this message:\n{prev_offenses}",
                                        inline=False
                                        )
                else:
                    slurembed.add_field(name="Previous Slur Uses:", value="`CASE LIST TOO LONG`", inline=False)

            else:
                slurembed.add_field(name="Previous Slur Uses:", value=f"{self.config.emotes.fail} The user is a first time offender.", inline=False)

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            acceptable_use = Button(label="Acceptable Use")
            acceptable_use.callback = self.cb_acceptable_use

            false_positive = Button(label="False Positive")
            false_positive.callback = self.cb_false_positive

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.interaction_check = cb_is_mod

            await channel.send(embed=slurembed, view=button_view)


def setup(bot, **kwargs):
    bot.add_cog(Slur(bot, kwargs["config"]))
