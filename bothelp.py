import nextcord

from baseutils import *

docs = {
		"about": "shows basic information about the bot",
		"help": "get documention for the bot or specific command\n\
			*syntax:* `s!help [command]`",
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
	
async def get_help(ctx, command):
	if isMod(ctx.author.roles):
		if command in docs.keys():
			embedVar = nextcord.Embed(
				title=f"Sersi help: {command}", description=docs[command], color=nextcord.Color.from_rgb(237,91,6))
			await ctx.send(embed=embedVar)
		elif command is None:
			embedVar = nextcord.Embed(
				title="Sersi help\n", description="use `s!help command` to get documentation on specific command\n\
					 list of currently implemented commands:\n`"
					 + str(", ".join(docs.keys()))
					 + "`"
					 , color=nextcord.Color.from_rgb(237,91,6))
			await ctx.send(embed=embedVar)
		else:
			embedVar = nextcord.Embed(
				title=f"Sersi help: {command}", description="unknown command, use `s!help` to get list of commands", color=nextcord.Color.from_rgb(237,91,6))
			await ctx.send(embed=embedVar)
	else:
		await ctx.send("https://en.wikipedia.org/wiki/Nineteen_Eighty-Four")