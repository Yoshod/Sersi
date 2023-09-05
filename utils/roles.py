import nextcord

async def give_role(
    member: nextcord.Member|int,
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
        handle_error (callable, optional): Function to handle errors. Defaults to print.
    """

    if isinstance(member, int) and guild is not None:
        member = guild.get_member(member)
    if isinstance(role, int) and guild is not None:
        role = guild.get_role(role)
    if member is None or role is None:
        print("Error: Invalid member or role")
        return False
    if role not in member.roles:
        try:
            await member.add_roles(role, reason=reason, atomic=True)
        except nextcord.Forbidden:
            print(f"Error: Missing permissions to give role {role.name}")
            return False
        except nextcord.HTTPException:
            await print(f"Error: An error occured while giving role {role.name}")
            return False
    return True

async def remove_role(
    member: nextcord.Member|int,
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
        handle_error (callable, optional): Function to handle errors. Defaults to print.
    """

    if isinstance(member, int) and guild is not None:
        member = guild.get_member(member)
    if isinstance(role, int) and guild is not None:
        role = guild.get_role(role)
    if member is None or role is None:
        print("Error: Invalid member or role")
        return False
    if role in member.roles:
        try:
            await member.remove_roles(role, reason=reason, atomic=True)
        except nextcord.Forbidden:
            print(f"Error: Missing permissions to remove role {role.name}")
            return False
        except nextcord.HTTPException:
            print(f"Error: An error occured while removing role {role.name}")
            return False
    return True
