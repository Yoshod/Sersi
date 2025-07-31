import nextcord
from nextcord.ext import commands
from utils.database import SessionLocal, ModeratorRoles


async def get_permissions(member: nextcord.Member):
    permissions = {
        "authority_level": 0,
        "can_warn": False,
        "can_timeout": False,
        "can_immediate_ban": False,
        "can_vote_ban": False,
        "can_unban": False,
        "can_reform": False,
        "can_blacklist": False,
        "can_kick": False,
        "declare_raid": False,
        "add_moderator": False,
        "remove_moderator": False,
        "is_immune": False,
        "edit_offences": False,
        "edit_cases": False,
    }

    role_ids = [role.id for role in member.roles]

    with SessionLocal() as session:
        for role in role_ids:
            role_data = (
                session.query(ModeratorRoles)
                .filter_by(role_id=role, guild_id=member.guild.id)
                .first()
            )

            if role_data is None:
                continue

            permissions["authority_level"] = max(
                permissions["authority_level"], role_data.authority_level
            )
            permissions["can_warn"] = permissions["can_warn"] or role_data.can_warn
            permissions["can_timeout"] = (
                permissions["can_timeout"] or role_data.can_timeout
            )
            permissions["can_immediate_ban"] = (
                permissions["can_immediate_ban"] or role_data.can_immediate_ban
            )
            permissions["can_vote_ban"] = (
                permissions["can_vote_ban"] or role_data.can_vote_ban
            )
            permissions["can_unban"] = permissions["can_unban"] or role_data.can_unban
            permissions["can_reform"] = (
                permissions["can_reform"] or role_data.can_reform
            )
            permissions["can_blacklist"] = (
                permissions["can_blacklist"] or role_data.can_blacklist
            )
            permissions["can_kick"] = permissions["can_kick"] or role_data.can_kick
            permissions["declare_raid"] = (
                permissions["declare_raid"] or role_data.declare_raid
            )
            permissions["add_moderator"] = (
                permissions["add_moderator"] or role_data.add_moderator
            )
            permissions["remove_moderator"] = (
                permissions["remove_moderator"] or role_data.remove_moderator
            )
            permissions["is_immune"] = permissions["is_immune"] or role_data.is_immune
            permissions["edit_offences"] = (
                permissions["edit_offences"] or role_data.edit_offences
            )
            permissions["edit_cases"] = (
                permissions["edit_cases"] or role_data.edit_cases
            )

    return permissions


async def is_sersi_contributor(member: nextcord.Member, bot: commands.Bot) -> bool:
    app_info = await bot.application_info()

    if member.id not in [developer.id for developer in app_info.team.members]:
        return False

    return True
