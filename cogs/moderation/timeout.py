import datetime

import nextcord

from nextcord.ext import commands
from pytz import timezone
from utils import logs
from utils.cases.approval import update_approved, update_objected
from nextcord.ui import Button, View

from utils.cases.autocomplete import fetch_offences_by_partial_name
from utils.cases.embed_factory import create_timeout_case_embed
from utils.cases.fetch import get_case_by_id
from utils.cases.misc import offence_validity_check
from utils.config import Configuration
from utils.database import db_session, TimeoutCase
from utils.perms import (
    cb_is_compliance,
    permcheck,
    is_mod,
    is_dark_mod,
    is_immune,
    target_eligibility,
)
from utils.review import create_alert
from utils.sersi_embed import SersiEmbed


def convert(timespan: str, duration: int) -> datetime.timedelta | None:
    match timespan:
        case "m":
            return datetime.timedelta(minutes=duration)

        case "h":
            if not duration > 672:
                return datetime.timedelta(hours=duration)

        case "d":
            if not duration > 28:
                return datetime.timedelta(days=duration)

        case "w":
            if not duration > 4:
                return datetime.timedelta(weeks=duration)

    return None


class TimeoutSystem(commands.Cog):
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
        description="Used to do timeout stuff",
    )
    async def timeout(self, interaction: nextcord.Interaction):
        pass

    @timeout.subcommand(description="Used to timeout a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The person you wish to timeout.",
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence for which the user is being timed out.",
        ),
        detail: str = nextcord.SlashOption(
            name="detail",
            description="Details on the offence,",
            min_length=8,
            max_length=1024,
        ),
        duration: int = nextcord.SlashOption(
            name="duration",
            description="The length of time the user should be timed out for",
            min_value=1,
            max_value=40320,
        ),
        timespan: str = nextcord.SlashOption(
            name="timespan",
            description="The unit of time being used",
            choices={
                "Minutes": "m",
                "Hours": "h",
                "Days": "d",
                "Weeks": "w",
            },
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        planned_end: datetime.timedelta = convert(timespan, duration)

        if not planned_end:
            interaction.followup.send(
                f"{self.config.emotes.fail} You have input an invalid timeout duration. "
                "A timeout cannot last any longer than 28 days."
            )
            return

        if not target_eligibility(interaction.user, offender):
            warning_alert = SersiEmbed(
                title="Unauthorised Moderation Target",
                description=f"{interaction.user.mention} ({interaction.user.id}) attempted to warn {offender.mention} "
                f"({offender.id}) despite being outranked!",
            )

            await interaction.guild.get_channel(self.config.channels.logging).send(
                content=f"**ALERT:** {interaction.guild.get_role(self.config.permission_roles.dark_moderator).mention}",
                embed=warning_alert,
            )

            await interaction.followup.send(
                f"{self.config.emotes.fail} {offender.mention} is a higher level than you. This has been reported."
            )
            return

        if is_immune(offender):
            if not await permcheck(interaction, is_dark_mod):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} {offender.mention} is immune."
                )
                return

        if not offence_validity_check(offence):
            await interaction.followup.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. Try again or consider using the "
                f"'Other' offence."
            )
            return

        case = TimeoutCase(
            offender=offender.id,
            moderator=interaction.user.id,
            offence=offence,
            details=detail,
            duration=duration,
            planned_end=datetime.datetime.now(timezone.utc) + planned_end,
        )

        with db_session(interaction.user) as session:
            session.add(case)
            session.commit()

        try:
            await offender.send(
                embed=SersiEmbed(
                    title=f"You have been timed out in {interaction.guild.name}!",
                    description=f"You have been timed out in {interaction.guild.name}. The details about the timeout are "
                    "below. If you would like to appeal your timeout you can do so:\n"
                    "https://appeals.wickbot.com",
                    fields={
                        "Offence:": f"`{offence}`",
                        "Detail:": f"`{detail}`",
                        "Duration:": f"`{duration}{timespan}`",
                    },
                    footer="Sersi Timeout",
                ).set_thumbnail(interaction.guild.icon.url)
            )
            not_sent = False

        except (nextcord.Forbidden, nextcord.HTTPException):
            not_sent = True

        sersi_case = get_case_by_id(self.config, case.id, False)

        logging_embed: SersiEmbed = create_timeout_case_embed(
            sersi_case.__dict__,
            interaction=interaction,
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=logging_embed
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=logging_embed
        )

        await offender.timeout(
            planned_end, reason=f"[{offence}: {detail}] - {interaction.user}"
        )


        result: nextcord.WebhookMessage = await interaction.followup.send(
            embed=SersiEmbed(
                title="Timeout Result:",
                fields={
                    "Offence:": f"`{offence}`",
                    "Detail:": f"`{detail}`",
                    "Duration:": f"`{duration}{timespan}`",
                    "Member:": f"{offender.mention} ({offender.id})",
                    "DM Sent:": self.config.emotes.fail
                    if not_sent
                    else self.config.emotes.success,
                },
                footer="Sersi Timeout",
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

    @timeout.subcommand(description="Used to remove a user's timeout")
    async def remove(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The person you wish to end the timeout for.",
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason for ending the timeout",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        ...
        ...
        ...

        await offender.edit(timeout=None, reason=f"[{reason}] - {interaction.user}")

    @add.on_autocomplete("offence")
    async def search_offences(self, interaction: nextcord.Interaction, offence: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        offences: list[str] = fetch_offences_by_partial_name(offence)
        await interaction.response.send_autocomplete(sorted(offences))


def setup(bot, **kwargs):
    bot.add_cog(TimeoutSystem(bot, kwargs["config"]))
