import nextcord

from nextcord.ext import commands
from baseutils import *

class Bothelp(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.docs = {
				"slurs": "when the bot detects a slur, it sends an alert to <#897874682198511648>, \
					the alert shows the offending message, its author and the detected slur(s).\n\n\
					__buttons for moderator response:__\n\
					`Action Taken`: press after you have taken an action against the offending user\n\
					`Acceptable Use`: press when you deem the slur usage to be acceptable per server rules\n\
					`False Positive`: press when the slur is detected as a substring of a non-offensive word\n\n\
					messages containing false positives are sent to <#978078399635550269>, \
					consider if a new goodword should be added via the `s!addgoodword <word>` command.\n\n\
					**relevant commands:** `addslur`, `addgoodword`, `removeslur`, `removegoodword`, `listslurs`, `listgoodwords`, `reload`",
				"mentions": "when a moderator role is mentioned in message, the bot sends an alert to <#897874682198511648>, \
					the alert shows the message containing the mention and its author.\n\n\
					__buttons for moderator response:__\n\
					`Action Taken`: press after you have taken an action based on the report\n\
					`Action Not Necessary`: press when the report was made in good faith, \
					but no action was deemed necessary\n\
					`Bad Faith Ping`: press when the user made the mention in bad faith, eg. trolling, mod ping spam...",
				"about": "shows basic information about the bot",
				"docs": "get a specific documentation entry\n\
					*syntax:* `s!docs [entry_name]`",
				"help": "get a list of currently loaded cogs and commands\n\
					use `s!help [command] for more extensive info on command`",
				"ping": "test the response time of the bot",
				"addslur": "adds a new slur to the list of slurs to detect\n\
					*syntax:* `s!addslur <slur>`",
				"addgoodword": "adds a new goodword into the whitelist to not detect substring slurs in\n\
					*syntax:* `s!addgoodword <goodword>`",
				"removeslur": "removes a slur from the list to no longer be detected\n\
					*syntax:* `s!removeslur <slur>`",
				"removegoodword": "removes a goodword from the whitelist\n\
					*syntax:* `s!removegoodword <goodword>`",
				"listslurs": "lists slurs currently being detected by the bot, 100 slurs listed per page\n\
					*syntax:* `s!listslurs [page]`",
				"listgoodwords": "list goodwords currently whitlested from slur detection, 100 words listed per page\n\
					*syntax* `s!listgoodwords [page]`",
				"reload": "reloads the lists of detected slurs and whitelisted goodwords from files",
				}
		
	@commands.command()
	async def docs(self, ctx, entry=None):
		if isMod(ctx.author.roles):
			if entry in self.docs.keys():
				embedVar = nextcord.Embed(
					title=f"Sersi help: {entry}", description=self.docs[entry], color=nextcord.Color.from_rgb(237,91,6))
				embedVar.colour=nextcord.Colour.teal()
				await ctx.send(embed=embedVar)
			elif entry is None:
				embedVar = nextcord.Embed(
					title="Sersi help\n", description="use `s!docs entry_name` to get a specific documentation entry\n\n\
						__list of currently available entries:__\n`"
						+ str(", ".join(self.docs.keys()))
						+ "`",
						color=nextcord.Color.from_rgb(237,91,6))
				embedVar.colour=nextcord.Colour.teal()
				await ctx.send(embed=embedVar)
			else:
				embedVar = nextcord.Embed(
					title=f"Sersi help: {entry}", description="unknown entry, use `s!docs` to get list of all available entries", color=nextcord.Color.from_rgb(237,91,6))
				embedVar.colour=nextcord.Colour.brand_red()
				await ctx.send(embed=embedVar)
		else:
			await ctx.send("https://en.wikipedia.org/wiki/Nineteen_Eighty-Four")
				
def setup(bot):
	bot.add_cog(Bothelp(bot))