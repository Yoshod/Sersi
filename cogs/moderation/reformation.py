import nextcord
from nextcord.ext import commands

from utils.base import ConfirmView, SersiEmbed, ban
from utils.cases import get_reformation_next_case_number
from utils.channels import make_transcript
from utils.config import Configuration
from utils.database import db_session, BanCase, ReformationCase, VoteDetails, VoteRecord
from utils.offences import fetch_offences_by_partial_name
from utils.perms import permcheck, is_mod, is_senior_mod
from utils.roles import parse_roles
from utils.voting import VoteView, vote_planned_end


class Reformation(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersifail = config.emotes.fail

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def reformation(self, interaction: nextcord.Interaction):
        pass

    @reformation.subcommand(
        name="add", description="Send a user to reformation centre."
    )
    async def reformation_needed(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to send to reformation", required=True
        ),
        offence: str = nextcord.SlashOption(
            description="Offence committed by member",
            required=True,
        ),
        details: str = nextcord.SlashOption(
            description="Additional details about offence",
            required=True,
            min_length=8,
            max_length=1024,
        ),
    ):
        """Send a user to reformation centre.

        Sends a [member] to reformation centre for reform by giving said [member] the @Reformation role.
        Removes @Civil Engineering Initiate and all Opt-In-Roles.
        Permission Needed: Moderator, Trial Moderator.
        """

        if not await permcheck(interaction, is_mod):
            return

        reformation_role = interaction.guild.get_role(self.config.roles.reformation)

        if reformation_role in member.roles:
            await interaction.send(
                f"{self.sersifail} member is already in reformation", ephemeral=True
            )
            return

        await interaction.response.defer()

        @ConfirmView.query(
            title="Reformation Needed",
            prompt="Following member will be sent to reformation:",
            embed_args={
                "User": member.mention,
                "Offence": offence,
                "Details": details,
            },
        )
        async def execute(*args, **kwargs):
            # ------------------------------- ROLES
            # give reformation role
            reason = f"{offence} - {details}"

            await member.add_roles(reformation_role, reason=reason)

            # remove civil engineering initiate
            await member.remove_roles(
                *parse_roles(
                    interaction.guild,
                    self.config.roles.civil_engineering_initiate,
                ),
                reason=reason,
            )

            # remove opt-ins
            await member.remove_roles(
                *parse_roles(interaction.guild, *self.config.opt_in_roles.values()),
                reason=reason,
            )

            # ------------------------------- CREATING THE CASE CHANNEL
            # get case number

            case_num = get_reformation_next_case_number()

            case_name = f"reformation-case-{str(case_num).zfill(4)}"
            overwrites = {
                interaction.guild.default_role: nextcord.PermissionOverwrite(
                    read_messages=False
                ),
                interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True),
                interaction.guild.get_role(
                    self.config.permission_roles.reformist
                ): nextcord.PermissionOverwrite(read_messages=True),
                interaction.guild.get_role(
                    self.config.permission_roles.moderator
                ): nextcord.PermissionOverwrite(read_messages=True),
                member: nextcord.PermissionOverwrite(
                    read_messages=True,
                    create_public_threads=False,
                    create_private_threads=False,
                    external_stickers=False,
                    embed_links=False,
                    attach_files=False,
                    use_external_emojis=False,
                ),
            }
            category = nextcord.utils.get(
                interaction.guild.categories, name="REFORMATION ROOMS"
            )

            case_channel = await interaction.guild.create_text_channel(
                case_name, overwrites=overwrites, category=category
            )

            # ------------------------------- INSERT CASE INTO DATABASE

            with db_session() as session:
                session.add(
                    ReformationCase(
                        case_number=case_num,
                        offender=member.id,
                        moderator=interaction.user.id,
                        offence=offence,
                        details=details,
                        cell_channel=case_channel.id,
                        state="open",
                    )
                )
                session.commit()

            # ------------------------------- LOGGING

            # Giving a welcome to the person sent to reformation
            welcome_embed = SersiEmbed(
                title="Welcome to Reformation",
                description=f"Hello {member.mention}, you have been sent to reformation by {interaction.user.mention}. "
                f"The reason given for this is `{reason}`. \n\nFor more information on reformation "
                f"check out <#{self.config.channels.reformation_info}> or talk to a <@&"
                f"{self.config.permission_roles.reformist}>.",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )

            await case_channel.send(embed=welcome_embed)

            embed = SersiEmbed(
                title="User Has Been Sent to Reformation",
                description=f"Moderator {interaction.user.mention} ({interaction.user.id}) has sent user {member.mention}"
                f" ({member.id}) to reformation.\n\n" + f"**__Reason:__**\n{reason}",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )

            channel = interaction.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(
                self.config.channels.reform_public_log
            )
            await channel.send(embed=embed)

            return embed

        await execute(self.bot, self.config, interaction)

    @reformation_needed.on_autocomplete("offence")
    async def offence_by_name(self, interaction: nextcord.Interaction, string: str):
        if not await permcheck(interaction, is_mod):
            return

        return fetch_offences_by_partial_name(string)

    @reformation.subcommand(
        name="query_release",
        description="Query releasing a user from reformation centre.",
    )
    async def reformation_query(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to send to reformation", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for sending to reformation",
            required=True,
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == self.config.roles.reformation:
                is_in_reformation = True
        if not is_in_reformation:
            await interaction.send("Member is not in reformation.")
            return

        await interaction.response.defer()

        embedVar = SersiEmbed(
            title=f"Reformation Query: **{member.name}** ({member.id})",
            description=f"Reformation Inmate {member.name} was deemed well enough to start a query about their "
            f"release\nQuery started by {interaction.user.mention} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6),
            footer=f"{member.id}",
            fields={
                "Reason": reason,
            },
        )

        vote_type = self.config.voting["reform-free"]

        with db_session(interaction.user) as session:
            case: ReformationCase = (
                session.query(ReformationCase)
                .filter_by(offender=member.id, state="open")
                .first()
            )

            if case is None:
                await interaction.send("Reformation case for member not found.")
                return

            vote_details = VoteDetails(
                case_id=case.id,
                vote_type="reform-free",
                vote_url=interaction.channel.id,
                planned_end=vote_planned_end(vote_type),
                started_by=interaction.user.id,
            )

            session.add(vote_details)
            session.commit()

            channel = self.bot.get_channel(self.config.channels.moderation_votes)
            message = await channel.send(
                embed=embedVar, view=VoteView(vote_type, vote_details)
            )

            vote_details.vote_url = message.jump_url
            session.commit()

        await interaction.followup.send(
            f"Release from reformation vote {message.jump_url} for {member.mention} was started.",
            ephemeral=True,
        )

    @reformation.subcommand(
        name="query_failed", description="Query a ban of failed reformation inmate."
    )
    async def reformation_failed(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to ban", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for banning member",
            required=False,
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == self.config.roles.reformation:
                is_in_reformation = True
        if not is_in_reformation:
            await interaction.send("Member is not in reformation.")
            return

        await interaction.response.defer()

        embedVar = SersiEmbed(
            title=f"Reformation Failed Query: **{member.name}** ({member.id})",
            description=f"Reformation Inmate {member.name} seems to not be able to be reformed. Should the "
            f"reformation process therefore be given up and the user be banned?\nQuery"
            f" started by {interaction.user.mention} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6),
            footer=f"{member.id}",
            fields={
                "Reason": reason,
            },
        )

        vote_type = self.config.voting["reform-fail"]

        with db_session(interaction.user) as session:
            case: ReformationCase = (
                session.query(ReformationCase)
                .filter_by(offender=member.id, state="open")
                .first()
            )

            if case is None:
                await interaction.send("Reformation case for member not found.")
                return

            vote_details = VoteDetails(
                case_id=case.id,
                vote_type="reform-fail",
                vote_url=interaction.channel.id,
                planned_end=vote_planned_end(vote_type),
                started_by=interaction.user.id,
            )

            session.add(vote_details)
            session.commit()

            channel = self.bot.get_channel(self.config.channels.moderation_votes)
            message = await channel.send(
                embed=embedVar, view=VoteView(vote_type, vote_details)
            )

            vote_details.vote_url = message.jump_url
            session.commit()

        await interaction.followup.send(
            f"Reformation fail vote {message.jump_url} for {member.mention} was started.",
            ephemeral=True,
        )

    @reformation.subcommand(
        name="release", description="Release a user from reformation centre. (manual)"
    )
    async def reformation_release(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to release", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for releasing member",
            required=True,
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == self.config.roles.reformation:
                is_in_reformation = True
        if not is_in_reformation:
            await interaction.send("Member is not in reformation.")
            return

        await interaction.response.defer()

        @ConfirmView.query(
            title="Release Member from reformation",
            prompt="Following member will be released from reformation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            },
        )
        async def execute(*args, **kwargs):
            # remove reformation role
            await member.remove_roles(
                *parse_roles(interaction.guild, self.config.roles.reformation),
                reason=reason,
            )

            # add civil engineering initiate role
            await member.add_roles(
                *parse_roles(
                    interaction.guild, self.config.roles.civil_engineering_initiate
                ),
                reason=reason,
            )

            # close case
            with db_session(interaction.user) as session:
                case: ReformationCase = (
                    session.query(ReformationCase)
                    .filter_by(offender=member.id, state="open")
                    .first()
                )
                case.state = "released"
                session.commit()

            # logging
            embed = SersiEmbed(
                title="User Has Been Released from Reformation",
                description=f"Lead Moderator {interaction.user.mention} ({interaction.user.id}) has released user {member.mention}"
                f" ({member.id}) from reformation.\n\n" + f"**__Reason:__**\n{reason}",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )

            channel = interaction.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(
                self.config.channels.reform_public_log
            )
            await channel.send(embed=embed)

            # transcript
            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            cell_channel = interaction.guild.get_channel(case.cell_channel)

            transcript = await make_transcript(cell_channel, interaction.channel, embed)
            if transcript is None:
                await channel.send(embed=embed)
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")

            await cell_channel.delete()

            return embed

        await execute(self.bot, self.config, interaction)

    @reformation.subcommand(
        name="delete_cell",
        description="Delete an unoccupied reformation cell if it was not deleted automatically.",
    )
    async def reformation_delete_cell(
        self,
        interaction: nextcord.Interaction,
    ):
        if not await permcheck(interaction, is_mod):
            return

        with db_session() as session:
            case: ReformationCase = (
                session.query(ReformationCase)
                .filter_by(cell_channel=interaction.channel.id)
                .first()
            )

            if case is None:
                await interaction.response.send_message(
                    "This is not a reformation cell.", ephemeral=True
                )
                return

            if case.state == "open":
                await interaction.response.send_message(
                    "Reformation case is still open.", ephemeral=True
                )
                return

            embed = SersiEmbed(
                title="Reformation Cell Deleted",
                description=f"Reformation cell for case {case.id} has been deleted by {interaction.user.mention} ({interaction.user.id})",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )

            # transcript
            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            cell_channel = interaction.guild.get_channel(case.cell_channel)

            transcript = await make_transcript(cell_channel, channel, embed)
            if transcript is None:
                await channel.send(embed=embed)
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")

            await cell_channel.delete()

            return

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        reformation_role = member.get_role(self.config.roles.reformation)

        if reformation_role is not None:
            async for ban_entry in member.guild.bans():
                if member.id == ban_entry.user.id:
                    # close case
                    with db_session() as session:
                        case: ReformationCase = (
                            session.query(ReformationCase)
                            .filter_by(offender=member.id, state="open")
                            .first()
                        )
                        if case is None:
                            return
                        case.state = "failed"
                        session.commit()

                    ban_embed = nextcord.Embed(
                        title=f"Reformation inmate **{member}** ({member.id}) banned!",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    ban_embed.add_field(name="Reason:", value=ban_entry.reason)
                    channel = self.bot.get_channel(self.config.channels.mod_logs)
                    await channel.send(embed=ban_embed)

                    # transcript
                    channel = member.guild.get_channel(
                        self.config.channels.teachers_lounge
                    )
                    cell_channel = member.guild.get_channel(case.cell_channel)

                    transcript = await make_transcript(cell_channel, channel, ban_embed)
                    if transcript is None:
                        await channel.send(embed=ban_embed)
                        await channel.send(
                            f"{self.sersifail} Failed to Generate Transcript!"
                        )

                    await cell_channel.delete()

                    return

            # member not yet banned, proceed to ban
            # await member.ban(reason="Left while in reformation centre.", delete_message_days=0)
            await ban(member, "leave", reason="Left while in reformation centre.")

            channel = self.bot.get_channel(self.config.channels.alert)
            embed = nextcord.Embed(
                title=f"User **{member}** ({member.id}) has left the server while in the reformation centre!",
                description=f"User has left the server while having the <@&{self.config.roles.reformation}> role. "
                f"They have been banned automatically.",
                colour=nextcord.Color.from_rgb(237, 91, 6),
            )

            # close case
            with db_session() as session:
                case: ReformationCase = (
                    session.query(ReformationCase)
                    .filter_by(offender=member.id, state="open")
                    .first()
                )
                case.state = "failed"

                session.add(
                    BanCase(
                        offender=member.id,
                        moderator=member.guild.me.id,
                        offence=case.offence,
                        details=case.details,
                        active=True,
                        ban_type="reformation leave",
                    )
                )
                session.commit()

            # transcript
            channel = member.guild.get_channel(self.config.channels.teachers_lounge)
            cell_channel = member.guild.get_channel(case.cell_channel)

            transcript = await make_transcript(cell_channel, channel, embed)
            if transcript is None:
                await channel.send(embed=embed)
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")

            await cell_channel.delete()

    @commands.Cog.listener()
    async def on_reformation_ban(self, details: VoteDetails):
        print(details.outcome)
        if details.outcome != "Accepted":
            return

        guild = self.bot.get_guild(self.config.guilds.main)

        # close case
        with db_session() as session:
            case: ReformationCase = session.query(ReformationCase).get(details.case_id)
            case.state = "failed"

            member = guild.get_member(case.offender)

            yes_voters = [
                guild.get_member(vote[0]).mention
                for vote in session.query(VoteRecord.voter)
                .filter_by(vote_id=details.vote_id, vote="yes")
                .all()
            ]

            await ban(
                member, "rf", reason=f"Reformation Failed: {case.id} - {case.offence}"
            )

            session.add(
                BanCase(
                    offender=member.id,
                    moderator=details.started_by,
                    offence=case.offence,
                    details=case.details,
                    active=True,
                    ban_type="reformation failed",
                )
            )
            session.commit()

            embed_fields = {
                "Offender": member.mention,
                "Offence": case.offence,
                "Details": case.details,
            }

        # logging
        yes_list = "\n• ".join(yes_voters)

        embed = SersiEmbed(
            title="Reformation Failed",
            description=f"Reformation Inmate {member.name} has been deemed unreformable by\n•{yes_list}",
            color=nextcord.Color.from_rgb(0, 0, 0),
            fields=embed_fields,
        )

        channel = self.bot.get_channel(self.config.channels.alert)
        await channel.send(embed=embed)

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

        channel = self.bot.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=embed)

        # transcript
        channel = guild.get_channel(self.config.channels.teachers_lounge)
        cell_channel = guild.get_channel(case.cell_channel)

        transcript = await make_transcript(cell_channel, channel, embed)
        if transcript is None:
            await channel.send(embed=embed)
            await channel.send(f"{self.sersifail} Failed to Generate Transcript!")

        await cell_channel.delete()

    @commands.Cog.listener()
    async def on_reformation_release(self, details: VoteDetails):
        if details.outcome != "Accepted":
            return

        guild = self.bot.get_guild(self.config.guilds.main)

        # close case
        with db_session() as session:
            case: ReformationCase = session.query(ReformationCase).get(details.case_id)
            case.state = "reformed"
            session.commit()

            member = guild.get_member(case.offender)

            yes_voters = [
                guild.get_member(vote[0]).mention
                for vote in session.query(VoteRecord.voter)
                .filter_by(vote_id=details.vote_id, vote="yes")
                .all()
            ]

        # roles
        try:
            civil_engineering_initiate = guild.get_role(
                self.config.roles.civil_engineering_initiate
            )
            reformed = guild.get_role(self.config.roles.reformed)

            await member.add_roles(
                civil_engineering_initiate,
                reformed,
                reason="Released out of the Reformation Centre",
                atomic=True,
            )
        except AttributeError:
            pass
            # await interaction.send("Could not assign roles.")
        await member.remove_roles(
            guild.get_role(self.config.roles.reformation),
            reason="Released out of the Reformation Centre",
            atomic=True,
        )

        # logs
        yes_list = "\n• ".join(yes_voters)

        log_embed = nextcord.Embed(
            title=f"Successful Reformation: **{member.name}** ({member.id})",
            description=f"Reformation Member {member.name} was deemed well enough to be considered "
            f"reformed.\nThis has been approved by:\n• {yes_list}.",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        channel = guild.get_channel(self.config.channels.alert)
        await channel.send(embed=log_embed)

        channel = guild.get_channel(self.config.channels.logging)
        await channel.send(embed=log_embed)

        channel = guild.get_channel(self.config.channels.mod_logs)
        await channel.send(embed=log_embed)

        # transcript
        channel = guild.get_channel(self.config.channels.teachers_lounge)
        cell_channel = guild.get_channel(case.cell_channel)

        transcript = await make_transcript(cell_channel, channel, log_embed)
        if transcript is None:
            await channel.send(embed=log_embed)
            await channel.send(f"{self.sersifail} Failed to Generate Transcript!")

        await cell_channel.delete()


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Reformation(bot, kwargs["config"]))
