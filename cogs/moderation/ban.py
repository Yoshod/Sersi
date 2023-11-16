import nextcord

from nextcord.ext import commands
from nextcord.ui import Button, View
from pytz import timezone
import datetime

from utils.cases import (
    create_case_embed,
    get_case_by_id,
    check_if_banned,
)
from utils.config import Configuration
from utils.database import VoteRecord, db_session, BanCase, VoteDetails
from utils.objection import AlertView
from utils.offences import fetch_offences_by_partial_name, offence_validity_check
from utils.perms import (
    is_full_mod,
    permcheck,
    is_mod,
    is_immune,
    target_eligibility,
    is_senior_mod,
    is_dark_mod,
    unban_eligibility,
)
from utils.sersi_embed import SersiEmbed
from utils.review import create_alert
from utils import logs
from utils.voting import VoteView, vote_planned_end
from utils.base import convert_to_timedelta


class BanSystem(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
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

        # update_approved(new_embed.fields[0].value, self.config)

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
            self.config, interaction.message, datetime.datetime.now(timezone.utc)
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

        # update_objected(new_embed.fields[0].value, self.config)

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
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Used to do ban stuff",
    )
    async def ban(self, interaction: nextcord.Interaction):
        pass

    @ban.subcommand(description="Used to ban a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The person you wish to ban.",
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence for which the user is being banned.",
        ),
        detail: str = nextcord.SlashOption(
            name="detail",
            description="Details on the offence,",
            min_length=8,
            max_length=1024,
        ),
        ban_type: str = nextcord.SlashOption(
            name="type",
            description="The type of ban",
            choices={
                "Vote Ban": "urgent",
                "Immediate Ban": "emergency",
            },
        ),
        timeout: bool = nextcord.SlashOption(
            name="timeout",
            description="Should the user be timed out?",
            choices={
                "Yes": True,
                "No": False,
            },
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if ban_type == "emergency" and not await permcheck(interaction, is_full_mod):
            return

        if ban_type == "emergency" and timeout:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} You cannot do an Immediate Ban with a Timeout",
                ephemeral=True,
            )

        elif ban_type == "emergency":
            await interaction.response.defer()

        else:
            await interaction.response.defer(ephemeral=True)

        try:
            if not target_eligibility(interaction.user, offender):
                warning_alert = SersiEmbed(
                    title="Unauthorised Moderation Target",
                    description=f"{interaction.user.mention} ({interaction.user.id}) attempted to ban {offender.mention} ({offender.id}) despite being outranked!",
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

        except AttributeError:
            pass

        try:
            await interaction.guild.fetch_ban(offender)
            await interaction.send(
                f"{self.config.emotes.fail} {offender.mention} is already banned.",
                ephemeral=True,
            )
            return

        except nextcord.NotFound:
            pass

        if not offence_validity_check(offence):
            await interaction.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. Try again or consider using the 'Other' offence.",
                ephemeral=True,
            )
            return

        sersi_case = BanCase(
            offender=offender.id,
            moderator=interaction.user.id,
            offence=offence,
            details=detail,
            ban_type=ban_type,
        )

        with db_session(interaction.user) as session:
            session.add(sersi_case)
            session.commit()

            sersi_case = session.query(BanCase).filter_by(id=sersi_case.id).first()

        match ban_type:
            case "urgent":
                if timeout:
                    vote_embed = SersiEmbed(
                        title=f"Ban Vote: **{offender.name}** ({offender.id})",
                        description=f"A Moderator has requested an Ban Vote be held for {offender.mention}. The moderator has decided that the user has should be timedout and cannot participate in {interaction.guild.name}. The user has been informed they are timed out, but not why. Please review the details below carefuly in order to make an accurate decision.",
                        fields={
                            "Moderator": interaction.user.mention,
                            "Offender": offender.mention,
                            "Offence": offence,
                            "Offence Details": detail,
                        },
                    )

                    try:
                        await offender.send(
                            embed=SersiEmbed(
                                title=f"You have been timed out in {interaction.guild.name}!",
                                description=f"You have been timed out in {interaction.guild.name}.",
                                fields={
                                    "Duration:": "`3 Days`",
                                },
                                footer="Sersi Timeout",
                            ).set_thumbnail(interaction.guild.icon.url)
                        )

                    except (nextcord.Forbidden, nextcord.HTTPException):
                        pass

                    planned_end: datetime.timedelta = convert_to_timedelta("h", 72)

                    await offender.timeout(
                        planned_end,
                        reason=f"[{offence}: {detail}] - {interaction.user}",
                    )

                else:
                    vote_embed = SersiEmbed(
                        title=f"Ban Vote: **{offender.name}** ({offender.id})",
                        description=f"A Moderator has requested an Urgent Ban Vote be held for {offender.mention}. The moderator has decided that the user should not be timedout and can still participate in {interaction.guild.name}. Please review the details below carefuly in order to make an accurate decision.",
                        fields={
                            "Moderator": interaction.user.mention,
                            "Offender": offender.mention,
                            "Offence": offence,
                            "Offence Details": detail,
                        },
                    )

                vote_type = self.config.voting["urgent-ban"]
                with db_session(interaction.user) as session:
                    vote_case = VoteDetails(
                        case_id=sersi_case.id,
                        vote_type="urgent-ban",
                        vote_url=interaction.channel.mention,
                        planned_end=vote_planned_end(vote_type),
                        started_by=interaction.user.id,
                    )

                    session.add(vote_case)
                    session.commit()

                    channel = self.bot.get_channel(
                        self.config.channels.moderation_votes
                    )
                    vote_message = await channel.send(
                        embed=vote_embed, view=VoteView(vote_type, vote_case)
                    )

                    vote_case.vote_url = vote_message.jump_url
                    session.commit()

                await interaction.followup.send(
                    f"{self.config.emotes.success} Vote Created!"
                )

            case "emergency":
                ban_confirmation = SersiEmbed(
                    title=f"Confirm Ban of **{offender.name}** ({offender.id})",
                    description="Are you sure that you wish to proceed?",
                    fields={
                        "Moderator": interaction.user.mention,
                        "Offender": offender.mention,
                        "Offence": offence,
                        "Offence Details": detail,
                    },
                )

                approve = Button(
                    label="Yes",
                    style=nextcord.ButtonStyle.red,
                    custom_id=f"ban-confirm:{sersi_case.id}",
                )

                object = Button(
                    label="No",
                    style=nextcord.ButtonStyle.blurple,
                    custom_id=f"ban-no:{sersi_case.id}",
                )

                button_view = View(timeout=10800)
                button_view.add_item(approve)
                button_view.add_item(object)

                await interaction.followup.send(
                    embed=ban_confirmation, view=button_view
                )

    @ban.subcommand(description="Used to ban a user")
    async def remove(
        self,
        interaction: nextcord.Interaction,
        offender: str = nextcord.SlashOption(
            name="offender_id",
            description="The person you wish to unban.",
            min_length=17,
            max_length=18,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="Reason you are unbanning the user",
            min_length=8,
            max_length=1024,
        ),
        original_case: str = nextcord.SlashOption(
            name="ban_id",
            description="The ID of the original ban case",
            min_length=6,
            max_length=22,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return

        try:
            offender = int(offender)

        except ValueError:
            await interaction.response.send_message(
                f"{self.config.emotes.fail} Invalid Case ID"
            )

        await interaction.response.defer(ephemeral=True)

        with db_session(interaction.user) as session:
            if original_case == "LEGACY":
                if not await permcheck(interaction, is_dark_mod):
                    return

                await interaction.guild.unban(
                    nextcord.Object(id=offender), reason=reason
                )

                await interaction.followup.send(
                    f"{self.config.emotes.success} User Unbanned!"
                )
                return

            sersi_case: BanCase = (
                session.query(BanCase).filter_by(id=original_case).first()
            )

            if not sersi_case:
                interaction.followup.send(
                    f"{self.config.emotes.fail} No case has been found with the ID {original_case}."
                )
                return

        if not unban_eligibility(
            interaction.user, interaction.guild.get_member(sersi_case.moderator)
        ):
            await interaction.followup.send(
                f"{self.config.emotes.fail} {interaction.user.mention} Ban Case `{sersi_case.id}` was carried out by someone of a higher level than you. Please ask them to review the ban and consider an unban."
            )
            return

        try:
            await interaction.guild.unban(
                nextcord.Object(id=sersi_case.offender), reason=reason
            )

        except nextcord.HTTPException:
            await interaction.followup.send(
                f"{self.config.emotes.fail} Unable to unban. Manual Unban via Discord client interface is authorised!"
            )
            return

        with db_session(interaction.user) as session:
            sersi_case = session.query(BanCase).filter_by(id=sersi_case.id).first()
            sersi_case.active = False
            sersi_case.unbanned_by = interaction.user.id
            sersi_case.unban_reason = reason
            session.commit()

            sersi_case = session.query(BanCase).filter_by(id=sersi_case.id).first()

        unbanned_embed = create_case_embed(sersi_case, interaction, self.config)

        await interaction.followup.send(
            f"{self.config.emotes.success} User has been unbanned successfully!",
            embed=unbanned_embed,
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        match btn_id.split(":", 1):
            case ["urgent-ban-approve", uuid]:
                for field in interaction.message.embeds[0].fields:
                    if field.value.splitlines()[0] == interaction.user.mention:
                        await interaction.followup.send(
                            "You already voted", ephemeral=True
                        )
                        return

                new_embed = interaction.message.embeds[0]
                new_embed.add_field(
                    name="Voted Yes:",
                    value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*",
                    inline=True,
                )
                yes_votes = new_embed.description[-1]
                yes_votes = int(yes_votes) + 1

                new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
                await interaction.message.edit(embed=new_embed)

                if yes_votes >= 3:
                    await interaction.message.edit(view=None)

                    yes_men = []
                    for field in new_embed.fields:
                        if field.name == "Voted Yes:":
                            yes_men.append(field.value)

                    sersi_case = get_case_by_id(self.config, uuid, False)

                    offender: nextcord.Member = interaction.guild.get_member(
                        sersi_case["Offender ID"]
                    )

                    try:
                        await offender.send(
                            embed=SersiEmbed(
                                title=f"You have been banned in {interaction.guild.name}!",
                                description=f"You have been banned in {interaction.guild.name}. The details about the ban are "
                                "below. If you would like to appeal your ban you can do so:\n"
                                "https://appeals.wickbot.com",
                                fields={
                                    "Offence:": f"`{sersi_case['Offence']}`",
                                    "Detail:": f"`{sersi_case['Details']}`",
                                },
                                footer="Sersi Ban",
                            ).set_thumbnail(interaction.guild.icon.url)
                        )
                        not_sent = False

                    except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                        not_sent = True

                    logging_embed: SersiEmbed = create_case_embed(
                        sersi_case,
                        interaction=interaction,
                    )

                    await interaction.guild.get_channel(
                        self.config.channels.mod_logs
                    ).send(embed=logging_embed)
                    await interaction.guild.get_channel(
                        self.config.channels.logging
                    ).send(embed=logging_embed)

                    await offender.ban(reason=f"Sersi Ban {sersi_case['Details']}")

                    await interaction.followup.send(
                        embed=SersiEmbed(
                            title="Ban Result:",
                            fields={
                                "Offence:": f"`{sersi_case['Offence']}`",
                                "Detail:": f"`{sersi_case['Details']}`",
                                "Member:": f"{offender.mention} ({offender.id})",
                                "DM Sent:": self.config.emotes.fail
                                if not_sent
                                else self.config.emotes.success,
                            },
                            footer="Sersi Ban",
                        ),
                        wait=True,
                    )

                    with db_session(interaction.user) as session:
                        session.add(sersi_case)
                        session.commit()

                else:
                    await interaction.followup.send(
                        "Your vote has been recorded as 'Approve'."
                    )

            case ["urgent-ban-object", uuid]:
                for field in interaction.message.embeds[0].fields:
                    if field.value.splitlines()[0] == interaction.user.mention:
                        await interaction.followup.send(
                            "You already voted", ephemeral=True
                        )
                        return

                new_embed = interaction.message.embeds[0]
                new_embed.add_field(
                    name="Voted No:",
                    value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*",
                    inline=True,
                )
                no_votes = new_embed.description[-1]
                no_votes = int(no_votes) + 1

                new_embed.description = f"{new_embed.description[:-1]}{no_votes}"
                await interaction.message.edit(embed=new_embed)

                await interaction.followup.send(
                    "Your vote has been recorded as 'Object'."
                )

            case ["ban-confirm", uuid]:
                if not await permcheck(interaction, is_full_mod):
                    return

                await interaction.message.edit(view=None)

                sersi_case: BanCase = get_case_by_id(uuid)
                offender: nextcord.Member = interaction.guild.get_member(
                    sersi_case.offender
                )

                try:
                    await offender.send(
                        embed=SersiEmbed(
                            title=f"You have been banned in {interaction.guild.name}!",
                            description=f"You have been banned in {interaction.guild.name}. The details about the ban are "
                            "below. If you would like to appeal your ban you can do so:\n"
                            "https://appeals.wickbot.com",
                            fields={
                                "Offence:": f"`{sersi_case.offence}`",
                                "Detail:": f"`{sersi_case.details}`",
                            },
                            footer="Sersi Ban",
                        ).set_thumbnail(interaction.guild.icon.url)
                    )
                    not_sent = False

                except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                    not_sent = True

                logging_embed: SersiEmbed = create_case_embed(
                    sersi_case, interaction=interaction, config=self.config
                )

                await interaction.guild.get_channel(self.config.channels.mod_logs).send(
                    embed=logging_embed
                )
                await interaction.guild.get_channel(self.config.channels.logging).send(
                    embed=logging_embed
                )

                offender: nextcord.User = await interaction.client.fetch_user(
                    sersi_case.offender
                )

                await interaction.guild.ban(
                    offender, reason=f"{[sersi_case.details]} -{interaction.user.name}"
                )

                with db_session(interaction.user) as session:
                    case: BanCase = session.query(BanCase).filter_by(id=uuid).first()
                    case.active = True
                    session.commit()

                    case: BanCase = session.query(BanCase).filter_by(id=uuid).first()

                result: nextcord.WebhookMessage = await interaction.message.edit(
                    embed=SersiEmbed(
                        title="Ban Result:",
                        fields={
                            "Offence:": f"`{sersi_case.offence}`",
                            "Detail:": f"`{sersi_case.details}`",
                            "Member:": f"{offender.mention} ({offender.id})",
                            "DM Sent:": self.config.emotes.fail
                            if not_sent
                            else self.config.emotes.success,
                            "Sent for Review:": self.config.emotes.success,
                        },
                        footer="Sersi Ban",
                    ),
                )

                (
                    reviewer_role,
                    reviewed_role,
                    review_embed,
                    review_channel,
                ) = create_alert(
                    interaction.user,
                    self.config,
                    logging_embed,
                    sersi_case,
                    result.jump_url,
                )

                await review_channel.send(
                    f"{reviewer_role.mention} a ban by a {reviewed_role.mention} has been taken and should now be reviewed.",
                    embed=review_embed,
                    view=AlertView(self.config, reviewer_role, sersi_case),
                )

            case ["ban-no", uuid]:
                if not await permcheck(interaction, is_mod):
                    return

                sersi_case: BanCase = get_case_by_id(uuid)
                offender: nextcord.Member = interaction.guild.get_member(
                    sersi_case.offender
                )

                with db_session(interaction.user) as session:
                    case: BanCase = session.query(BanCase).filter_by(id=uuid).first()
                    session.delete(case)

                    result: nextcord.WebhookMessage = await interaction.message.edit(
                        embed=SersiEmbed(
                            title="Ban Cancelled:",
                            description=f"{self.config.emotes.success} Ban has been cancelled!",
                            footer="Sersi Ban",
                        ),
                    )

                    await interaction.message.edit(view=None)

                    session.commit()

    @add.on_autocomplete("offence")
    async def search_offences(self, interaction: nextcord.Interaction, offence: str):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        offences: list[str] = fetch_offences_by_partial_name(offence)
        await interaction.response.send_autocomplete(sorted(offences))

    @commands.Cog.listener()
    async def on_vote_ban(self, detail: VoteDetails):
        if detail.outcome != "Accepted":
            return

        guild: nextcord.Guild = self.bot.get_guild(self.config.guilds.main)

        # close case
        with db_session() as session:
            case: BanCase = session.query(BanCase).get(detail.case_id)
            case.active = True

            user: nextcord.Member = guild.get_member(case.offender)
            if user is None:
                user: nextcord.User = await self.bot.fetch_user(case.offender)

            yes_voters = [
                vote[0]
                for vote in session.query(VoteRecord.voter)
                .filter_by(vote_id=detail.vote_id, vote="yes")
                .all()
            ]

            try:
                await user.send(
                    embed=SersiEmbed(
                        title=f"You have been banned in {guild.name}!",
                        description=f"You have been banned in {guild.name}. The details about the ban are "
                        "below. If you would like to appeal your ban you can do so:\n"
                        "https://appeals.wickbot.com",
                        fields={
                            "Offence:": f"`{case.offence}`",
                            "Detail:": f"`{case.details}`",
                        },
                        footer="Sersi Ban",
                    ).set_thumbnail(guild.icon.url)
                )

            except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
                pass

            if isinstance(user, nextcord.Member):
                await user.edit(timeout=None, reason="Ban Vote Successfull")

            await guild.ban(user, reason=f"Sersi Ban {case.details}")

            session.commit()
            case: BanCase = session.query(BanCase).get(detail.case_id)

        # logging
        yes_list = "\n• ".join(yes_voters)

        embed = nextcord.Embed(
            title="Vote Ban Complete",
            description=f"{self.config.emotes.success} {user.mention} ({user.id}) has been banned."
            f"Yes Voters: {yes_list}",
            color=nextcord.Color.from_rgb(0, 0, 0),
        )

        channel = self.bot.get_channel(self.config.channels.alert)
        await channel.send(embed=embed)

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

        channel = self.bot.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=embed)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(BanSystem(bot, kwargs["config"]))
