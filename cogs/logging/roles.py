import nextcord
from nextcord.ext import commands
from configutils import Configuration
from baseutils import SersiEmbed


class MemberRoles(commands.Cog):

    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        channel: nextcord.TextChannel = before.guild.get_channel(self.config.channels.role_logs)
        async for entry in after.guild.audit_logs(action=nextcord.AuditLogAction.member_role_update, limit=1):
            log: nextcord.AuditLogEntry = entry

        if log.user.bot:  # role was assigned or removed by a bot
            return

        elif log.before.roles:  # audit log shows roles as prviously had, so this is a role removal entry
            logging = SersiEmbed(
                description="A role has been removed",
                footer="Sersi Role Logging",
                fields={
                    "User affected:": before.mention
                }
            )
            logging.set_author(name=log.user, icon_url=log.user.display_avatar.url)
            for role in log.before.roles:
                logging.add_field(name="Role removed:", value=role.mention, inline=False)
                logging.add_field(name="IDs:", value=f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```", inline=False)

            await channel.send(embed=logging)

        elif log.after.roles:  # audit log shows roles as now have, so this is an added role entry
            logging = SersiEmbed(
                description="A role has been added",
                footer="Sersi Role Logging",
                fields={
                    "User affected:": before.mention
                }
            )
            logging.set_author(name=log.user, icon_url=log.user.display_avatar.url)
            for role in log.after.roles:
                logging.add_field(name="Role added:", value=role.mention, inline=False)
                logging.add_field(name="IDs:", value=f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```", inline=False)

            await channel.send(embed=logging)

        else:
            # the fuck?!
            raise Exception('Audit log entry is in illegal state')


def setup(bot, **kwargs):
    bot.add_cog(MemberRoles(bot, kwargs["config"]))
