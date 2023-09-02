import nextcord
import nextcord.ext.commands

from utils import config
from utils.sersi_embed import SersiEmbed

config = config.Configuration.from_yaml_file("./persistent_data/config.yaml")


async def permcheck(
    hook: [nextcord.ext.commands.Context | nextcord.Interaction], function: callable
) -> bool:
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
            args: str = ""
            for arg in hook.args:
                args += f"• {arg}\n"
            if args == "":
                args = "`none`"
            embed.add_field(name="Args:", value=args, inline=False)

            kwargs: str = ""
            for kwarg in hook.kwargs:
                kwargs += f"• {kwarg}: {hook.kwargs[kwarg]}\n"
            if kwargs == "":
                kwargs = "`none`"
            embed.add_field(name="Kwargs:", value=kwargs, inline=False)

            await hook.guild.get_channel(hook.cog.config.channels.logging).send(
                embed=embed
            )

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


def is_staff(member: nextcord.Member) -> bool:
    return is_allowed(
        member,
        [
            config.permission_roles.staff,
            config.permission_roles.trial_moderator,
            config.permission_roles.moderator,
            config.permission_roles.senior_moderator,
            config.permission_roles.cet,
            config.permission_roles.cet_lead,
            config.permission_roles.dark_moderator,
        ],
    )


def is_mod(member: nextcord.Member) -> bool:
    return is_allowed(
        member,
        [
            config.permission_roles.moderator,
            config.permission_roles.trial_moderator,
        ],
    )


def is_full_mod(member: nextcord.Member) -> bool:
    return is_allowed(member, [config.permission_roles.moderator])


def is_dark_mod(member: nextcord.Member) -> bool:
    return is_allowed(member, [config.permission_roles.dark_moderator])


def is_senior_mod(member: nextcord.Member) -> bool:
    return is_allowed(
        member,
        [
            config.permission_roles.senior_moderator,
            config.permission_roles.dark_moderator,
        ],
    )


def is_cet_lead(member: nextcord.Member) -> bool:
    return is_allowed(member, [config.permission_roles.cet_lead])


def is_slt(member: nextcord.Member) -> bool:
    return is_allowed(
        member,
        [
            config.permission_roles.cet_lead,
            config.permission_roles.senior_moderator,
            config.permission_roles.compliance,
            config.permission_roles.dark_moderator,
        ],
    )


def is_sersi_contributor(member: nextcord.Member) -> bool:
    return is_allowed(member, [config.permission_roles.sersi_contributor])


def is_cet(member: nextcord.Member) -> bool:
    return is_allowed(
        member, [config.permission_roles.cet, config.permission_roles.cet_lead]
    )


def is_immune(member: nextcord.Member) -> bool:
    return is_allowed(member, [config.permission_roles.dark_moderator])


def target_eligibility(actor: nextcord.Member, target: nextcord.Member) -> bool:
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
) -> bool:
    if permitted_roles is None:
        permitted_roles = []

    for role in member.roles:
        if role in permitted_roles:
            return True
    return False


def is_allowed(member: nextcord.Member, roles: list[int]) -> bool:
    for role in member.roles:
        if role.id in roles:
            return True
    return False


async def cb_is_mod(interaction) -> bool:
    return await permcheck(interaction, is_mod)


async def cb_is_dark_mod(interaction) -> bool:
    return await permcheck(interaction, is_dark_mod)


async def cb_is_cet(interaction) -> bool:
    return await permcheck(interaction, is_cet)
