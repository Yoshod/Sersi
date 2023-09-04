from datetime import datetime
import nextcord

from nextcord.ext import commands
from nextcord.ui import Button, View
from pytz import timezone

from utils.cases.autocomplete import fetch_offences_by_partial_name
from utils.cases.create import create_warn_case
from utils.cases.delete import delete_warn
from utils.cases.embed_factory import create_warn_case_embed
from utils.cases.mend import deactivate_warn
from utils.cases.misc import offence_validity_check, deletion_validity_check
from utils.config import Configuration
from utils.cases.fetch import get_case_by_id
from utils.cases.approval import update_approved, update_objected
from utils.perms import (
    permcheck,
    is_mod,
    is_dark_mod,
    is_immune,
    target_eligibility,
    cb_is_compliance,
)
from utils.sersi_embed import SersiEmbed
from utils.review import create_alert
from utils import logs


class WarningSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    async def cb_approve(self, interaction: nextcord.Interaction):
        new_embed: nextcord.Embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Moderation Action Approved",
            value=interaction.user.mention,
            inline=True,
        )
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        update_approved(new_embed.fields[0].value, self.config)

        # Logging
        logging_embed = SersiEmbed(
            title="Moderation Action Approved",
            description="A Moderator Action has been approved by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
            footer="Sersi Moderation Peer Review",
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=logging_embed)

        await logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    async def cb_objection(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Moderation Action Objected To",
            value=interaction.user.mention,
            inline=True,
        )
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)

        update_objected(new_embed.fields[0].value, self.config)

        # Logging
        logging_embed = SersiEmbed(
            title="Moderation Action Objected To",
            description="A Moderator Action has been objected to by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
            footer="Sersi Moderation Peer Review",
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=logging_embed)

        await logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

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

        sersi_case = get_case_by_id(self.config, uuid, False)

        logging_embed: SersiEmbed = create_warn_case_embed(
            sersi_case, interaction=interaction
        )

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
                },
                footer="Sersi Warning",
            ),
            wait=True,
        )

        reviewer_role, reviewed_role, review_embed, review_channel = create_alert(
            interaction.user, self.config, logging_embed, sersi_case, result.jump_url
        )

        approve = Button(label="Approve", style=nextcord.ButtonStyle.green)
        approve.callback = self.cb_approve

        objection = Button(label="Object", style=nextcord.ButtonStyle.red)
        objection.callback = self.cb_objection

        button_view = View(timeout=None)
        button_view.add_item(approve)
        button_view.add_item(objection)

        if reviewer_role.id == self.config.permission_roles.compliance:
            button_view.interaction_check = cb_is_compliance

        await review_channel.send(
            f"{reviewer_role.mention} a warning by a {reviewed_role.mention} has been taken and should now be reviewed.",
            embed=review_embed,
            view=button_view,
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
