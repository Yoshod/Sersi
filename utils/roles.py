import nextcord

async def give_role(
    memeber: nextcord.Member|int,
    role: nextcord.Role|int,
    guild: nextcord.Guild = None,
    reason: str = None,
):
    """
    Gives a role to a member

    Args:
        memeber (nextcord.Member|int): Member to give role to
        role (nextcord.Role|int): Role to give
        guild (nextcord.Guild, optional): Guild to get member and role from.
            Defaults to None, required if memeber or role is an int.
        reason (str, optional): Reason for audit log. Defaults to None. 
    """

    if isinstance(memeber, int) and guild is not None:
        memeber = guild.get_member(memeber)
    if isinstance(role, int) and guild is not None:
        role = guild.get_role(role)
    if memeber is None or role is None:
        return
    if role not in memeber.roles:
        try:
            await memeber.add_roles(role, reason=reason, atomic=True)
        except Exception:
            pass

async def remove_role(
    memeber: nextcord.Member|int,
    role: nextcord.Role|int,
    guild: nextcord.Guild = None,
    reason: str = None,
):
    """
    Removes a role from a member

    Args:
        memeber (nextcord.Member|int): Member to remove role from
        role (nextcord.Role|int): Role to remove
        guild (nextcord.Guild, optional): Guild to get member and role from.
            Defaults to None, required if memeber or role is an int.
        reason (str, optional): Reason for audit log. Defaults to None. 
    """

    if isinstance(memeber, int) and guild is not None:
        memeber = guild.get_member(memeber)
    if isinstance(role, int) and guild is not None:
        role = guild.get_role(role)
    if memeber is None or role is None:
        return
    if role in memeber.roles:
        try:
            await memeber.remove_roles(role, reason=reason, atomic=True)
        except Exception:
            pass
