import configparser
import nextcord
from nextcord.ui import View, Button

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


async def permcheck(hook, function):
    if isinstance(hook, nextcord.ext.commands.Context):
        if function(hook.author):
            return True
        else:
            await hook.send(f"{get_config('EMOTES', 'fail')} Insufficient permission!")

            embed = nextcord.Embed(
                title="Unauthorised Command Usage",
                colour=nextcord.Colour.brand_red())
            embed.add_field(name="Command:", value=hook.command, inline=False)
            embed.add_field(name="Author:", value=hook.author, inline=False)
            embed.add_field(name="Message:", value=hook.message.jump_url, inline=False)

            del hook.args[:2]    # chop off self and ctx of the args
            argstr = ""
            for arg in hook.args:
                argstr += f"• {arg}\n"
            if argstr == "":
                argstr = "`none`"
            embed.add_field(name="Args:", value=argstr, inline=False)

            kwargstr = ""
            for kwarg in hook.kwargs:
                kwargstr += f"• {kwarg}\n"
            if kwargstr == "":
                kwargstr = "`none`"
            embed.add_field(name="Kwargs:", value=kwargstr, inline=False)

            channel = hook.guild.get_channel(get_config_int('CHANNELS', 'logging'))
            await channel.send(embed=embed)

            return False

    elif isinstance(hook, nextcord.Interaction):
        if function(hook.user):
            return True
        else:
            await hook.response.send_message("Sorry, you don't get to vote", ephemeral=True)

            embed = nextcord.Embed(
                title="Unauthorised Interaction",
                colour=nextcord.Colour.brand_red())
            embed.add_field(name="User:", value=hook.user, inline=False)
            embed.add_field(name="Message:", value=hook.message.jump_url, inline=False)

            channel = hook.guild.get_channel(get_config_int('CHANNELS', 'logging'))
            await channel.send(embed=embed)

            return False


def is_staff(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'staff')
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_mod(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'moderator'),
        get_config_int('PERMISSION ROLES', 'trial moderator')
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_full_mod(member: nextcord.Member):
    permitted_roles = [
        get_config_int('PERMISSION ROLES', 'moderator'),
    ]

    for role in member.roles:
        if role.id in permitted_roles:
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
        get_config_int('PERMISSION ROLES', 'senior moderator'),
        get_config_int('PERMISSION ROLES', 'dark moderator')
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


class ConfirmView(View):
    def __init__(self, on_proceed, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        btn_proceed = Button(label="Proceed", style=nextcord.ButtonStyle.green)
        btn_proceed.callback = on_proceed
        btn_cancel = Button(label="Cancel", style=nextcord.ButtonStyle.red)
        btn_cancel.callback = self.cb_cancel
        self.add_item(btn_proceed)
        self.add_item(btn_cancel)

    async def cb_cancel(self, interaction):
        await interaction.message.edit("Action canceled!", embed=None, view=None)

    async def on_timeout(self):
        await self.message.edit("Action timed out!", embed=None, view=None)

    async def interaction_check(self, interaction):
        return interaction.user == interaction.message.reference.cached_message.author

    async def send_as_reply(self, ctx, content: str = None, embed=None):
        self.message = await ctx.reply(content, embed=embed, view=self)

async def cb_check_mod(interaction):
    return await permcheck(interaction, is_mod)


# config stuff below


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
