import nextcord
from nextcord.ext import commands

from utils.cases import create_case_embed
from utils.config import Configuration
from utils.database import db_session, WarningCase
from utils.objection import AlertView
from utils.offences import fetch_offences_by_partial_name, offence_validity_check
from utils.perms import (
    permcheck,
    is_mod,
    is_dark_mod,
    is_immune,
    target_eligibility,
)
from utils.review import create_alert
from utils.sersi_embed import SersiEmbed


class WarningSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Used to do warn stuff",
    )
    async def warn(self, interaction: nextcord.Interaction):
        pass

    @warn.subcommand(description="Used to warn a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The person you wish to warn.",
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence for which the user is being warned.",
        ),
        detail: str = nextcord.SlashOption(
            name="detail",
            description="Details on the offence,",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer()

        if not target_eligibility(interaction.user, offender):
            warning_alert = SersiEmbed(
                title="Unauthorised Moderation Target",
                description=f"{interaction.user.mention} ({interaction.user.id}) attempted to warn "
                f"{offender.mention} ({offender.id}) despite being outranked!",
            )

            await interaction.guild.get_channel(self.config.channels.logging).send(
                content=f"**ALERT:** {interaction.guild.get_role(self.config.permission_roles.dark_moderator).mention}",
                embed=warning_alert,
            )

            await interaction.send(
                f"{self.config.emotes.fail} {offender.mention} is a higher level than you. This has been reported.",
                ephemeral=True,
            )
            return

        if is_immune(offender):
            await interaction.send(
                f"{self.config.emotes.fail} {offender.mention} is immune.",
                ephemeral=True,
            )
            return

        if not offence_validity_check(offence):
            await interaction.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. "
                "Try again or consider using the 'Other' offence.",
                ephemeral=True,
            )
            return

        case = WarningCase(
            offender=offender.id,
            moderator=interaction.user.id,
            offence=offence,
            details=detail,
        )
        with db_session(interaction.user) as session:
            session.add(case)
            session.commit()

            case = session.query(WarningCase).filter_by(id=case.id).first()

        try:
            await offender.send(
                embed=SersiEmbed(
                    title=f"You have been warned in {interaction.guild.name}!",
                    fields={"Offence:": f"`{offence}`", "Detail:": f"`{detail}`"},
                    footer="Sersi Warning",
                ).set_thumbnail(interaction.guild.icon.url)
            )
            not_sent: bool = False

        except (nextcord.Forbidden, nextcord.HTTPException):
            not_sent: bool = True

        logging_embed: SersiEmbed = create_case_embed(case, interaction, self.config)

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=logging_embed
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=logging_embed
        )

        # anchor: nextcord.Message = await interaction.channel.send("⚓")

        result: nextcord.WebhookMessage = await interaction.followup.send(
            embed=SersiEmbed(
                title="Warn Result:",
                fields={
                    "Offence:": f"`{offence}`",
                    "Detail:": f"`{detail}`",
                    "Member:": f"{offender.mention} ({offender.id})",
                    "DM Sent:": self.config.emotes.fail
                    if not_sent
                    else self.config.emotes.success,
                    "Sent for Review:": self.config.emotes.success,
                },
                footer="Sersi Warning",
            ),
            wait=True,
        )

        reviewer_role, reviewed_role, review_embed, review_channel = create_alert(
            interaction.user, self.config, logging_embed, case, result.jump_url
        )

        await review_channel.send(
            f"{reviewer_role.mention} a warning by a {reviewed_role.mention} has been taken and should now be reviewed.",
            embed=review_embed,
            view=AlertView(self.config, reviewer_role, case),
        )

    @warn.subcommand(description="Deactivate a warn")
    async def deactivate(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="The Case ID of the warn you want to deactivate",
            min_length=11,
            max_length=22,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for deactivating the warning",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        with db_session(interaction.user) as session:
            case: WarningCase = (
                session.query(WarningCase).filter(WarningCase.id == case_id).first()
            )

            if not case:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} {case_id} is not a valid warn case."
                )

            if not case.active:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} {case_id} is already deactivated."
                )
                return

            case.active = False
            case.deactivate_reason = reason
            case.deactivated_by = interaction.user.id
            session.commit()

            case: WarningCase = (
                session.query(WarningCase).filter(WarningCase.id == case_id).first()
            )

        logging_embed = SersiEmbed(
            title="Warn Deactivated",
            fields={
                "Warn ID:": case_id,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                "Reason:": reason,
            },
        )

        try:
            await interaction.guild.get_member(case.offender).send(
                embed=SersiEmbed(
                    title=f"Warn Deactivated in {interaction.guild.name}",
                    description=f"Your warn in {interaction.guild.name} has been deactivated. "
                    "It is still visible to moderators.",
                )
            )
        except nextcord.HTTPException:
            pass

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=logging_embed
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=logging_embed
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} Warn {case_id} has been deactivated!"
        )

    @warn.subcommand(description="Used to delete a deactivated warn")
    async def delete(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=11,
            max_length=22,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason you are deleting the warn",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=False)

        with db_session(interaction.user) as session:
            case: WarningCase = session.query(WarningCase).filter_by(id=case_id).first()

            if not case:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} {case_id} is not a valid warn case."
                )
                return

            if case:
                session.delete(case)
                await interaction.guild.get_channel(self.config.channels.logging).send(
                    embed=SersiEmbed(
                        title="Warning Deleted",
                    )
                    .add_field(name="Warn ID", value=f"`{case_id}`", inline=True)
                    .add_field(
                        name="Administrator",
                        value=f"{interaction.user.mention}",
                        inline=True,
                    )
                    .add_field(name="Reason", value=f"`{reason}`", inline=False)
                    .set_thumbnail(interaction.user.display_avatar.url)
                )

                await interaction.followup.send(
                    f"{self.config.emotes.success} Warning {case_id} successfully deleted."
                )

                session.commit()

            else:
                await interaction.guild.get_channel(self.config.channels.logging).send(
                    embed=SersiEmbed(
                        title="Warning Deletion Attempted",
                    )
                    .add_field(name="Warn ID", value=f"`{case_id}`", inline=True)
                    .add_field(
                        name="Administrator",
                        value=f"{interaction.user.mention}",
                        inline=True,
                    )
                    .add_field(name="Reason", value=f"`{reason}`", inline=False)
                    .set_thumbnail(interaction.user.display_avatar.url)
                )

                await interaction.followup.send(
                    f"{self.config.emotes.fail} Warning {case_id} has not been deleted."
                )

    @add.on_autocomplete("offence")
    async def search_offences(self, interaction: nextcord.Interaction, offence: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        offences: list[str] = fetch_offences_by_partial_name(offence)
        await interaction.response.send_autocomplete(sorted(offences))


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(WarningSystem(bot, kwargs["config"]))
