# Sersi Offences Commands
# Written by Hekkland


from baseutils import isMod

offenceList = ["Intentional Bigotry", "Unintentional Bigotry", "Spam", "NSFW Content", "Channel Misuse"]


def getOffenceList(ctx):
    if isMod(ctx.author.roles):
        offenceOutput = "\n".join(offenceList)
        return f"__**Adam Something Central Offence List**__\n{offenceOutput}"
    else:
        return "Only moderators can use this command."
