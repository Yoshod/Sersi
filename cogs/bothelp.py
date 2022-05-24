import nextcord

from nextcord.ext import commands
from baseutils import *


class Bothelp(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.docs = {
            "slurs": "When Sersi detects a slur, it sends an alert to <#897874682198511648>. \
                The alert shows the offending message, its author, and the detected slur(s).\n\n\
                __Buttons For Moderator Response:__\n\
                `Action Taken`: Press this after you have taken an action against the offending user.\n\
                `Acceptable Use`: Press this when you deem the slur usage to be in line with server rules.\n\
                `False Positive`: Press when the slur is detected as a substring of a non-offensive word.\n\n\
                Messages containing false positives are sent to <#978078399635550269>, \
                consider if a new goodword should be added via the `s!addgoodword <word>` command.\n\n\
                **Relevant Commands:** `addslur`, `addgoodword`, `removeslur`, `removegoodword`, `listslurs`, `listgoodwords`, `reload`.",
            "mentions": "When a moderator role is mentioned in message, Sersi sends an alert to <#897874682198511648>. \
                The alert shows the message containing the mention and its author.\n\n\
                __Buttons For Moderator Response:__\n\
                `Action Taken`: Press this after you have taken an action based on the report.\n\
                `Action Not Necessary`: Press this when the report was made in good faith, \
                but no action was deemed necessary.\n\
                    `Bad Faith Ping`: Press this when the user made the mention in bad faith such as trolling or mod ping spam.",
            "about": "Shows basic information about Sersi.",
            "docs": "Get a specific documentation entry.\n\
                    *syntax:* `s!docs [entry_name]`",
            "help": "Gets a list of currently loaded cogs and commands.\n\
                    use `s!help [command] for more extensive info on command`",
            "ping": "Tests the latency of the Sersi.",
            "addslur": "Adds a new slur to the list of slurs to detect.\n\
                    *syntax:* `s!addslur <slur>`",
            "addgoodword": "Adds a new goodword into the whitelist of words to not detect substring slurs in.\n\
                    *syntax:* `s!addgoodword <goodword>`",
            "removeslur": "Removes a word from the list of slurs to no longer be detected.\n\
                    *syntax:* `s!removeslur <slur>`",
            "removegoodword": "Removes a word from the goodword whitelist.\n\
                    *syntax:* `s!removegoodword <goodword>`",
            "listslurs": "Lists all slurs currently being detected by Sersi with a maximum of 100 slurs listed per page.\n\
                    *syntax:* `s!listslurs [page]`",
            "listgoodwords": "Lists all goodwords currently whitlested from slur detection with a maximum of 100 words listed per page.\n\
                    *syntax* `s!listgoodwords [page]`"}

    @commands.command()
    async def docs(self, ctx, entry=None):
        if isMod(ctx.author.roles):
            if entry in self.docs.keys():
                embedVar = nextcord.Embed(
                    title=f"Sersi Help: {entry}", description=self.docs[entry], color=nextcord.Color.from_rgb(237, 91, 6))
                embedVar.colour = nextcord.Colour.teal()
                await ctx.send(embed=embedVar)
            elif entry is None:
                embedVar = nextcord.Embed(
                    title="Sersi help\n", description="Use `s!docs entry_name` to get a specific documentation entry.\n\n\
                        __List of Currently Available Entries:__\n`"
                    + str(", ".join(self.docs.keys()))
                    + "`",
                    color=nextcord.Color.from_rgb(237, 91, 6))
                embedVar.colour = nextcord.Colour.teal()
                await ctx.send(embed=embedVar)
            else:
                embedVar = nextcord.Embed(
                    title=f"Sersi Help: {entry}", description="unknown entry, use `s!docs` to get list of all available entries", color=nextcord.Color.from_rgb(237, 91, 6))
                embedVar.colour = nextcord.Colour.brand_red()
                await ctx.send(embed=embedVar)
        else:
            await ctx.send("https://en.wikipedia.org/wiki/Nineteen_Eighty-Four")


def setup(bot):
    bot.add_cog(Bothelp(bot))
