import nextcord
from nextcord import SlashOption
from nextcord.ext import commands

from utils.base import encode_snowflake
from utils.sersi_embed import SersiEmbed
from utils.views import ConfirmView, DualCustodyView
from utils.config import Configuration
from utils.perms import (
    permcheck,
    is_staff,
    is_mod_lead,
    is_slt,
    is_admin,
    is_cet_lead,
    blacklist_check,
)
from utils.database import (
    db_session,
    BlacklistCase,
    CaseApproval,
    VoteDetails,
    VoteRecord,
)
from utils.voting import VoteView, vote_planned_end
from utils.staff import StaffRole, Branch, add_staff_to_db, staff_retire, RemovalType


class Staff(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    async def remove_all_permission_roles(self, member: nextcord.Member):
        for role in vars(self.config.permission_roles):
            role_object: nextcord.Role = member.guild.get_role(
                vars(self.config.permission_roles)[role]
            )
            if role_object is None:
                continue
            try:
                await member.remove_roles(role_object)
            except nextcord.errors.HTTPException:
                continue

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def staff(self, interaction: nextcord.Interaction):
        pass

    @staff.subcommand(name="add")
    async def add_to_staff(self, interaction: nextcord.Interaction):
        pass

    @staff.subcommand(name="remove")
    async def remove_from_staff(self, interaction: nextcord.Interaction):
        pass

    @staff.subcommand(name="blacklist")
    async def blacklist(self, interaction: nextcord.Interaction):
        pass

    @add_to_staff.subcommand(
        description="Makes a server member a Trial Moderator",
    )
    async def trial_moderator(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        if not permcheck(interaction, is_mod_lead):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is blacklisted from the Staff Team. Speak to an Administrator."
            )
            return

        trial_moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.trial_moderator
        )
        await member.add_roles(trial_moderator, reason="Sersi command", atomic=True)

        await interaction.send(
            f"{self.config.emotes.success} {member.mention} was given the {trial_moderator.name} role."
        )

        # logging
        add_staff_to_db(member.id, Branch.MOD, StaffRole.TRIAL_MOD, interaction.user.id)

        log_embed = SersiEmbed(
            title="New Trial Moderator added.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                f"New {trial_moderator.name}:": member.mention,
            },
            footer="Sersi Add Trial Mod",
        ).set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @add_to_staff.subcommand(
        description="Promotes a Trial Moderator to Moderator",
    )
    async def promote(self, interaction: nextcord.Interaction, member: nextcord.Member):
        if not permcheck(interaction, is_mod_lead):
            return

        await interaction.response.defer()

        trial_moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.trial_moderator
        )
        moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.moderator
        )

        if trial_moderator not in member.roles:
            await interaction.followup.send(
                f"{self.config.emotes.fail} Moderators need to be trial modertors first"
            )
            return

        await member.remove_roles(trial_moderator, reason="Sersi command", atomic=True)
        await member.add_roles(moderator, reason="Sersi command", atomic=True)

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} was given the {moderator.name} role.\n"
            "Remember: You're not truly a moderator until your first ban. ;)",
        )

        # logging
        log_embed = SersiEmbed(
            title="Trial Moderator matured into a full Moderator.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                "New Moderator:": member.mention,
            },
            footer="Sersi Add Trial Mod",
        ).set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @add_to_staff.subcommand(description="Reinstates a retired Moderator")
    async def reinstate_moderator(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        if not permcheck(interaction, is_mod_lead):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is blacklisted from the Staff Team. Speak to an Administrator."
            )
            return

        honourable_member: nextcord.Role = interaction.guild.get_role(
            self.config.roles.honourable_member
        )
        moderator: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.moderator
        )

        if honourable_member not in member.roles:
            await interaction.followup.send(
                f"{self.config.emotes.fail} This user is not an Honourable Member and therefore cannot be reinstated as a Moderator."
            )
            return

        await interaction.response.defer()

        await member.remove_roles(
            honourable_member, reason="Sersi command", atomic=True
        )
        await member.add_roles(moderator, reason="Sersi command", atomic=True)

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} was given the {moderator.name} role.\n"
            "Welcome back to the team! :)",
        )

        # logging
        log_embed = SersiEmbed(
            title="Honourable Member reinstated as a Moderator.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                "New Moderator:": member.mention,
            },
            footer="Sersi Add Trial Mod",
            author=interaction.user,
        )
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )
        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @add_to_staff.subcommand(description="Adds a new member to the CE-Team")
    async def community_engagement(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        if not permcheck(interaction, is_cet_lead):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is blacklisted from the Staff Team. Speak to an Administrator."
            )
            return

        cet: nextcord.Role = interaction.guild.get_role(
            self.config.permission_roles.cet
        )
        await member.add_roles(cet, reason="Sersi command", atomic=True)

        await interaction.send(
            f"{self.config.emotes.success} {member.mention} was given the {cet.name} role."
        )

        # logging
        log_embed = SersiEmbed(
            title="New CE-Team Member added.",
            fields={
                "Responsible CETL:": interaction.user.mention,
                f"New {cet.name}:": member.mention,
            },
            footer="Sersi Add CET Mod",
        ).set_author(
            name=interaction.user, icon_url=interaction.user.display_avatar.url
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

    @remove_from_staff.subcommand(
        description="Discharge from Server Staff.",
    )
    async def discharge(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            required=True,
            description="User you wish to discharge and blacklist from Server Staff",
        ),
        reason: str = SlashOption(
            required=True,
            description="Reason for discharging the user;",
            min_length=8,
            max_length=1024,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="ADMINISTRATOR ONLY! Reason to bypass dual custody",
            min_length=8,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_slt):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is already blacklisted from the staff team."
            )
            return

        await interaction.response.defer()

        @ConfirmView.query(
            title="Discharge Staff Member",
            prompt=f"""Are you sure you want to proceed with dishonourable discharge of {member.mention}?
                All staff and permission roles will be removed from the member.
                This action will result in the user being blacklisted from the server staff.""",
            embed_args={"Reason": reason},
        )
        @DualCustodyView.query(
            title="Discharge Staff Member",
            prompt="Following staff member will be dishonorably discharged from the staff:",
            perms=is_slt,
            embed_args={"Member": member, "Reason": reason},
            bypass=True if bypass_reason else False,
        )
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            # remove staff/permission roles
            await self.remove_all_permission_roles(member)

            staff_retire(
                member, RemovalType.REMOVED_BAD_STANDING, interaction.user.id, reason
            )

            embed_fields = {
                "Discharged Member:": member.mention,
                "Reason:": reason,
                "Responsible Member:": interaction.user.mention,
            }
            if bypass_reason and is_admin(interaction.user):
                embed_fields["Bypass Reason:"] = bypass_reason
            else:
                embed_fields["Confirming Member:"] = confirming_moderator.mention

            log_embed = SersiEmbed(
                title="Dishonourable Discharge of Staff Member",
                description="Member has been purged from staff and mod team and added to blacklist.",
                fields=embed_fields,
                footer="Staff Discharge",
            )

            staff_retire(
                member.id, RemovalType.REMOVED_BAD_STANDING, interaction.user.id, reason
            )

            if bypass_reason:
                await interaction.followup.send(embed=log_embed)

            channel = interaction.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=log_embed)

            with db_session(interaction.user) as session:
                case: BlacklistCase = BlacklistCase(
                    offender=member.id,
                    moderator=interaction.user.id,
                    blacklist="Staff",
                    reason=reason,
                )
                session.add(case)

                if confirming_moderator != interaction.user:
                    session.add(
                        CaseApproval(
                            case_id=case.id,
                            approver=confirming_moderator.id,
                            approved=True,
                        )
                    )
                session.commit()

        await execute(self.bot, self.config, interaction)

    @remove_from_staff.subcommand(
        description="Used to Retire from the staff team",
    )
    async def retire(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            required=False,
            description="Who to retire; Specify yourself to retire yourself.",
        ),
        reason: str = SlashOption(
            required=True,
            description="Reason for retiring from the staff team;",
            min_length=8,
            max_length=1024,
        ),
    ):
        if member is None:
            member = interaction.user

        if member == interaction.user:
            if not await permcheck(interaction, is_staff):
                return
        else:
            if not await permcheck(interaction, is_slt):
                return

        await interaction.response.defer()

        await self.remove_all_permission_roles(member)

        staff_retire(member, RemovalType.RETIRE, interaction.user.id, reason)

        try:
            await member.add_roles(
                interaction.guild.get_role(self.config.roles.honourable_member)
            )
        except (nextcord.Forbidden, nextcord.HTTPException, AttributeError):
            pass

        await interaction.followup.send(
            f"{self.config.emotes.success} {member.mention} has retired from the mod team. Thank you for your service!"
        )

        # logging
        log_embed: nextcord.Embed = SersiEmbed(
            title="Moderator has (been) retired.",
            fields={
                "Responsible Moderator:": interaction.user.mention,
                "Retired Moderator:": member.mention,
            },
        )

        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=log_embed
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=log_embed
        )

    @blacklist.subcommand(description="Add a user to the Staff Blacklist")
    async def add(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Who to blacklist.",
        ),
        reason: str = SlashOption(
            description="The reason you are blacklisting this user."
        ),
    ):
        if not await permcheck(interaction, is_slt):
            return

        if blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is already blacklisted from the Staff Team."
            )

        interaction.response.defer()

        with db_session(interaction.user) as session:
            case: BlacklistCase = BlacklistCase(
                offender=member.id,
                moderator=interaction.user.id,
                blacklist="Staff",
                reason=reason,
            )
            session.add(case)
            session.commit()

        interaction.followup.send(
            f"{self.config.emotes.success} The user has now been blacklisted from the Staff Team."
        )
        return

    @blacklist.subcommand(description="Remove a user to the Staff Blacklist")
    async def remove(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Who to blacklist.",
        ),
        reason: str = SlashOption(
            description="The reason you are removing this user from the blacklist."
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        if not blacklist_check(member):
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is not on the Staff Team blacklist."
            )

        interaction.response.defer()

        with db_session(interaction.user) as session:
            case: BlacklistCase = (
                session.query(BlacklistCase)
                .filter_by(offender=member.id, active=True, blacklist="Staff")
                .first()
            )
            case.active = False
            case.removed_by = interaction.user.id
            case.removal_reason = reason
            session.commit()

        interaction.followup.send(
            f"{self.config.emotes.success} The user is no longer blacklisted from the Staff Team."
        )
        return

    @staff.subcommand(
        description="Revoke a user's Honourable Member status and blacklist them from the Staff Team"
    )
    async def revoke_honoured_member(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = SlashOption(
            description="Member to revoke Honourable Member status from",
        ),
        reason: str = SlashOption(
            description="Reason for revoking Honourable Member status",
            min_length=10,
            max_length=1024,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="ADMINISTRATOR ONLY! Reason to bypass vote",
            min_length=10,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        honourable_member: nextcord.Role = interaction.guild.get_role(
            self.config.roles.honourable_member
        )

        if honourable_member not in member.roles:
            interaction.response.send_message(
                f"{self.config.emotes.fail} This user is not an Honourable Member."
            )
            return

        if blacklist_check(member):
            member.remove_roles(
                honourable_member, reason="Blacklisted from staff", atomic=True
            )
            interaction.response.send_message(
                f"{self.config.emotes.success} This user is already blacklisted from the Staff Team"
                " and has been removed from the Honourable Member role immediately."
            )
            return

        interaction.response.defer(ephemeral=True)

        if bypass_reason and permcheck(interaction, is_admin):
            await member.remove_roles(
                honourable_member, reason="Blacklisted from staff", atomic=True
            )
            interaction.followup.send(
                f"{self.config.emotes.success} {member.mention} has been removed from the Honourable Member role."
            )

            # logging
            log_embed = SersiEmbed(
                title="Honoured Member status revoked.",
                fields={
                    "Responsible Administrator:": interaction.user.mention,
                    "Removed Honoured Member:": member.mention,
                    "Reason:": reason,
                    "Bypass Reason:": bypass_reason,
                },
            ).set_author(
                name=interaction.user, icon_url=interaction.user.display_avatar.url
            )

            await interaction.guild.get_channel(self.config.channels.logging).send(
                embed=log_embed
            )
            await interaction.guild.get_channel(self.config.channels.mod_logs).send(
                embed=log_embed
            )

            return

        # start the vote to revoke honoured member role
        vote_embed = SersiEmbed(
            title=f"Revoke Honourable Member Status of {member.name}",
            description=f"{member.mention} has been nominated to have their Honourable Member status revoked. \n"
            f"__Reason stated by {interaction.user.mention}:__ \n\n{reason}",
            author=interaction.user,
        )

        vote_channel = self.config.channels.staff_votes

        vote_message = await interaction.guild.get_channel(vote_channel).send(
            embed=vote_embed
        )

        vote_type = self.config.voting["honour-revoke"]
        with db_session(interaction.user) as session:
            case: BlacklistCase = BlacklistCase(
                id=encode_snowflake(interaction.id),
                offender=member.id,
                moderator=interaction.user.id,
                active=False,
                blacklist="Staff",
                reason=reason,
                scrubbed=True,
            )
            session.add(case)

            vote: VoteDetails = VoteDetails(
                vote_type="honour-revoke",
                vote_url=vote_message.jump_url,
                case_id=case.id,
                started_by=interaction.user.id,
                planned_end=vote_planned_end(vote_type),
            )
            session.add(vote)
            session.commit()

            await vote_message.edit(view=VoteView(vote_type, vote))

        await interaction.followup.send(
            f"{self.config.emotes.success} Vote to revoke Honourable Member status has been started."
        )

    @commands.Cog.listener()
    async def on_honoured_member_revoke(self, details: VoteDetails):
        if details.outcome != "Accepted":
            return

        guild = self.bot.get_guild(self.config.guilds.main)

        with db_session(self.bot.user) as session:
            case: BlacklistCase = (
                session.query(BlacklistCase).filter_by(id=details.case_id).first()
            )
            case.active = True
            case.scrubbed = False
            session.commit()

            yes_voters = [
                guild.get_member(vote[0]).mention
                for vote in session.query(VoteRecord.voter)
                .filter_by(vote_id=details.vote_id, vote="yes")
                .all()
            ]

            member = guild.get_member(case.offender)
        honourable_member = guild.get_role(self.config.roles.honourable_member)

        await member.remove_roles(
            honourable_member, reason="Honoured member removal vote", atomic=True
        )

        # logging
        log_embed = SersiEmbed(
            title="Honoured Member status revoked.",
            description=f"{member.mention} has been removed from the Honourable Member role "
            f"due to a successful vote and blacklisted from staff.",
            fields={
                "Removed Honoured Member:": member.mention,
                "Reason:": case.reason,
                "Voters:": "- " + "\n- ".join(yes_voters),
            },
        )

        await guild.get_channel(self.config.channels.logging).send(embed=log_embed)
        await guild.get_channel(self.config.channels.mod_logs).send(embed=log_embed)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Staff(bot, kwargs["config"]))
