import nextcord
from configutils import get_config, get_config_int


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

            del hook.args[:2]    # chop off self and ctx off the args
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
