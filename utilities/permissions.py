from nextcord.ext import commands
from nextcord.ext.commands import Context


def is_a_sersi_contributor():
    def predicate(context: Context) -> bool:
        if context.cog.config is None:
            raise Exception("Configuration not found within the cog")

        return context.guild is not None and context.guild.get_role(context.cog.config.staff_roles.sersi_contributor) in context.author.roles

    return commands.check(predicate)
