import nextcord
from slurdetector import *
from baseutils import *
# from buttoncallbacks import *

from nextcord.ext import commands
from nextcord.ui import Button, View


class Slur(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.notModFail = "<:sersifail:979070135799279698> Only moderators can use this command."
        load_slurdetector()

    async def cb_action_taken(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
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
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
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
        channel = self.bot.get_channel(getFalsePositivesChannel(interaction.guild_id))

        embedVar = nextcord.Embed(
            title="Marked as false positive",
            color=nextcord.Color.from_rgb(237, 91, 6))

        for field in new_embed.fields:
            if field.name in ["Context:", "Slurs Found:"]:
                embedVar.add_field(name=field.name, value=field.value, inline=False)

        embedVar.add_field(name="Report URL:", value="interaction.message.jump_url", inline=False)
        await channel.send(embed=embedVar)

        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
        embedLogVar = nextcord.Embed(
            title="False Positive Pressed",
            description="Detected slur has been deemed a false positive by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    @commands.command()
    async def addslur(self, ctx, slur):
        """adds a new slur to the list of slurs to detect."""
        if isMod(ctx.author.roles):
            slur = clearString(slur)
            if slur in slurs:
                await ctx.send(f"{slur} is already on the list of slurs")
                return

            await ctx.send(f"Slur to be added: {slur}")
            with open("slurs.txt", "a") as file:
                file.write(slur)
                file.write("\n")
            load_slurs()    # reloads updated list into memory

            # logging
            channel = self.bot.get_channel(getLoggingChannel(ctx.message.guild.id))
            embedVar = nextcord.Embed(
                title="Slur Added",
                description="A new slur has been added to the filter.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.add_field(name="Added By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
            embedVar.add_field(name="Slur Added:", value=slur, inline=False)
            await channel.send(embed=embedVar)
            await ctx.send("<:sersisuccess:979066662856822844> Slur added. Detection will start now.")
        else:
            await ctx.send(self.notModFail)

    @commands.command()
    async def addgoodword(self, ctx, word):
        """adds a new goodword into the whitelist to not detect substring slurs in."""
        if isMod(ctx.author.roles):
            word = clearString(word)
            if word in goodword:
                await ctx.send(f"{word} is already on the whitelist")
                return

            await ctx.send(f"Goodword to be added: {word}")
            with open("goodword.txt", "a") as file:
                file.write(word)
                file.write("\n")
            load_goodwords()    # reloads updated list into memory

            # logging
            channel = self.bot.get_channel(getLoggingChannel(ctx.message.guild.id))
            embedVar = nextcord.Embed(
                title="Goodword Added",
                description="A new goodword has been added to the filter.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.add_field(name="Added By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
            embedVar.add_field(name="Goodword Added:", value=word, inline=False)
            await channel.send(embed=embedVar)
            await ctx.send("<:sersisuccess:979066662856822844> Goodword added. Detection will start now.")
        else:
            await ctx.send(self.notModFail)

    @commands.command()
    async def removeslur(self, ctx, slur):
        """removes a slur from the list to no longer be detected."""
        if isMod(ctx.author.roles):
            rmSlur(ctx, slur)

            # logging
            channel = self.bot.get_channel(getLoggingChannel(ctx.message.guild.id))
            embedVar = nextcord.Embed(
                title="Slur Removed",
                description="A slur has been removed from the filter.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.add_field(name="Removed By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
            embedVar.add_field(name="Slur Removed:", value=slur, inline=False)
            await channel.send(embed=embedVar)
            await ctx.send(f"<:sersisuccess:979066662856822844> Slur {slur} is no longer in the list")
        else:
            await ctx.send(self.notModFail)

    @commands.command()
    async def removegoodword(self, ctx, word):
        """removes a goodword from the whitelist."""
        if isMod(ctx.author.roles):
            rmGoodword(ctx, word)

            # logging
            channel = self.bot.get_channel(getLoggingChannel(ctx.message.guild.id))
            embedVar = nextcord.Embed(
                title="Goodword Removed",
                description="A goodword has been removed from the filter.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.add_field(name="Removed By:", value=f"{ctx.message.author.mention} ({ctx.message.author.id})", inline=False)
            embedVar.add_field(name="Goodword Removed:", value=word, inline=False)
            await channel.send(embed=embedVar)
            await ctx.send(f"<:sersisuccess:979066662856822844> Goodword {word} is no longer in the list")
        else:
            await ctx.send(self.notModFail)

    @commands.command()
    async def listslurs(self, ctx, page=1):
        """lists slurs currently being detected by the bot, 100 slurs listed per page."""
        if isMod(ctx.author.roles):
            wordlist = []
            pages, index = 1, 0

            with open("slurs.txt", "r") as file:
                for line in file:
                    wordlist.append(line[0:-1])
            wordlist.sort()

            # check if multiple pages are needed, 100 slurs per page will be listed
            if len(wordlist) > 100:
                pages += (len(wordlist) - 1) // 100

                # get the index of the current page
                index = int(page) - 1
                if index < 0:
                    index = 0
                elif index >= pages:
                    index = pages - 1

                # update the list to a subsection according to the index
                if index == (pages - 1):
                    templist = wordlist[index * 100:]
                else:
                    templist = wordlist[index * 100: index * 100 + 100]
                wordlist = templist

            # post the list as embed
            embedVar = nextcord.Embed(
                title="List of currently detected slurs",
                description=str(", ".join(wordlist))
                + "\n\n**page "
                + str(index + 1)
                + "/"
                + str(pages)
                + "**",
                color=nextcord.Color.from_rgb(237, 91, 6))
            await ctx.send(embed=embedVar)
        else:
            await ctx.send(self.notModFail)

    @commands.command()
    async def listgoodwords(self, ctx, page=1):
        """lists goodwords currently whitlested from slur detection, 100 words listed per page"""
        if isMod(ctx.author.roles):
            wordlist = []
            pages, index = 1, 0

            with open("goodword.txt", "r") as file:
                for line in file:
                    wordlist.append(line[0:-1])
            wordlist.sort()

            # check if multiple pages are needed, 100 goodwords per page will be listed
            if len(wordlist) > 100:
                pages += (len(wordlist) - 1) // 100

                # get the index of the current page
                index = int(page) - 1
                if index < 0:
                    index = 0
                elif index >= pages:
                    index = pages - 1

                # update the list to a subsection according to the index
                if index == (pages - 1):
                    templist = wordlist[index * 100:]
                else:
                    templist = wordlist[index * 100: index * 100 + 100]
                wordlist = templist

            embedVar = nextcord.Embed(
                title="List of words currently whitelisted from slur detection",
                description=str(", ".join(wordlist))
                + "\n\n**page "
                + str(index + 1)
                + "/"
                + str(pages)
                + "**",
                color=nextcord.Color.from_rgb(237, 91, 6))
            await ctx.send(embed=embedVar)
        else:
            await ctx.send(self.notModFail)

    @commands.command()
    async def reloadslurs(self, ctx):
        """reloads the lists of detected slurs and whitelisted goodwords from files"""
        if isMod(ctx.author.roles):
            load_goodwords()
            load_slurs()

            # Logging
            channel = self.bot.get_channel(getLoggingChannel(ctx.message.guild.id))
            embedVar = nextcord.Embed(
                title="Slurs and Goodwords Reloaded",
                description="The list of slurs and goodwords in memory has been reloaded.\n\n__Reloaded By:__\n"
                + str(ctx.message.author.mention)
                + " ("
                + str(ctx.message.author.id)
                + ")",
                color=nextcord.Color.from_rgb(237, 91, 6))
            await channel.send(embed=embedVar)
        else:
            await ctx.send(self.notModFail)

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        detected_slurs = detectSlur(message.content)
        if message.author == self.bot.user:  # ignores message if message is by bot
            return

        elif len(detected_slurs) > 0:  # checks slur heat
            channel = self.bot.get_channel(getAlertChannel(message.guild.id))
            slurembed = nextcord.Embed(
                title="Slur(s) Detected",
                description="A slur has been detected. Moderation action is advised.",
                color=nextcord.Color.from_rgb(237, 91, 6)
            )
            slurembed.add_field(name="Channel:", value=message.channel.mention, inline=False)
            slurembed.add_field(name="User:", value=message.author.mention)
            slurembed.add_field(name="Context:", value=message.content, inline=False)
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

            await channel.send(embed=slurembed, view=button_view)


def setup(bot):
    bot.add_cog(Slur(bot))
