import nextcord
import nextcord.ext.commands
import configutils

config = configutils.Configuration.from_yaml_file("./persistent_data/config.yaml")


async def permcheck(hook, function):
    if isinstance(hook, nextcord.ext.commands.Context):
        if function is True:
            return True
        elif function(hook.author):
            return True
        else:
            await hook.send(f"{config.emotes.fail} Insufficient permission!")

            embed = nextcord.Embed(
                title="Unauthorised Command Usage", colour=nextcord.Colour.brand_red()
            )
            embed.add_field(name="Command:", value=hook.command, inline=False)
            embed.add_field(
                name="Author:", value=f"{hook.author} ({hook.author.id})", inline=False
            )
            embed.add_field(name="Message:", value=hook.message.jump_url, inline=False)

            del hook.args[:2]  # chop off self and ctx off the args
            argstr = ""
            for arg in hook.args:
                argstr += f"• {arg}\n"
            if argstr == "":
                argstr = "`none`"
            embed.add_field(name="Args:", value=argstr, inline=False)

            kwargstr = ""
            for kwarg in hook.kwargs:
                kwargstr += f"• {kwarg}: {hook.kwargs[kwarg]}\n"
            if kwargstr == "":
                kwargstr = "`none`"
            embed.add_field(name="Kwargs:", value=kwargstr, inline=False)

            channel = hook.guild.get_channel(hook.cog.config.channels.logging)
            await channel.send(embed=embed)

            return False

    elif isinstance(hook, nextcord.Interaction):
        if function(hook.user):
            return True
        else:
            await hook.response.send_message(
                f"{config.emotes.fail} Permission denied.", ephemeral=True
            )

            embed = nextcord.Embed(
                title="Unauthorised Interaction", colour=nextcord.Colour.brand_red()
            )
            embed.add_field(
                name="User:", value=f"{hook.user} ({hook.user.id})", inline=False
            )
            embed.add_field(name="Message:", value=hook.message.jump_url, inline=False)

            channel = hook.guild.get_channel(config.channels.logging)
            await channel.send(embed=embed)

            return False


def is_staff(member: nextcord.Member):
    permitted_roles = [config.permission_roles.staff]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_mod(member: nextcord.Member):
    permitted_roles = [
        config.permission_roles.moderator,
        config.permission_roles.trial_moderator,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_full_mod(member: nextcord.Member):
    permitted_roles = [config.permission_roles.moderator]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_dark_mod(member: nextcord.Member):
    permitted_roles = [config.permission_roles.dark_moderator]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_senior_mod(member: nextcord.Member):
    permitted_roles = [
        config.permission_roles.senior_moderator,
        config.permission_roles.dark_moderator,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_cet_lead(member: nextcord.Member):
    permitted_roles = [config.permission_roles.cet_lead]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_slt(member: nextcord.Member):
    permitted_roles = [
        config.permission_roles.cet_lead,
        config.permission_roles.senior_moderator,
        config.permission_roles.dark_moderator,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_sersi_contrib(member: nextcord.Member):
    permitted_roles = [config.permission_roles.sersi_contributor]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_cet(member: nextcord.Member):
    permitted_roles = [config.permission_roles.cet, config.permission_roles.cet_lead]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


# This does not work, perhaps if I knew more about why I could fix it
def is_custom_role(
    member: nextcord.Member, permitted_roles: list[nextcord.Role] = None
):
    if permitted_roles is None:
        permitted_roles = []

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


async def cb_is_mod(interaction):
    return await permcheck(interaction, is_mod)


async def cb_is_dark_mod(interaction):
    return await permcheck(interaction, is_dark_mod)


async def cb_is_cet(interaction):
    return await permcheck(interaction, is_cet)
