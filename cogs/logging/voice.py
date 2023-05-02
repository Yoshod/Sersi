import nextcord
from nextcord.ext import commands

from utils.baseutils import SersiEmbed
from utils.configutils import Configuration


class VoiceLogs(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ):
        if before.deaf != after.deaf:
            entries = await member.guild.audit_logs(
                action=nextcord.AuditLogAction.member_update, limit=1
            ).flatten()
            log: nextcord.AuditLogEntry = entries[0]

            if after.deaf:
                await member.guild.get_channel(self.config.channels.voice_logs).send(
                    embed=SersiEmbed(
                        description=f"{log.target.mention} ({log.target.id}) was server deafened",
                        fields={"Voice Channel": after.channel.mention},
                        footer="Sersi Voice Logging",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )
            elif before.deaf:
                await member.guild.get_channel(self.config.channels.voice_logs).send(
                    embed=SersiEmbed(
                        description=f"{log.target.mention} ({log.target.id}) was server un-deafened",
                        fields={"Voice Channel": after.channel.mention},
                        footer="Sersi Voice Logging",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )

        elif before.mute != after.mute:
            entries = await member.guild.audit_logs(
                action=nextcord.AuditLogAction.member_update, limit=1
            ).flatten()
            log: nextcord.AuditLogEntry = entries[0]
            if after.mute:
                await member.guild.get_channel(self.config.channels.voice_logs).send(
                    embed=SersiEmbed(
                        description=f"{log.target.mention} ({log.target.id}) was server muted",
                        fields={"Voice Channel": after.channel.mention},
                        footer="Sersi Voice Logging",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )
            elif before.mute:
                await member.guild.get_channel(self.config.channels.voice_logs).send(
                    embed=SersiEmbed(
                        description=f"{log.target.mention} ({log.target.id}) was server un-muted",
                        fields={"Voice Channel": after.channel.mention},
                        footer="Sersi Voice Logging",
                    ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
                )

        if after.channel != before.channel:
            if after.channel is not None and before.channel is not None:
                entries = await member.guild.audit_logs(
                    action=nextcord.AuditLogAction.member_move, limit=1
                ).flatten()
                log: nextcord.AuditLogEntry = entries[0]
                if log.target == member:
                    await member.guild.get_channel(
                        self.config.channels.voice_logs
                    ).send(
                        embed=SersiEmbed(
                            description=f"{log.target.mention} ({log.target.id}) was forcefully moved",
                            fields={
                                "Previous Voice Channel": before.channel.mention,
                                "Current Voice Channel": after.channel.mention,
                            },
                            footer="Sersi Voice Logging",
                        ).set_author(
                            name=log.user, icon_url=log.user.display_avatar.url
                        )
                    )
                else:
                    await member.guild.get_channel(
                        self.config.channels.voice_logs
                    ).send(
                        embed=SersiEmbed(
                            description=f"{member.mention} ({member.id}) moved Voice Channels",
                            fields={
                                "Previous Voice Channel": before.channel.mention,
                                "Current Voice Channel": after.channel.mention,
                            },
                            footer="Sersi Voice Logging",
                        ).set_author(name=member, icon_url=member.display_avatar.url)
                    )

            elif not after.channel:
                entries = await member.guild.audit_logs(
                    action=nextcord.AuditLogAction.member_disconnect, limit=1
                ).flatten()
                log: nextcord.AuditLogEntry = entries[0]
                if log.target == member:
                    await member.guild.get_channel(
                        self.config.channels.voice_logs
                    ).send(
                        embed=SersiEmbed(
                            description=f"{member.mention} ({member.id}) was forcefully disconnected",
                            fields={
                                "From Voice Channel": f"{before.channel.mention} ({before.channel.id})"
                            },
                            footer="Sersi Voice Logging",
                        ).set_author(
                            name=log.user, icon_url=log.user.display_avatar.url
                        )
                    )
                else:
                    await member.guild.get_channel(
                        self.config.channels.voice_logs
                    ).send(
                        embed=SersiEmbed(
                            description=f"{member.mention} ({member.id}) disconnected from a voice channel",
                            fields={
                                "From Voice Channel": f"{before.channel.mention} ({before.channel.id})"
                            },
                            footer="Sersi Voice Logging",
                        )
                    )
            elif not before.channel:
                await member.guild.get_channel(self.config.channels.voice_logs).send(
                    embed=SersiEmbed(
                        description=f"{member.mention} joined a voice channel",
                        fields={"Voice Channel": after.channel.mention},
                        footer="Sersi Voice Logging",
                    )
                )


def setup(bot, **kwargs):
    bot.add_cog(VoiceLogs(bot, kwargs["config"]))
