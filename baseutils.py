import configparser

# 856262303795380224 asc guild id
# 977377117895536640 mfs guild id


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


def ajustCommandPrefix(bot):
    if bot.user.id == 978259801844879373:   # Sersi(cracked)
        bot.command_prefix = "cs!"


def get_config(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    if module in config:
        module = config[module]
        return int(module.get(var, default))


def set_config(module, var, value):
    config = configparser.ConfigParser()
    config.read("config.ini")

    if module not in config:
        config[module] = {}     # sets new category is not exist

    config[module][var] = value

    with open("config.ini", "w") as file:
        config.write(file)
