import configparser

# 856262303795380224 asc guild id
# 977377117895536640 mfs guild id


def checkForMods(messageData):
    for modmention in ["<@&856424878437040168>", "<@&963537133589643304>", "<@&875805670799179799>", "<@&883255791610638366>", "<@&977939552641613864>"]:
        if modmention in messageData:
            return True
    return False


def isStaff(userRoles):
    for role in userRoles:
        if role.id in [974166116618350642, 977394150494326855]:  # "Staff", "certified bot tester"
            return True
    return False


def isMod(userRoles):
    for role in userRoles:
        if role.id in [856424878437040168, 883255791610638366, 977394150494326855]:  # "Moderator", "Trial Moderator", "certified bot tester"
            return True
    return False


def isDarkMod(userRoles):
    for role in userRoles:
        if 875805670799179799 == role.id:
            return True
    return False


def isSersiContrib(userRoles):
    for role in userRoles:
        if role.id in [977602747786493972, 977394150494326855]:
            return True
    return False


def get_config(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    if module in config:
        module = config[module]
        return module.get(var, default)


def get_config_bool(module, var, default=None):
    return get_config(module, var, default).lower() == "true"


def get_config_int(module, var, default=None):
    return int(get_config(module, var, default))


def set_config(module, var, value):
    config = configparser.ConfigParser()
    config.read("config.ini")

    if module not in config:
        config[module] = {}     # sets new category is not exist

    config[module][var] = value

    with open("config.ini", "w") as file:
        config.write(file)
