import configparser
import nextcord

# 856262303795380224 asc guild id
# 977377117895536640 mfs guild id


def modmention_check(messageData):
    modmentions = [
        f"<@&{get_config_int('PERMISSION ROLES', 'trial moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'senior moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'dark moderator')}>"
    ]

    for modmention in modmentions:
        if modmention in messageData:
            return True
    return False


def is_staff(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'staff')
    ]

    for role in member.roles:
        if role.id in permitted_roles:  # "Staff", "certified bot tester"
            return True
    return False


def is_mod(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'moderator'),
        get_config_int('PERMISSION ROLES', 'trial moderator')
    ]

    for role in member.roles:
        if role.id in permitted_roles:  # "Moderator", "Trial Moderator", "certified bot tester"
            return True
    return False


def is_dark_mod(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'dark moderator')
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_senior_mod(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'senior moderator')
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_sersi_contrib(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'sersi contributor')
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def setting_present(module, var):
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.has_option(module, var)


def get_config(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.get(module, var, fallback=default)


def get_config_bool(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.getboolean(module, var, fallback=default)


def get_config_int(module, var, default=None):
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.getint(module, var, fallback=default)


def set_config(module, var, value):
    config = configparser.ConfigParser()
    config.read("config.ini")
    module = module.upper()

    if module not in config:
        config[module] = {}     # sets new category if not exist

    config[module][var] = value

    with open("config.ini", "w") as file:
        config.write(file)
