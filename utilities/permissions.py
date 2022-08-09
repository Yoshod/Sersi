from nextcord.ext import commands
from nextcord.ext.commands import Context


def is_a_sersi_contributor():
    def predicate(ctx: Context) -> bool:
        if ctx.cog.config is None:
            raise Exception("Configuration not found within the cog")

        return ctx.guild is not None and ctx.guild.get_role(ctx.cog.config.staff_roles.sersi_contributor) in ctx.author.roles

    return commands.check(predicate)
