import nextcord
from nextcord.ext import commands

from utils.configutils import Configuration


class AuditLogs(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False, guild_ids=[977377117895536640, 856262303795380224]
    )
    async def get_audit_logs(self, interaction: nextcord.Interaction):
        message: str = ""
        async for entry in interaction.guild.audit_logs(limit=10):
            message += f"{entry.user} did {entry.action.name} to {entry.target}\n"
        await interaction.send(message)


def setup(bot, **kwargs):
    bot.add_cog(AuditLogs(bot, kwargs["config"]))
