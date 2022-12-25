# Sersi Offences Commands
# Written by Hekkland


from permutils import is_mod

offenceList = [
    "Intentional Bigotry",
    "Unintentional Bigotry",
    "Spam",
    "NSFW Content",
    "Channel Misuse",
]


def getOffenceList(ctx):
    if is_mod(ctx.author):
        offenceOutput = "\n".join(offenceList)
        return f"__**Adam Something Central Offence List**__\n{offenceOutput}"
    else:
        return "Only moderators can use this command."
