import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.database import (
    db_session,
    RaidActivations,
    RaidDeactivations,
    BanCase,
)
from utils.perms import (
    is_full_mod,
    permcheck,
)
from utils.sersi_embed import SersiEmbed


class AntiRaid(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        name="raid",
        description="Toggle raid mode.",
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def raid(self, interaction: nextcord.Interaction):
        pass

    @raid.subcommand(
        name="activate",
        description="Activate raid mode.",
    )
    async def raid_activate(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_full_mod):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            raid_activation = (
                session.query(RaidActivations)
                .order_by(RaidActivations.timestamp.desc())
                .first()
            )
            if raid_activation:
                alert_check = (
                    session.query(RaidDeactivations)
                    .filter_by(activation_id=raid_activation.activation_id)
                    .first()
                )

                if not alert_check:
                    await interaction.followup.send(
                        "Raid mode is already active.",
                        ephemeral=True,
                    )
                    return

            rule = await interaction.guild.create_auto_moderation_rule(
                name="Raid Mode",
                event_type=nextcord.AutoModerationEventType.message_send,
                actions=[
                    nextcord.AutoModerationAction(
                        type=nextcord.AutoModerationActionType.block_message
                    )
                ],
                trigger_type=nextcord.AutoModerationTriggerType.keyword,
                trigger_metadata=nextcord.AutoModerationTriggerMetadata(
                    regex_patterns=[".*"]
                ),
                enabled=True,
                exempt_roles=[interaction.guild.get_role(self.config.roles.staff.mod)],
                reason="Raid Mode",
            )

            raid = RaidActivations(moderator=interaction.user.id, rule_id=rule.id)
            session.add(raid)
            session.commit()

            raid_case = (
                session.query(RaidActivations)
                .filter_by(activation_id=raid.activation_id)
                .first()
            )

        raid_embed = SersiEmbed(
            title="Raid Mode Activated!",
            description=f"Raid mode has been activated!\n\nOnly Moderators are able to send messages during Raid Mode.\n\nThe /raid ban command can now be used to mass ban raiders.\n\nRaid ID: {raid_case.activation_id}\n\n**Moderator:** {interaction.user.mention}",
            color=nextcord.Color.red(),
            thumbnail_url=self.bot.user.avatar.url,
        )

        await interaction.followup.send(
            "Raid mode activated.",
            ephemeral=True,
        )

        await interaction.guild.get_channel(self.config.channels.staff.alert).send(
            f"**RAID MODE ACTIVATED:** {interaction.guild.get_role(self.config.roles.staff.mod).mention}",
            embed=raid_embed,
        )

    @raid.subcommand(
        name="deactivate",
        description="Deactivate raid mode.",
    )
    async def raid_deactivate(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_full_mod):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            raid_activation = (
                session.query(RaidActivations)
                .order_by(RaidActivations.timestamp.desc())
                .first()
            )
            if not raid_activation:
                await interaction.followup.send(
                    "Raid mode is not active.",
                    ephemeral=True,
                )
                return

            rule = await interaction.guild.fetch_auto_moderation_rule(
                raid_activation.rule_id
            )
            await rule.delete()

            raid_deactivation = RaidDeactivations(
                activation_id=raid_activation.activation_id,
                moderator=interaction.user.id,
            )
            session.add(raid_deactivation)
            session.commit()

            raid_case = (
                session.query(RaidDeactivations)
                .filter_by(activation_id=raid_deactivation.activation_id)
                .first()
            )

            raid_bans = (
                session.query(BanCase)
                .filter_by(details=f"{raid_case.activation_id} Raid")
                .all()
            )

        raid_embed = SersiEmbed(
            title="Raid Mode Deactivated",
            description=f"Raid mode has been deactivated by {interaction.user.mention}.\nRaid ID: {raid_case.activation_id}\n\n**Bans:** {len(raid_bans)}",
            color=nextcord.Color.green(),
            thumbnail_url=self.bot.user.avatar.url,
        )

        await interaction.followup.send(
            "Raid mode deactivated.",
            ephemeral=True,
        )

        await interaction.guild.get_channel(self.config.channels.staff.alert).send(
            f"{interaction.guild.get_role(self.config.roles.staff.mod).mention}",
            embed=raid_embed,
        )

    @raid.subcommand(
        name="ban",
        description="Ban raiders.",
    )
    async def raid_ban(
        self,
        interaction: nextcord.Interaction,
        raider_1: nextcord.User = nextcord.SlashOption(
            description="Raider 1",
            required=True,
        ),
        raider_2: nextcord.User = nextcord.SlashOption(
            description="Raider 2",
            required=False,
        ),
        raider_3: nextcord.User = nextcord.SlashOption(
            description="Raider 3",
            required=False,
        ),
        raider_4: nextcord.User = nextcord.SlashOption(
            description="Raider 4",
            required=False,
        ),
        raider_5: nextcord.User = nextcord.SlashOption(
            description="Raider 5",
            required=False,
        ),
        raider_6: nextcord.User = nextcord.SlashOption(
            description="Raider 6",
            required=False,
        ),
        raider_7: nextcord.User = nextcord.SlashOption(
            description="Raider 7",
            required=False,
        ),
        raider_8: nextcord.User = nextcord.SlashOption(
            description="Raider 8",
            required=False,
        ),
        raider_9: nextcord.User = nextcord.SlashOption(
            description="Raider 9",
            required=False,
        ),
        raider_10: nextcord.User = nextcord.SlashOption(
            description="Raider 10",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_full_mod):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            raid_activation = (
                session.query(RaidActivations)
                .order_by(RaidActivations.timestamp.desc())
                .first()
            )
            if not raid_activation:
                await interaction.followup.send(
                    "Raid mode is not active.",
                    ephemeral=True,
                )
                return

            raid_deactivation = (
                session.query(RaidDeactivations)
                .filter_by(activation_id=raid_activation.activation_id)
                .first()
            )
            if raid_deactivation:
                await interaction.followup.send(
                    "Raid mode is not active.",
                    ephemeral=True,
                )
                return

            raid_case = (
                session.query(RaidActivations)
                .filter_by(activation_id=raid_activation.activation_id)
                .first()
            )

        raiders = []
        banned_raiders = []
        not_banned_raiders = []
        for i in range(1, 10):
            raider: nextcord.User | None = eval(f"raider_{i}")
            if raider is None:
                break

            raiders.append(raider.id)

            with db_session() as session:
                sersi_case = BanCase(
                    offender=raider.id,
                    moderator=interaction.user.id,
                    offence="Other",
                    details=f"{raid_case.activation_id} Raid",
                    ban_type="emergency",
                    active=True,
                )
                session.add(sersi_case)
                session.commit()

            try:
                await interaction.guild.ban(
                    raider,
                    reason=f"{raid_case.activation_id} Raid",
                    delete_message_days=1,
                )

                banned_raiders.append(raider.id)
            except nextcord.DiscordException:
                not_banned_raiders.append(raider.id)

        banned_string = f"**Bans Requested by {interaction.user.mention}:**\n"
        for raider in raiders:
            if raider in banned_raiders:
                banned_string += (
                    f"{self.config.emotes.success} <@{raider}> ({raider})\n"
                )

            elif raider in not_banned_raiders:
                banned_string += f"{self.config.emotes.fail} <@{raider}> ({raider})\n"

            else:
                banned_string += f"<@{raider}> ({raider})\n"

        raid_embed = SersiEmbed(
            title="Raid Ban Processed",
            description=banned_string,
            color=nextcord.Color.red(),
            thumbnail_url=self.bot.user.avatar.url,
        )

        await interaction.followup.send(
            "Raid ban processed.",
            embed=raid_embed,
            ephemeral=True,
        )

        await interaction.guild.get_channel(self.config.channels.staff.alert).send(
            "**RAID BAN:**",
            embed=raid_embed,
        )

        await interaction.guild.get_channel(self.config.channels.log.general).send(
            "**RAID BAN:**",
            embed=raid_embed,
        )

        await interaction.guild.get_channel(self.config.channels.log.mod).send(
            "**RAID BAN:**",
            embed=raid_embed,
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(AntiRaid(bot, kwargs["config"]))
