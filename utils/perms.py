import nextcord
import nextcord.ext.commands
from utils import config
from utils.base import SersiEmbed

config = config.Configuration.from_yaml_file("./persistent_data/config.yaml")


async def permcheck(hook, function):
    if isinstance(hook, nextcord.ext.commands.Context):
        if function is True:
            return True
        elif function(hook.author):
            return True
        else:
            await hook.send(f"{config.emotes.fail} Insufficient permission!")

            embed: nextcord.Embed = SersiEmbed(
                title="Unauthorised Command Usage",
                colour=nextcord.Colour.brand_red(),
                fields={
                    "Command:": f"{hook.command}",
                    "Author:": f"{hook.author} ({hook.author.id})",
                    "Message:": hook.message.jump_url,
                },
            )

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

            await hook.guild.get_channel(config.channels.logging).send(
                embed=SersiEmbed(
                    title="Unauthorised Interaction",
                    colour=nextcord.Colour.brand_red(),
                    fields={
                        "User:": f"{hook.user} ({hook.user.id})",
                        "Message:": hook.message.jump_url,
                    },
                )
            )

            return False


def is_staff(member: nextcord.Member):
    permitted_roles: list[int] = [
        config.permission_roles.staff,
        config.permission_roles.trial_moderator,
        config.permission_roles.moderator,
        config.permission_roles.senior_moderator,
        config.permission_roles.cet,
        config.permission_roles.cet_lead,
        config.permission_roles.dark_moderator,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_mod(member: nextcord.Member):
    permitted_roles: list[int] = [
        config.permission_roles.moderator,
        config.permission_roles.trial_moderator,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_full_mod(member: nextcord.Member):
    permitted_roles: list[int] = [config.permission_roles.moderator]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_dark_mod(member: nextcord.Member):
    permitted_roles: list[int] = [config.permission_roles.dark_moderator]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_senior_mod(member: nextcord.Member):
    permitted_roles: list[int] = [
        config.permission_roles.senior_moderator,
        config.permission_roles.dark_moderator,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_cet_lead(member: nextcord.Member):
    permitted_roles: list[int] = [config.permission_roles.cet_lead]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_slt(member: nextcord.Member):
    permitted_roles: list[int] = [
        config.permission_roles.cet_lead,
        config.permission_roles.senior_moderator,
        config.permission_roles.dark_moderator,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_sersi_contrib(member: nextcord.Member):
    permitted_roles: list[int] = [config.permission_roles.sersi_contributor]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_cet(member: nextcord.Member):
    permitted_roles: list[int] = [
        config.permission_roles.cet,
        config.permission_roles.cet_lead,
    ]

    for role in member.roles:
        if role.id in permitted_roles:
            return True
    return False


def is_immune(member: nextcord.Member):
    immune_roles: list[int] = [
        config.permission_roles.dark_moderator,
        config.permission_roles.cet_lead,
        config.permission_roles.senior_moderator,
        config.permission_roles.moderator,
        config.permission_roles.trial_moderator,
    ]

    for role in member.roles:
        if role.id in immune_roles:
            return True
    return False


def target_eligibility(actor: nextcord.Member, target: nextcord.Member):
    hierarchy: dict[int:int] = {
        config.permission_roles.dark_moderator: 10,
        config.permission_roles.cet_lead: 3,
        config.permission_roles.senior_moderator: 3,
        config.permission_roles.moderator: 2,
        config.permission_roles.cet: 2,
        config.permission_roles.trial_moderator: 2,
    }

    actor_rank = 0
    target_rank = 0

    for role in actor.roles:
        rank = hierarchy.get(role.id, 0)
        actor_rank = max(actor_rank, rank)

    for role in target.roles:
        rank = hierarchy.get(role.id, 0)
        target_rank = max(target_rank, rank)

    return actor_rank > target_rank


def is_custom_role(
    member: nextcord.Member, permitted_roles: list[nextcord.Role] = None
):
    if permitted_roles is None:
        permitted_roles = []

    for role in member.roles:
        if role in permitted_roles:
            return True
    return False


async def cb_is_mod(interaction):
    return await permcheck(interaction, is_mod)


async def cb_is_dark_mod(interaction):
    return await permcheck(interaction, is_dark_mod)


async def cb_is_cet(interaction):
    return await permcheck(interaction, is_cet)
