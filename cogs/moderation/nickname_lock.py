import nextcord
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class NicknameLock(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        log: nextcord.AuditLogEntry = (
            await after.guild.audit_logs(
                limit=1, action=nextcord.AuditLogAction.member_update
            ).flatten()
        )[0]

        if log.user.bot or before.nick == after.nick:
            return

        if (
            after.guild.get_role(self.config.punishment_roles["role_lock"])
            in after.roles
        ):
            await after.edit(nick=before.nick, reason="Nickname Lock")

            # logging
            await after.guild.get_channel(self.config.channels.logging).send(
                embed=SersiEmbed(
                    title="Nickname Change prevented",
                    footer="Sersi Nickname Lock",
                    fields={
                        "User": f"{after.mention} ({after.id})",
                        "Attempted Nickname": after.nick,
                        "Nickname kept at": before.nick,
                    },
                )
            )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(NicknameLock(bot, kwargs["config"]))
