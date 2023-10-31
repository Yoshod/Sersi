import datetime
from nextcord.ext import commands
import nextcord

from utils.base import PageView, convert_to_timedelta
from utils.cases import (
    fetch_cases_by_partial_id,
    create_case_embed,
    fetch_all_cases,
    get_case_by_id,
    get_case_audit_logs,
    validate_case_edit,
)
from utils.config import Configuration
from utils.database import (
    BanCase,
    TimeoutCase,
    WarningCase,
    db_session,
    Case,
    ScrubbedCase,
    Offence,
)
from utils.offences import fetch_offences_by_partial_name
from utils.perms import permcheck, is_mod, is_senior_mod, is_dark_mod
from utils.sersi_embed import SersiEmbed


class Cases(commands.Cog):
    punishment_choices = {
        "Informal Warning": "Informal Warning",
        "Warning": "Warning",
        "Reformation": "Reformation Centre",
        "Temporary Ban": "Temporary Ban",
        "Priority Ban": "Priority Ban",
        "Emergency Ban": "Emergency Ban",
        "Emergency Ban & Trust and Safety": "Emergency Ban & TnS Report",
    }

    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
        description="Used to get a case",
    )
    async def cases(self, interaction: nextcord.Interaction):
        pass

    @cases.subcommand(description="Used to display all cases")
    async def list(
        self,
        interaction: nextcord.Interaction,
        page: int = nextcord.SlashOption(
            name="page",
            description="The page you want to view",
            min_value=1,
            default=1,
            required=False,
        ),
        case_type: str = nextcord.SlashOption(
            name="case_type",
            description="The specific case type you are looking for",
            required=False,
            choices=[
                "Ban",
                "Bad Faith Ping",
                "Kick",
                "Probation",
                "Reformation",
                "Slur Usage",
                "Timeout",
                "Warn",
            ],
        ),
        moderator: nextcord.Member = nextcord.SlashOption(
            name="moderator",
            description="The moderator whos cases you are looking for",
            required=False,
        ),
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The offender whos cases you are looking for",
            required=False,
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence you are looking for",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if case_type == "scrubbed_cases" and not await permcheck(
            interaction, is_senior_mod
        ):
            return

        await interaction.response.defer(ephemeral=False)

        cases_embed = SersiEmbed(title=f"{interaction.guild.name} Cases")
        if not interaction.user.is_on_mobile():
            cases_embed.set_thumbnail(interaction.guild.icon.url)

        view = PageView(
            config=self.config,
            base_embed=cases_embed,
            fetch_function=fetch_all_cases,
            author=interaction.user,
            entry_form="{entry}",
            field_title="{entries[0].list_entry_header}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            case_type=case_type,
            moderator_id=moderator.id if moderator else None,
            offender_id=offender.id if offender else None,
            offence=offence,
        )

        await view.send_followup(interaction)

    @cases.subcommand(description="Used to get a case by its ID")
    async def detail(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=11,
            max_length=22,
        ),
        scrubbed: bool = nextcord.SlashOption(
            name="scrubbed",
            description="Specify if you're looking for a scrubbed case",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        sersi_case = get_case_by_id(case_id)

        if not sersi_case:
            await interaction.followup.send(
                f"{self.config.emotes.fail} `{case_id}` does not exist!"
            )

        else:
            await interaction.followup.send(
                embed=create_case_embed(sersi_case, interaction, self.config)
            )

    @cases.subcommand(description="Get audit logs for a case")
    async def audit(
        self,
        interaction: nextcord.Interaction,
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=11,
            max_length=22,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        with db_session() as session:
            if not session.query(Case).filter(Case.id == case_id).first():
                await interaction.followup.send(
                    f"{self.config.emotes.fail} Case {case_id} does not exist."
                )
                return

        audit_embed = SersiEmbed(title=f"Case `{case_id}` Audit Logs")
        audit_embed.set_thumbnail(interaction.guild.icon.url)

        view = PageView(
            config=self.config,
            base_embed=audit_embed,
            fetch_function=get_case_audit_logs,
            author=interaction.user,
            entry_form="{entry.old_value} => {entry.new_value}",
            field_title="{entries[0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=1,
            case_id=case_id,
        )

        await view.send_followup(interaction)

    @cases.subcommand(description="Used to scrub a Sersi Case")
    async def scrub(
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
            description="The reason you are scrubbing the case",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return

        await interaction.response.defer(ephemeral=False)

        with db_session(interaction.user) as session:
            case: Case = session.query(Case).filter(Case.id == case_id).first()

            if not case:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} Case {case_id} does not exist."
                )
                return

            if case.scrubbed:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} Case {case_id} has already been scrubbed."
                )
                return

            case.scrubbed = True
            session.add(
                ScrubbedCase(
                    case_id=case_id, scrubber=interaction.user.id, reason=reason
                )
            )
            session.commit()

        logging_embed = SersiEmbed(
            title="Case Scrubbed",
        )

        logging_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
        logging_embed.add_field(
            name="Senior Moderator",
            value=f"{interaction.user.mention}",
            inline=True,
        )
        logging_embed.add_field(name="Reason", value=f"`{reason}`", inline=False)

        logging_embed.set_thumbnail(interaction.user.display_avatar.url)

        logging_channel = interaction.guild.get_channel(self.config.channels.logging)

        await logging_channel.send(embed=logging_embed)

        await interaction.followup.send(
            f"{self.config.emotes.success} Case {case_id} successfully scrubbed."
        )

    @cases.subcommand(description="Used to delete a scrubbed Sersi Case")
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
            description="The reason you are deleting the case",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_dark_mod):
            return

        await interaction.response.defer(ephemeral=False)

        with db_session() as session:
            case: Case = session.query(Case).filter(Case.id == case_id).first()

            session.delete(case)
            session.commit()

        if case:
            logging_embed = SersiEmbed(
                title="Case Deleted",
            )

            logging_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
            logging_embed.add_field(
                name="Mega Administrator",
                value=f"{interaction.user.mention}",
                inline=True,
            )
            logging_embed.add_field(name="Reason", value=f"`{reason}`", inline=False)

            logging_embed.set_thumbnail(interaction.user.display_avatar.url)

            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )

            await logging_channel.send(embed=logging_embed)

            await interaction.followup.send(
                f"{self.config.emotes.success} Case {case_id} successfully deleted."
            )

        else:
            logging_embed = SersiEmbed(
                title="Case Deletion Attempted",
            )

            logging_embed.add_field(name="Case ID", value=f"`{case_id}`", inline=True)
            logging_embed.add_field(
                name="Mega Administrator",
                value=f"{interaction.user.mention}",
                inline=True,
            )
            logging_embed.add_field(name="Reason", value=f"`{reason}`", inline=False)

            logging_embed.set_thumbnail(interaction.user.display_avatar.url)

            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )

            await logging_channel.send(embed=logging_embed)

            await interaction.followup.send(
                f"{self.config.emotes.fail} Case {case_id} has not been deleted."
            )

    @cases.subcommand(description="Used to edit a Sersi Case")
    async def edit(
        self,
        interaction: nextcord.Interaction,
        case_type: str = nextcord.SlashOption(
            name="case_type",
            description="The type of case you are editing",
            choices={
                "Warning": "Warning",
                "Timeout": "Timeout",
                "Ban": "Ban",
            },
        ),
        case_id: str = nextcord.SlashOption(
            name="case_id",
            description="Case ID",
            min_length=11,
            max_length=22,
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence for which the user is being warned.",
            required=False,
        ),
        detail: str = nextcord.SlashOption(
            name="detail",
            description="Details on the offence,",
            min_length=8,
            max_length=1024,
            required=False,
        ),
        duration: int = nextcord.SlashOption(
            name="duration",
            description="The length of time the user should be timed out for",
            min_value=1,
            max_value=40320,
            required=False,
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
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        valid_output, error_message = validate_case_edit(
            interaction,
            self.config,
            case_type,
            case_id,
            offence,
            detail,
            duration,
            timespan,
        )

        if not valid_output:
            await interaction.followup.send(error_message)
            return

        sersi_case = get_case_by_id(case_id)

        match sersi_case:
            case WarningCase():
                with db_session(interaction.user) as session:
                    sersi_case = (
                        session.query(WarningCase).filter_by(id=sersi_case.id).first()
                    )
                    if offence != sersi_case.offence and offence is not None:
                        sersi_case.offence = offence
                        offence_changed = True

                    else:
                        offence_changed = False

                    if detail != sersi_case.details and detail is not None:
                        sersi_case.details = detail
                        detail_changed = True

                    else:
                        detail_changed = False

                    if not detail_changed and not offence_changed:
                        await interaction.followup.send(
                            f"{self.config.emotes.fail} You have not changed any details about the case!"
                        )
                        return

                    session.commit()
                    sersi_case = (
                        session.query(WarningCase).filter_by(id=sersi_case.id).first()
                    )

                    case_embed = create_case_embed(sersi_case, interaction, self.config)

                    await interaction.followup.send(
                        f"{self.config.emotes.success} Case Updated", embed=case_embed
                    )

                    offender = interaction.guild.get_member(sersi_case.offender)

                    try:
                        await offender.send(
                            embed=SersiEmbed(
                                title=f"Warning Updated in {interaction.guild.name}!",
                                description="A change has been made to your warning. Please see below for the new case information.",
                                fields={
                                    "Offence:": f"`{sersi_case.offence}`",
                                    "Detail:": f"`{sersi_case.details}`",
                                },
                                footer="Sersi Warning",
                            ).set_thumbnail(interaction.guild.icon.url)
                        )

                    except (nextcord.Forbidden, nextcord.HTTPException):
                        pass

                    return

            case BanCase():
                with db_session(interaction.user) as session:
                    sersi_case = (
                        session.query(BanCase).filter_by(id=sersi_case.id).first()
                    )
                    if offence != sersi_case.offence and offence is not None:
                        sersi_case.offence = offence
                        offence_changed = True

                    else:
                        offence_changed = False

                    if detail != sersi_case.details and detail is not None:
                        sersi_case.details = detail
                        detail_changed = True

                    else:
                        detail_changed = False

                    if not detail_changed and not offence_changed:
                        await interaction.followup.send(
                            f"{self.config.emotes.fail} You have not changed any details about the case!"
                        )
                        return

                    session.commit()
                    sersi_case = (
                        session.query(BanCase).filter_by(id=sersi_case.id).first()
                    )

                    case_embed = create_case_embed(sersi_case, interaction, self.config)

                    await interaction.followup.send(
                        f"{self.config.emotes.success} Case Updated", embed=case_embed
                    )

                    return

            case TimeoutCase():
                with db_session(interaction.user) as session:
                    sersi_case = (
                        session.query(TimeoutCase).filter_by(id=sersi_case.id).first()
                    )
                    if offence != sersi_case.offence and offence is not None:
                        sersi_case.offence = offence
                        offence_changed = True

                    else:
                        offence_changed = False

                    if detail != sersi_case.details and detail is not None:
                        sersi_case.details = detail
                        detail_changed = True

                    else:
                        detail_changed = False

                    if duration != sersi_case.duration and duration is not None:
                        sersi_case.duration = duration
                        duration_changed = True

                    else:
                        duration_changed = False

                    try:
                        time_delta: datetime.timedelta = convert_to_timedelta(
                            timespan, duration
                        )

                        planned_end = datetime.datetime.utcnow() + time_delta

                    except TypeError:
                        planned_end = sersi_case.planned_end

                    if planned_end != sersi_case.planned_end:
                        sersi_case.planned_end = planned_end
                        planned_end_changed = True
                        offender = interaction.guild.get_member(sersi_case.offender)
                        await offender.timeout(
                            time_delta,
                            reason=f"[Timeout Duration Edit - {interaction.user}",
                        )

                        embed_fields = {
                            "Offence:": f"`{sersi_case.offence}`",
                            "Detail:": f"`{sersi_case.details}`",
                            "Duration:": f"`{duration}{timespan}`",
                        }

                    else:
                        embed_fields = {
                            "Offence:": f"`{sersi_case.offence}`",
                            "Detail:": f"`{sersi_case.details}`",
                        }
                        planned_end_changed = False

                    if (
                        not detail_changed
                        and not offence_changed
                        and not duration_changed
                        and not planned_end_changed
                    ):
                        await interaction.followup.send(
                            f"{self.config.emotes.fail} You have not changed any details about the case!"
                        )
                        return

                    offender = interaction.guild.get_member(sersi_case.offender)

                    try:
                        await offender.send(
                            embed=SersiEmbed(
                                title=f"Timeout Updated in {interaction.guild.name}!",
                                description="A change has been made to your timeout. Please see below for the new case information.",
                                fields=embed_fields,
                                footer="Sersi Timeout",
                            ).set_thumbnail(interaction.guild.icon.url)
                        )

                    except (nextcord.Forbidden, nextcord.HTTPException):
                        pass

                    session.commit()
                    sersi_case = (
                        session.query(TimeoutCase).filter_by(id=sersi_case.id).first()
                    )

                    case_embed = create_case_embed(sersi_case, interaction, self.config)

                    await interaction.followup.send(
                        f"{self.config.emotes.success} Case Updated", embed=case_embed
                    )
                    return

    @edit.on_autocomplete("offence")
    async def search_offences(self, interaction: nextcord.Interaction, offence: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        offences: list[str] = fetch_offences_by_partial_name(offence)
        await interaction.response.send_autocomplete(sorted(offences))

    # TODO: its own cog perhaps?
    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
        description="Used to do stuff with offences",
    )
    async def offence(self, interaction: nextcord.Interaction):
        pass

    @offence.subcommand(description="Used to add a new offence")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offence_name: str = nextcord.SlashOption(
            name="offence",
            description="The name of the new offence",
            min_length=4,
            max_length=64,
        ),
        offence_description: str = nextcord.SlashOption(
            name="description",
            description="A description of the new offence",
            min_length=32,
            max_length=1024,
        ),
        offence_severity: int = nextcord.SlashOption(
            name="severity",
            description="The severity of the new offence",
            min_value=1,
            max_value=5,
            required=False,
        ),
        offence_group: str = nextcord.SlashOption(
            name="group",
            description="The group of the new offence",
            min_length=4,
            max_length=64,
            required=False,
        ),
        p_0: str = nextcord.SlashOption(
            name="first_punishment",
            description="This is the punishment for the first instance of the offence",
            choices=punishment_choices,
            required=False,
        ),
        p_1: str = nextcord.SlashOption(
            name="second_punishment",
            description="This is the punishment for the second instance of the offence",
            choices=punishment_choices,
            required=False,
        ),
        p_2: str = nextcord.SlashOption(
            name="third_punishment",
            description="This is the punishment for the third instance of the offence",
            choices=punishment_choices,
            required=False,
        ),
        p_3: str = nextcord.SlashOption(
            name="fourth_punishment",
            description="This is the punishment for the fourth instance of the offence",
            choices=punishment_choices,
            required=False,
        ),
        p_4: str = nextcord.SlashOption(
            name="fifth_punishment",
            description="This is the punishment for the fifth instance of the offence",
            choices=punishment_choices,
            required=False,
        ),
        p_5: str = nextcord.SlashOption(
            name="sixth_punishment",
            description="This is the punishment for the sixth instance of the offence",
            choices=punishment_choices,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return

        await interaction.response.defer(ephemeral=False)

        punishments = [p for p in [p_0, p_1, p_2, p_3, p_4, p_5] if p]

        with db_session(interaction.user) as session:
            session.add(
                Offence(
                    offence=offence_name,
                    detail=offence_description,
                    warn_severity=offence_severity,
                    group=offence_group,
                    punishments="|".join([p for p in punishments if p]),
                )
            )

        offence_added_log = SersiEmbed(
            title="New Offence Added",
            fields={
                "Offence": f"`{offence_name}`",
                "Description": f"`{offence_description}`",
                "Severity": f"`{offence_severity}`",
                "Punishments": f"`{'`, `'.join(punishments)}`",
                "Group": f"`{offence_group}`",
            },
        )
        offence_added_log.set_footer(text="Sersi Offences")

        logging_channel: nextcord.TextChannel = interaction.guild.get_channel(
            self.config.channels.logging
        )

        await logging_channel.send(embed=offence_added_log)

        await interaction.followup.send(embed=offence_added_log)

    @detail.on_autocomplete("case_id")
    @audit.on_autocomplete("case_id")
    @scrub.on_autocomplete("case_id")
    @delete.on_autocomplete("case_id")
    @edit.on_autocomplete("case_id")
    async def cases_by_id(self, interaction: nextcord.Interaction, case: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        cases = fetch_cases_by_partial_id(case)
        await interaction.response.send_autocomplete(cases)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Cases(bot, kwargs["config"]))
