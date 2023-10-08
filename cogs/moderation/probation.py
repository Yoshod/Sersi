import nextcord
from nextcord.ext import commands

from utils.base import ConfirmView, DualCustodyView
from utils.database import db_session, ProbationCase, CaseApproval
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.perms import permcheck, is_mod, is_full_mod, is_dark_mod


class Probation(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
    )
    async def probation(self, interaction: nextcord.Interaction):
        pass

    @probation.subcommand(
        description="Puts a member into probation",
    )
    async def add(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to put into probation", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for putting member into probation",
            required=True,
            min_length=8,
            max_length=1024,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="(Mega Administrator only!) Reason to bypass dual custody",
            min_length=8,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        probation_role = interaction.guild.get_role(self.config.roles.probation)

        if probation_role in member.roles:
            await interaction.send(
                f"{self.sersifail} member is already in probation", ephemeral=True
            )
            return

        await interaction.response.defer()

        @ConfirmView.query(
            title="Add Member to probation",
            prompt="Following member will be given probation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            },
        )
        @DualCustodyView.query(
            title="Add Member to probation",
            prompt="Following member will be given probation:",
            perms=is_full_mod,
            embed_args={
                "User": member.mention,
                "Reason": reason,
                "Moderator": interaction.user.mention,
            },
            bypass=True if bypass_reason else False,
        )
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            await member.add_roles(probation_role, reason=reason, atomic=True)
            case = ProbationCase(
                offender=member.id,
                moderator=interaction.user.id,
                reason=reason,
            )
            with db_session(interaction.user) as session:
                session.add(case)
                session.add(
                    CaseApproval(
                        case_id=case.id,
                        action="Add",
                        approval_type="Bypassed" if bypass_reason else "Dual Custody",
                        approver=confirming_moderator.id,
                        comment=bypass_reason,
                    )
                )
                session.commit()

            embed_fields = {
                "User": member.mention,
                "Reason": reason,
                "Resposible Moderator": interaction.user.mention,
            }

            if bypass_reason and is_dark_mod(interaction.user):
                embed_fields["Bypass Reason"] = bypass_reason
            else:
                embed_fields["Confirming Moderator"] = confirming_moderator.mention

            log_embed = SersiEmbed(
                title="Member put into Probation",
                fields=embed_fields,
            )

            log_channel = interaction.guild.get_channel(self.config.channels.logging)
            await log_channel.send(embed=log_embed)

            log_channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await log_channel.send(embed=log_embed)

            if bypass_reason:
                await interaction.followup.send(embed=log_embed)

            dm_embed = SersiEmbed(
                title="Adam Something Central Probation",
                description="Your behaviour on Adam Something Central has resulted in being put into probation by a "
                "moderator, continued rule breaking may result in a ban",
                colour=nextcord.Colour.brand_red(),
                fields={"Reason specified by moderator:": reason},
            )
            await member.send(embed=dm_embed)

            return SersiEmbed(
                title="Member in Probation",
                description=f"{member.mention} has been put into probation, continued rule breaking may result in a ban",
                fields={
                    "User": member.mention,
                    "Reason": reason,
                    "Moderator": interaction.user.mention,
                },
            )

        await execute(self.bot, self.config, interaction)

    @probation.subcommand(
        description="Removes a member from probation",
    )
    async def remove(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to remove from probation", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for removing member from probation",
            required=True,
            min_length=8,
            max_length=1024,
        ),
        bypass_reason: str = nextcord.SlashOption(
            description="(Mega Administrator only!) Reason to bypass dual custody",
            min_length=8,
            max_length=1024,
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        probation_role: nextcord.Role = interaction.guild.get_role(
            self.config.roles.probation
        )

        if probation_role not in member.roles:
            await interaction.send(
                "Error: cannot remove user from probation, member is currently not in probation"
            )
            return

        await interaction.response.defer()

        @ConfirmView.query(
            title="Remove Member from probation",
            prompt="Following member will be removed from probation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            },
        )
        @DualCustodyView.query(
            title="Remove Member from probation",
            prompt="Following member will be removed from probation:",
            perms=is_full_mod,
            embed_args={
                "User": member.mention,
                "Reason": reason,
                "Moderator": interaction.user.mention,
            },
            bypass=True if bypass_reason else False,
        )
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            await member.remove_roles(probation_role, reason=reason, atomic=True)

            with db_session(interaction.user) as session:
                case: ProbationCase = (
                    session.query(ProbationCase)
                    .filter_by(offender=member.id, active=True)
                    .first()
                )
                case.active = False
                case.removal_reason = reason
                session.add(
                    CaseApproval(
                        case_id=case.id,
                        action="Remove",
                        approval_type="Bypassed" if bypass_reason else "Dual Custody",
                        approver=confirming_moderator.id,
                        comment=bypass_reason,
                    )
                )
                session.commit()

            embed_fields = {
                "User": member.mention,
                "Reason": reason,
                "Resposible Moderator": interaction.user.mention,
            }

            if bypass_reason and is_dark_mod(interaction.user):
                embed_fields["Bypass Reason"] = bypass_reason
            else:
                embed_fields["Confirming Moderator"] = confirming_moderator.mention

            log_embed = SersiEmbed(
                title="Member removed from Probation",
                fields=embed_fields,
            )

            log_channel = interaction.guild.get_channel(self.config.channels.logging)
            await log_channel.send(embed=log_embed)

            log_channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await log_channel.send(embed=log_embed)

            if bypass_reason:
                await interaction.followup.send(embed=log_embed)

            dm_embed = SersiEmbed(
                title="Adam Something Central Probation Over",
                description="You were removed from probation on Adam Something Central",
                colour=nextcord.Colour.brand_red(),
                fields={"Reason specified by moderator:": reason},
            )
            await member.send(embed=dm_embed)

            return SersiEmbed(
                title="Member removed from Probation",
                description=f"{member.mention} was successfully removed from probation!",
                fields={
                    "User": member.mention,
                    "Reason": reason,
                    "Moderator": interaction.user.mention,
                },
            )

        await execute(self.bot, self.config, interaction)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Probation(bot, kwargs["config"]))
