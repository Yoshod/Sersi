import nextcord

from nextcord.ext import commands
from utils.config import Configuration
from utils.cases.fetch import get_case_by_id
from utils.perms import permcheck, is_mod, is_dark_mod, is_immune, target_eligibility
from utils.cases import (
    offence_validity_check,
    create_warn_case,
    create_warn_case_embed,
    fetch_offences_by_partial_name,
    deactivate_warn,
    deletion_validity_check,
    delete_warn,
)
from utils.base import SersiEmbed


class WarningSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
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
                description=f"{interaction.user.mention} ({interaction.user.id}) attempted to warn {offender.mention} ({offender.id}) despite being outranked!",
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

        if not offence_validity_check(self.config, offence):
            await interaction.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. Try again or consider using the 'Other' offence.",
                ephemeral=True,
            )
            return

        uuid = create_warn_case(
            self.config, offender, interaction.user, offence, detail
        )

        try:
            await offender.send(
                embed=SersiEmbed(
                    title=f"You have been warned in {interaction.guild.name}!",
                    fields={"Offence:": f"`{offence}`", "Detail:": f"`{detail}`"},
                    footer="Sersi Warning",
                ).set_thumbnail(interaction.guild.icon.url)
            )
            not_sent = False

        except (nextcord.Forbidden, nextcord.HTTPException):
            not_sent = True

        logging_embed: SersiEmbed = create_warn_case_embed(
            sersi_case=get_case_by_id(self.config, uuid, False), interaction=interaction
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=logging_embed
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=logging_embed
        )

        await interaction.followup.send(
            embed=SersiEmbed(
                title="Warn Result:",
                fields={
                    "Offence:": f"`{offence}`",
                    "Detail:": f"`{detail}`",
                    "Member:": f"{offender.mention} ({offender.id})",
                    "DM Sent:": self.config.emotes.fail
                    if not_sent
                    else self.config.emotes.success,
                },
            )
        )

    @warn.subcommand(description="Deactivate a warn")
    async def deactivate(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="The Case ID of the warn you want to deactivate",
            min_length=22,
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

        deactivated, offender_id = deactivate_warn(self.config, case_id)

        if deactivated:
            logging_embed = SersiEmbed(
                title="Warn Deactivated",
                fields={
                    "Warn ID:": case_id,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                    "Reason:": reason,
                },
            )

            offender = interaction.guild.get_member(offender_id)
            try:
                await offender.send(
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

        else:
            await interaction.followup.send(
                f"{self.config.emotes.fail} Warn {case_id} could not be deactivated."
            )

    @warn.subcommand(description="Used to delete a deactivated warn")
    async def delete(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=22,
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

        if deletion_validity_check(self.config, case_id):
            if delete_warn(self.config, case_id):

                await interaction.guild.get_channel(self.config.channels.logging).send(
                    embed=SersiEmbed(
                        title="Warning Deleted",
                    )
                    .add_field(name="Warn ID", value=f"`{case_id}`", inline=True)
                    .add_field(
                        name="Mega Administrator",
                        value=f"{interaction.user.mention}",
                        inline=True,
                    )
                    .add_field(name="Reason", value=f"`{reason}`", inline=False)
                    .set_thumbnail(interaction.user.display_avatar.url)
                )

                await interaction.followup.send(
                    f"{self.config.emotes.success} Warning {case_id} successfully deleted."
                )

            else:

                await interaction.guild.get_channel(self.config.channels.logging).send(
                    embed=SersiEmbed(
                        title="Warning Deletion Attempted",
                    )
                    .add_field(name="Warn ID", value=f"`{case_id}`", inline=True)
                    .add_field(
                        name="Mega Administrator",
                        value=f"{interaction.user.mention}",
                        inline=True,
                    )
                    .add_field(name="Reason", value=f"`{reason}`", inline=False)
                    .set_thumbnail(interaction.user.display_avatar.url)
                )

                await interaction.followup.send(
                    f"{self.config.emotes.fail} Warning {case_id} has not been deleted."
                )

        else:
            await interaction.followup.send(
                f"{self.config.emotes.fail} {case_id} is not a valid warn case."
            )

    @add.on_autocomplete("offence")
    async def search_offences(self, interaction: nextcord.Interaction, offence: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        offences: list[str] = fetch_offences_by_partial_name(self.config, offence)
        await interaction.response.send_autocomplete(sorted(offences))


def setup(bot, **kwargs):
    bot.add_cog(WarningSystem(bot, kwargs["config"]))
