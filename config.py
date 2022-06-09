import configparser

config = configparser.ConfigParser()


def load_config():
    config.read("config.ini")


def save_config():
    with open("config.ini", "w") as fp:
        config.write(fp)


def get_config_sections():
    section_list = []
    for section in config.sections():
        section_list.append(config[section])
    return section_list


def get_config(module, var, default):
    if module in config:
        if var in config[module]:
            return config[module][var]

    return default     # return the specified default value if configuration setting cannot be found


def get_config_int(module, var, default):
    return int(get_config(module, var, default))

def set_config(module, var, value):
    if module not in config:
        config[module] = {}
    config[module][var] = value
    save_config()
