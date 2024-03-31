from datetime import datetime, timedelta

import nextcord
from nextcord.ext import commands

from utils.cases import (
    create_case_embed,
    get_case_by_id,
    get_last_warning,
    fetch_cases_by_partial_id,
)
from utils.config import Configuration
from utils.database import db_session, KickCase, WarningCase, RelatedCase
from utils.perms import permcheck, is_mod, is_admin, is_immune, target_eligibility
from utils.dialog import confirm, ButtonPreset
from utils.sersi_embed import SersiEmbed
from utils.sersi_exceptions import CommandDisabledException


class KickSystem(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Used to kick a user",
    )
    async def kick(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member,
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason you are kicking the user",
            min_length=8,
            max_length=1024,
        ),
        related_warning: str = nextcord.SlashOption(
            name="related_warning",
            description="The ID of the warning case related to this timeout",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if not self.config.bot.dev_mode:
            raise CommandDisabledException

        await interaction.response.defer(ephemeral=True)

        if not target_eligibility(interaction.user, offender):
            warning_alert = SersiEmbed(
                title="Unauthorised Moderation Target",
                description=f"{interaction.user.mention} ({interaction.user.id}) attempted to **kick** {offender.mention} ({offender.id}) despite being outranked!",
            )

            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )

            mega_admin_role = interaction.guild.get_role(
                self.config.permission_roles.dark_moderator
            )

            await logging_channel.send(
                content=f"**ALERT:** {mega_admin_role.mention}", embed=warning_alert
            )

            await interaction.followup.send(
                f"{self.config.emotes.fail} {offender.mention} is a higher level than you. This has been reported."
            )
            return

        if is_immune(offender):
            if not await permcheck(interaction, is_admin):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} {offender.mention} is immune."
                )
                return

        await offender.send(
            embed=SersiEmbed(
                title=f"Kicked from {interaction.guild.name}",
                description=f"You have been kicked from {interaction.guild.name}. "
                "As this is not a ban you do not have to appeal this decision and can rejoin at your leisure. "
                "If you believe this was in error please rejoin and open an Administrator ticket.",
                fields={"Reason:": reason},
                footer="Sersi Moderation",
            )
        )

        try:
            await interaction.guild.kick(
                offender, reason=f"[{reason}] -{interaction.user.name}"
            )
            case = KickCase(
                offender=offender.id,
                moderator=interaction.user.id,
                reason=reason,
            )
            with db_session(interaction.user) as session:
                if related_warning is not None:
                    if (
                        not session.query(WarningCase)
                        .filter_by(id=related_warning)
                        .first()
                    ):
                        await interaction.followup.send(
                            f"{self.config.emotes.fail} {related_warning} is not a valid warning case."
                        )
                        return
                elif last_warning := get_last_warning(offender.id):
                    # If the last warning was issued within the last 15 minutes, ask user if the warning is related
                    if last_warning.created > datetime.utcnow() - timedelta(minutes=15):
                        if await confirm(
                            interaction,
                            content=f"Recent warning found for {offender.mention}. Is it related?",
                            embed=create_case_embed(
                                last_warning,
                                interaction=interaction,
                                config=self.config,
                            ),
                            true_button=ButtonPreset.YES_PRIMARY,
                            false_button=ButtonPreset.NO_NEUTRAL,
                            ephemeral=True,
                        ):
                            related_warning = last_warning.id

                session.add(case)
                if related_warning is not None:
                    session.add(
                        RelatedCase(
                            case_id=case.id,
                            related_case_id=related_warning,
                        )
                    )
                session.commit()

            logging_embed = create_case_embed(
                get_case_by_id(self.config, case.id, False), interaction, self.config
            )
            await interaction.guild.get_channel(self.config.channels.logging).send(
                embed=logging_embed
            )
            await interaction.guild.get_channel(self.config.channels.mod_logs).send(
                embed=logging_embed
            )

            confirm_embed = SersiEmbed(
                title="Kick Result:",
                fields={
                    "Member:": f"{offender.mention} ({offender.id})",
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                    "Successful:": self.config.emotes.success,
                    "Case ID:": case.id,
                },
                author=interaction.user,
                thumbnail_url=offender.avatar.url,
            )

        except nextcord.HTTPException:
            confirm_embed = SersiEmbed(
                title="Kick Result:",
                fields={
                    "Member:": f"{offender.mention} ({offender.id})",
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                    "Successful:": self.config.emotes.fail,
                },
                author=interaction.user,
            )

        await interaction.channel.send(embed=confirm_embed)

    @kick.on_autocomplete("related_warning")
    async def search_warnings(
        self,
        interaction: nextcord.Interaction,
        related_warning: str,
        offender: nextcord.Member,
    ):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        warnings: list[str] = fetch_cases_by_partial_id(
            related_warning, type="Warning", offender=offender.id
        )
        await interaction.response.send_autocomplete(warnings)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(KickSystem(bot, kwargs["config"]))
