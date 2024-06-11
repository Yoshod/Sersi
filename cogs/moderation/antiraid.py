import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.database import (
    db_session,
    RaidActivations,
    RaidDeactivations,
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
                exempt_roles=[
                    interaction.guild.get_role(self.config.permission_roles.moderator)
                ],
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

        await interaction.guild.get_channel(self.config.channels.alert).send(
            f"**RAID MODE ACTIVATED:** {interaction.guild.get_role(self.config.permission_roles.moderator).mention}",
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

        raid_embed = SersiEmbed(
            title="Raid Mode Deactivated",
            description=f"Raid mode has been deactivated by {interaction.user.mention}.\nRaid ID: {raid_case.activation_id}",
            color=nextcord.Color.green(),
            thumbnail_url=self.bot.user.avatar.url,
        )

        await interaction.followup.send(
            "Raid mode deactivated.",
            ephemeral=True,
        )

        await interaction.guild.get_channel(self.config.channels.alert).send(
            f"{interaction.guild.get_role(self.config.permission_roles.moderator).mention}",
            embed=raid_embed,
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(AntiRaid(bot, kwargs["config"]))
