import nextcord

from nextcord.ext import commands
from nextcord.ui import Button, View

from baseutils import DualCustodyView
from configutils import get_config, get_config_int
from permutils import permcheck, is_mod, is_full_mod, cb_is_mod
from slurdetector import load_slurdetector, load_slurs, load_goodwords, get_slurs, get_goodwords, clear_string, rm_slur, rm_goodword, detect_slur


class Slur(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        load_slurdetector()

    async def cb_action_taken(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        embedLogVar = nextcord.Embed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_acceptable_use(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Usage Deemed Acceptable By", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
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
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'false positives'))

        embedVar = nextcord.Embed(
            title="Marked as false positive",
            color=nextcord.Color.from_rgb(237, 91, 6))

        for field in new_embed.fields:
            if field.name in ["Context:", "Slurs Found:"]:
                embedVar.add_field(name=field.name, value=field.value, inline=False)

        embedVar.add_field(name="Report URL:", value=interaction.message.jump_url, inline=False)
        await channel.send(embed=embedVar)

        # Logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        embedLogVar = nextcord.Embed(
            title="False Positive Pressed",
            description="Detected slur has been deemed a false positive by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_slur_list_next_page(self, interaction):
        new_embed = interaction.message.embeds[0]
        for field in new_embed.fields:
            if field.name.lower() == "page:":
                page_field = field
        page = int(page_field.value.split('/')[0][2:]) + 1
        wordlist, pages, page = get_slurs(page, 20)
        new_embed.clear_fields()
        if len(wordlist) > 10:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[0:10]))
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[10:]))
        else:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist))
        new_embed.add_field(name="page:", value=f"**{page}/{pages}**", inline=False)
        await interaction.message.edit(embed=new_embed)

    async def cb_slur_list_prev_page(self, interaction):
        new_embed = interaction.message.embeds[0]
        for field in new_embed.fields:
            if field.name.lower() == "page:":
                page_field = field
        page = int(page_field.value.split('/')[0][2:]) - 1
        wordlist, pages, page = get_slurs(page, 20)
        new_embed.clear_fields()
        if len(wordlist) > 10:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[0:10]))
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[10:]))
        else:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist))
        new_embed.add_field(name="page:", value=f"**{page}/{pages}**", inline=False)
        await interaction.message.edit(embed=new_embed)

    async def cb_goodword_list_next_page(self, interaction):
        new_embed = interaction.message.embeds[0]
        for field in new_embed.fields:
            if field.name.lower() == "page:":
                page_field = field
        page = int(page_field.value.split('/')[0][2:]) + 1
        wordlist, pages, page = get_goodwords(page, 20)
        new_embed.clear_fields()
        if len(wordlist) > 10:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[0:10]))
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[10:]))
        else:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist))
        new_embed.add_field(name="page:", value=f"**{page}/{pages}**", inline=False)
        await interaction.message.edit(embed=new_embed)

    async def cb_goodword_list_prev_page(self, interaction):
        new_embed = interaction.message.embeds[0]
        for field in new_embed.fields:
            if field.name.lower() == "page:":
                page_field = field
        page = int(page_field.value.split('/')[0][2:]) - 1
        wordlist, pages, page = get_goodwords(page, 20)
        new_embed.clear_fields()
        if len(wordlist) > 10:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[0:10]))
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[10:]))
        else:
            new_embed.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist))
        new_embed.add_field(name="page:", value=f"**{page}/{pages}**", inline=False)
        await interaction.message.edit(embed=new_embed)

    @commands.command(aliases=["addsl"])
    async def addslur(self, ctx, *, slur=""):
        """adds a new slur to the list of slurs."""
        if not await permcheck(ctx, is_mod):
            return

        elif slur == "":
            await ctx.send(f"{ctx.author.mention} please provide a word to blacklist.")
            return
        slur = "".join(slur)
        slur = clear_string(slur)

        existing_slur = None
        for s in get_slurs():
            if s in slur:
                existing_slur = True

        if existing_slur is not None:
            await ctx.send(f"{self.sersifail} {slur} is in conflict with existing slur {existing_slur}; cannot be added.")
            return

        if slur in get_slurs():
            await ctx.send(f"{self.sersifail} {slur} is already on the list of slurs")
            return

        await ctx.send(f"Slur to be added: {slur}")
        with open("Files/SlurAlerts/slurs.txt", "a") as file:
            file.write(slur)
            file.write("\n")
        load_slurs()    # reloads updated list into memory

        # logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
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
        """adds a new goodword into the whitelist."""
        if not await permcheck(ctx, is_mod):
            return

        elif word == "":
            await ctx.send(f"{ctx.author.mention} please provide a word to whitelist.")
            return
        word = "".join(word)
        word = clear_string(word)
        if word in get_goodwords():
            await ctx.send(f"{self.sersifail} {word} is already on the whitelist")
            return

        word_contains_slur = False
        for slur in get_slurs():
            if slur in word:
                word_contains_slur = True

        if not word_contains_slur:
            await ctx.send(f"{self.sersifail} {word} does not contain any slurs; cannot be added.")
            return

        for existing_word in get_goodwords():
            if word in existing_word:
                await ctx.send(f"{self.sersifail} {word} is substring to existing goodword {existing_word}; cannot be added.")
                return
            elif existing_word in word:
                await ctx.send(f"{self.sersifail} existing goodword {existing_word} is substring to {word}; cannot be added.")
                return

        await ctx.send(f"Goodword to be added: {word}")
        with open("Files/SlurAlerts/goodword.txt", "a") as file:
            file.write(word)
            file.write("\n")
        load_goodwords()    # reloads updated list into memory

        # logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        embedVar = nextcord.Embed(
            title="Goodword Added",
            description="A new goodword has been added to the filter.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedVar.add_field(name="Added By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
        embedVar.add_field(name="Goodword Added:", value=word, inline=False)
        await channel.send(embed=embedVar)
        await ctx.send("{self.sersisuccess} Goodword added. Detection will start now.")

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
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
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
        """removes a slur from the list of slurs."""
        if not await permcheck(ctx, is_mod):
            return

        dialog_embed = nextcord.Embed(
            title="Remove Slur",
            description="Following slur will be removed from slur detection:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="Slur", value=slur)
        dialog_embed.add_field(name="Moderator", value=ctx.author.mention)
        dialog_embed.add_field(name="Moderator ID", value=ctx.author.id)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'alert'))
        view = DualCustodyView(self.cb_rmslur_confirm, ctx.author, is_full_mod)
        await view.send_dialogue(channel, embed=dialog_embed)

        await ctx.reply(f"Removal of `{slur}` from slur detection was sent for approval by another moderator")

    @commands.command(aliases=["rmgw", "rmgoodword", "removegw"])
    async def removegoodword(self, ctx, word):
        """removes a goodword from the whitelist."""
        if not await permcheck(ctx, is_mod):
            return

        rm_goodword(word)

        # logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
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
        """lists currently detected slurs

        lists slurs currently being detected by the bot, 100 slurs listed per page."""
        if not await permcheck(ctx, is_mod):
            return

        wordlist, pages, page = get_slurs(page, 20)

        # post the list as embed
        embedVar = nextcord.Embed(
            title="List of currently detected slurs",
            # description="**•**\u00A0" + "\n**•**\u00A0".join(wordlist),
            color=nextcord.Color.from_rgb(237, 91, 6))
        if len(wordlist) > 10:
            embedVar.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[0:10]))
            embedVar.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[10:]))
        else:
            embedVar.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist))
        embedVar.add_field(name="page:", value=f"**{page}/{pages}**", inline=False)
        btn_view = None
        if (pages > 1):
            btn_prev = Button(label="< prev")
            btn_prev.callback = self.cb_slur_list_prev_page
            btn_next = Button(label="next >")
            btn_next.callback = self.cb_slur_list_next_page
            btn_view = View()
            btn_view.add_item(btn_prev)
            btn_view.add_item(btn_next)
        await ctx.send(embed=embedVar, view=btn_view)

    @commands.command(aliases=["lsgw", "lsgoodwords", "listgw"])
    async def listgoodwords(self, ctx, page=1):
        """list current goodwords

        currently whitlested from slur detection, 100 words listed per page"""
        if not await permcheck(ctx, is_mod):
            return

        wordlist, pages, page = get_goodwords(page, 20)

        # post the list as embed
        embedVar = nextcord.Embed(
            title="List of goodwords currently whitelisted from slur detection",
            # description="**•**\u00A0" + "\n**•**\u00A0".join(wordlist),
            color=nextcord.Color.from_rgb(237, 91, 6))
        if len(wordlist) > 10:
            embedVar.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[0:10]))
            embedVar.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist[10:]))
        else:
            embedVar.add_field(name="\u200b", value="**•**\u00A0" + "\n**•**\u00A0".join(wordlist))
        embedVar.add_field(name="page:", value=f"**{page}/{pages}**", inline=False)
        btn_view = None
        if (pages > 1):
            btn_prev = Button(label="< prev")
            btn_prev.callback = self.cb_goodword_list_prev_page
            btn_next = Button(label="next >")
            btn_next.callback = self.cb_goodword_list_next_page
            btn_view = View()
            btn_view.add_item(btn_prev)
            btn_view.add_item(btn_next)
        await ctx.send(embed=embedVar, view=btn_view)

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        detected_slurs = detect_slur(message.content)
        if message.author == self.bot.user:  # ignores message if message is by bot
            return

        elif len(detected_slurs) > 0:  # checks slur heat
            channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
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


def setup(bot):
    bot.add_cog(Slur(bot))
