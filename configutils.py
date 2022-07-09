import configparser


def get_options(module):
    config = configparser.ConfigParser()
    config.read("config.ini")
    if module not in config:
        return []
    return config[module]


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


def get_config_int(module, var, default=0):
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.getint(module, var, fallback=default)


def get_config_float(module, var, default=0.0):
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config.getfloat(module, var, fallback=default)


def get_config_list(module, var, default=[]):
    config = configparser.ConfigParser()
    config.read("config.ini")
    value = config.get(module, var, fallback=None)
    if value is None:
        return default
    else:
        return value.split(",")


def set_config(module, var, value):
    config = configparser.ConfigParser()
    config.read("config.ini")
    module = module.upper()

    if module not in config:
        config[module] = {}     # sets new category if not exist

    config[module][var] = value

    with open("config.ini", "w") as file:
        config.write(file)
