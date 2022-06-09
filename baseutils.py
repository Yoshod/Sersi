import configparser

def checkForMods(messageData):
    for modmention in ["<@&856424878437040168>", "<@&963537133589643304>", "<@&875805670799179799>", "<@&883255791610638366>", "<@&977939552641613864>"]:
        if modmention in messageData:
            return True
    return False


def isStaff(userRoles):
    staffRolePresent = False
    for role in userRoles:
        if role.id in [974166116618350642, 977394150494326855]:  # "Staff", "certified bot tester"
            staffRolePresent = True
    return (staffRolePresent)


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
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['CHANNELS']['alert'])


def getLoggingChannel(guild_id):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['CHANNELS']['logging'])


def getFalsePositivesChannel(guild_id):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['CHANNELS']['false positives'])


def getReformationRole(guild_id):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['ROLES']['reformation'])


def getReformedRole(guild_id):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['ROLES']['reformed'])


def getProbationRole(guild_id):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['ROLES']['probation'])


def getModlogsChannel(guild_id):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return int(config['CHANNELS']['modlogs'])


def ajustCommandPrefix(bot):
    if bot.user.id == 978259801844879373:   # Sersi(cracked)
        bot.command_prefix = "cs!"
