import nextcord

from nextcord.ext import commands
from utils.config import Configuration
from utils.perms import permcheck, is_mod, is_dark_mod, is_immune, target_eligibility
from utils.cases import (
    offence_validity_check,
    create_warn_case,
    create_warn_case_embed,
    get_case_by_id,
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

        await interaction.response.defer(ephemeral=False)

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

            await interaction.followup.send(
                f"{self.config.emotes.fail} {offender.mention} is a higher level than you. This has been reported."
            )
            return

        if is_immune(offender):
            await interaction.followup.send(
                f"{self.config.emotes.fail} {offender.mention} is immune."
            )
            return

        if not offence_validity_check(self.config, offence):
            await interaction.followup.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. Try again or consider using the 'Other' offence."
            )
            return

        uuid = create_warn_case(
            self.config, offender, interaction.user, offence, detail
        )

        warn_embed = SersiEmbed(
            title=f"You have been warned in {interaction.guild.name}!",
            fields={"Offence:": f"`{offence}`", "Detail:": f"`{detail}`"},
            footer="Sersi Warning",
        )

        warn_embed.set_thumbnail(interaction.guild.icon.url)

        try:
            await offender.send(embed=warn_embed)
            not_sent = False

        except nextcord.Forbidden:
            not_sent = True

        except nextcord.HTTPException:
            not_sent = True

        warn_case = get_case_by_id(self.config, uuid, False)

        logging_embed = create_warn_case_embed(warn_case, interaction)

        modlog_channel = interaction.guild.get_channel(self.config.channels.mod_logs)
        sersi_logs = interaction.guild.get_channel(self.config.channels.logging)

        await modlog_channel.send(embed=logging_embed)
        await sersi_logs.send(embed=logging_embed)

        confirm_embed = SersiEmbed(
            title="Warn Result:",
            fields={
                "Offence:": f"`{offence}`",
                "Detail:": f"`{detail}`",
                "Member:": f"{offender.mention} ({offender.id})",
            },
        )

        if not_sent:
            confirm_embed.add_field(
                name="DM Sent:", value=self.config.emotes.fail, inline=True
            )
            await interaction.followup.send(embed=confirm_embed)

        else:
            confirm_embed.add_field(
                name="DM Sent:", value=self.config.emotes.success, inline=True
            )
            await interaction.followup.send(embed=confirm_embed)

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
                alert_embed = SersiEmbed(
                    title=f"Warn Deactivated in {interaction.guild.name}",
                    description=f"Your warn in {interaction.guild.name} has been deactivated. It is still visible to moderators.",
                )
                await offender.send(embed=alert_embed)
            except nextcord.HTTPException:
                pass

            modlog_channel = interaction.guild.get_channel(
                self.config.channels.mod_logs
            )
            sersi_logs = interaction.guild.get_channel(self.config.channels.logging)

            await modlog_channel.send(embed=logging_embed)
            await sersi_logs.send(embed=logging_embed)

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

        valid_warn = deletion_validity_check(self.config, case_id)

        if valid_warn:
            deleted = delete_warn(self.config, case_id)

            if deleted:
                logging_embed = SersiEmbed(
                    title="Warning Deleted",
                )

                logging_embed.add_field(
                    name="Warn ID", value=f"`{case_id}`", inline=True
                )
                logging_embed.add_field(
                    name="Mega Administrator",
                    value=f"{interaction.user.mention}",
                    inline=True,
                )
                logging_embed.add_field(
                    name="Reason", value=f"`{reason}`", inline=False
                )

                logging_embed.set_thumbnail(interaction.user.display_avatar.url)

                logging_channel = interaction.guild.get_channel(
                    self.config.channels.logging
                )

                await logging_channel.send(embed=logging_embed)

                await interaction.followup.send(
                    f"{self.config.emotes.success} Warning {case_id} successfully deleted."
                )
            else:
                logging_embed = SersiEmbed(
                    title="Warning Deletion Attempted",
                )

                logging_embed.add_field(
                    name="Warn ID", value=f"`{case_id}`", inline=True
                )
                logging_embed.add_field(
                    name="Mega Administrator",
                    value=f"{interaction.user.mention}",
                    inline=True,
                )
                logging_embed.add_field(
                    name="Reason", value=f"`{reason}`", inline=False
                )

                logging_embed.set_thumbnail(interaction.user.display_avatar.url)

                logging_channel = interaction.guild.get_channel(
                    self.config.channels.logging
                )

                await logging_channel.send(embed=logging_embed)

                await interaction.followup.send(
                    f"{self.config.emotes.fail} Warning {case_id} has not been deleted."
                )

        else:
            await interaction.followup.send(
                f"{self.config.emotes.fail} {case_id} is not a valid warn case."
            )

    @add.on_autocomplete("offence")
    async def search_offences(self, interaction: nextcord.Interaction, offence):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        offences = fetch_offences_by_partial_name(self.config, offence)
        await interaction.response.send_autocomplete(offences)


def setup(bot, **kwargs):
    bot.add_cog(WarningSystem(bot, kwargs["config"]))
