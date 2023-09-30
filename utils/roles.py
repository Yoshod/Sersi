import nextcord


def parse_roles(guild: nextcord.Guild, *roles: nextcord.Role | int):
    """Parses roles for use in role assignment/removal on member."""
    for role in roles:
        match role:
            case nextcord.Role():
                yield role
            case int():
                role_obj = guild.get_role(role)
                if role_obj is not None:
                    yield role_obj
