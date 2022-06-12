import configparser
import nextcord

# 856262303795380224 asc guild id
# 977377117895536640 mfs guild id


def modmention_check(messageData):
    for modmention in ["<@&856424878437040168>", "<@&963537133589643304>", "<@&875805670799179799>", "<@&883255791610638366>", "<@&977939552641613864>"]:
        if modmention in messageData:
            return True
    return False


def is_staff(member: nextcord.Member):
    for role in member.roles:
        if role.id in [974166116618350642, 977394150494326855]:  # "Staff", "certified bot tester"
            return True
    return False


def is_mod(member: nextcord.Member):
    for role in member.roles:
        if role.id in [856424878437040168, 883255791610638366, 977394150494326855]:  # "Moderator", "Trial Moderator", "certified bot tester"
            return True
    return False


def is_dark_mod(member: nextcord.Member):
    for role in member.roles:
        if role.id == 875805670799179799:
            return True
    return False


def is_sersi_contrib(member: nextcord.Member):
    for role in member.roles:
        if role.id in [977602747786493972, 977394150494326855]:
            return True
    return False


def setting_present(module, var):
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.has_option(module, var)


def get_config(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.get(module, var, fallback=default)


def get_config_bool(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.getboolean(module, var, fallback=default)


def get_config_int(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    config.getint(module, var, fallback=default)


def set_config(module, var, value):
    config = configparser.ConfigParser()
    config.read("config.ini")

    if module not in config:
        config[module] = {}     # sets new category if not exist

    config[module][var] = value

    with open("config.ini", "w") as file:
        config.write(file)
