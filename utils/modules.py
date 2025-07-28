from utils.database import guild_db_manager, Modules


def check_module_enabled(guild_id: int, module_name: str) -> bool:
    """
    Check if a specific module is enabled for a given guild.

    :param guild_id: The ID of the guild to check.
    :param module_name: The name of the module to check.
    :return: True if the module is enabled, False otherwise.
    """
    with guild_db_manager.get_session(guild_id) as session:
        module = session.query(Modules).filter_by(module_name=module_name).first()
        return module is not None and module.enabled
