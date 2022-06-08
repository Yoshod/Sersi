
def checkForMods(messageData):
    for modmention in ["<@&856424878437040168>", "<@&963537133589643304>", "<@&875805670799179799>", "<@&883255791610638366>", "<@&977939552641613864>"]:
        if modmention in messageData:
            return True
    return False


def isMod(userRoles):
    modRolePresent = False
    for role in userRoles:
        if role.id in [856424878437040168, 883255791610638366, 977394150494326855]:  # "Moderator", "Trial Moderator", "certified bot tester"
            modRolePresent = True
    return (modRolePresent)


def isDarkMod(userRoles):
    darkModPresent = False
    for role in userRoles:
        if 875805670799179799 == role.id:
            darkModPresent = True
    return darkModPresent


def isSersiContrib(userRoles):
    sersiContrib = False
    for role in userRoles:
        if role.id in [977602747786493972, 977394150494326855]:
            sersiContrib = True
    return sersiContrib


def getAlertChannel(guild_id):
    if guild_id == 856262303795380224:      # asc
        return 897874682198511648           # information-centre
    elif guild_id == 977377117895536640:    # the proving grounds
        return 977377171054166037           # replies


def getLoggingChannel(guild_id):
    if guild_id == 856262303795380224:      # asc
        return 977609240107700244           # sersi-logs
    elif guild_id == 977377117895536640:    # the proving grounds
        return 977925156330672198           # logging


def getFalsePositivesChannel(guild_id):
    if guild_id == 856262303795380224:      # asc
        return 978078399635550269           # sersi-logs
    elif guild_id == 977377117895536640:    # the proving grounds
        return 978079399066882059           # logging


def getReformationRole(guild_id):
    if guild_id == 856262303795380224:
        return 878289857527562310
    elif guild_id == 977377117895536640:
        return 978334782968721468


def getReformedRole(guild_id):
    if guild_id == 856262303795380224:
        return 878289678623703080
    elif guild_id == 977377117895536640:
        return 978591187827044383


def getModlogsChannel(guild_id):
    if guild_id == 856262303795380224:
        return 903367950554259466
    elif guild_id == 977377117895536640:
        return 978346814904336484


def ajustCommandPrefix(bot):
    if bot.user.id == 978259801844879373:   # Sersi(cracked)
        bot.command_prefix = "cs!"
