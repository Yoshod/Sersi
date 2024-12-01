import nextcord
from nextcord.ext import commands, application_checks
from utils.database import guild_db_manager, ModeratorRoles
from utils.sersi_embed import SersiEmbed


class Moderation_roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="moderation_roles",
        description="Moderation roles",
        guild_ids=[977377117895536640],
    )
    async def moderation_roles(self, interaction: nextcord.Interaction):
        pass

    @application_checks.has_guild_permissions(administrator=True)
    @moderation_roles.subcommand(
        name="add",
        description="Add a moderation role",
    )
    async def add(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(
            description="Role to add", required=True
        ),
        authority_level: int = nextcord.SlashOption(
            description="Authority level of the role",
            required=True,
            min_value=1,
            max_value=10,
        ),
        can_warn: bool = nextcord.SlashOption(
            description="Can issue warnings", required=True
        ),
        can_timeout: bool = nextcord.SlashOption(
            description="Can timeout users", required=True
        ),
        can_immediate_ban: bool = nextcord.SlashOption(
            description="Can ban without a vote", required=True
        ),
        can_vote_ban: bool = nextcord.SlashOption(
            description="Can trigger and vote in ban votes", required=True
        ),
        can_unban: bool = nextcord.SlashOption(
            description="Can unban users", required=True
        ),
        can_reform: bool = nextcord.SlashOption(
            description="Can reform users", required=True
        ),
        can_blacklist: bool = nextcord.SlashOption(
            description="Can blacklist users", required=True
        ),
        can_kick: bool = nextcord.SlashOption(
            description="Can kick users", required=True
        ),
        declare_raid: bool = nextcord.SlashOption(
            description="Can declare a raid", required=True
        ),
        add_moderator: bool = nextcord.SlashOption(
            description="Can add moderators", required=True
        ),
        remove_moderator: bool = nextcord.SlashOption(
            description="Can remove moderators", required=True
        ),
        is_immune: bool = nextcord.SlashOption(
            description="Is immune to moderation", required=True
        ),
        edit_offences: bool = nextcord.SlashOption(
            description="Can edit offences", required=True
        ),
        edit_cases: bool = nextcord.SlashOption(
            description="Can edit cases", required=True
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        with guild_db_manager.get_session(interaction.guild.id) as session:
            existing_role: ModeratorRoles = (
                session.query(ModeratorRoles).filter_by(role_id=role.id).first()
            )

            if existing_role:
                return await interaction.followup.send(
                    embed=SersiEmbed(
                        title="Role already exists",
                        description=f"{role.mention} is already a moderation role. Please use the edit command to modify its permissions or the remove command to remove it.",
                    ),
                    ephemeral=True,
                )

            same_auth_level = (
                session.query(ModeratorRoles)
                .filter_by(authority_level=authority_level)
                .first()
            )

            new_role = ModeratorRoles(
                role_id=role.id,
                authority_level=authority_level,
                can_warn=can_warn,
                can_timeout=can_timeout,
                can_immediate_ban=can_immediate_ban,
                can_vote_ban=can_vote_ban,
                can_unban=can_unban,
                can_reform=can_reform,
                can_blacklist=can_blacklist,
                can_kick=can_kick,
                declare_raid=declare_raid,
                add_moderator=add_moderator,
                remove_moderator=remove_moderator,
                is_immune=is_immune,
                edit_offences=edit_offences,
                edit_Cases=edit_cases,
            )

            session.add(new_role)
            session.commit()

        if same_auth_level:
            return await interaction.followup.send(
                embed=SersiEmbed(
                    title="Role added",
                    description=f"{role.mention} has been added as a moderation role with authority level {authority_level}. There is already a role with the same authority level, as such this role will not be able to issue moderation commands targeting users with the same authority level.",
                ),
                ephemeral=True,
            )

        await interaction.followup.send(
            embed=SersiEmbed(
                title="Role added",
                description=f"{role.mention} has been added as a moderation role.",
            ),
            ephemeral=True,
        )

    @application_checks.has_guild_permissions(administrator=True)
    @moderation_roles.subcommand(
        name="edit",
        description="Edit a moderation role",
    )
    async def edit(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(
            description="Role to edit", required=True
        ),
        authority_level: int = nextcord.SlashOption(
            description="Authority level of the role",
            min_value=1,
            max_value=10,
        ),
        can_warn: bool = nextcord.SlashOption(
            description="Can issue warnings",
        ),
        can_timeout: bool = nextcord.SlashOption(
            description="Can timeout users",
        ),
        can_immediate_ban: bool = nextcord.SlashOption(
            description="Can ban without a vote",
        ),
        can_vote_ban: bool = nextcord.SlashOption(
            description="Can trigger and vote in ban votes",
        ),
        can_unban: bool = nextcord.SlashOption(
            description="Can unban users",
        ),
        can_reform: bool = nextcord.SlashOption(
            description="Can reform users",
        ),
        can_blacklist: bool = nextcord.SlashOption(
            description="Can blacklist users",
        ),
        can_kick: bool = nextcord.SlashOption(
            description="Can kick users",
        ),
        declare_raid: bool = nextcord.SlashOption(
            description="Can declare a raid",
        ),
        add_moderator: bool = nextcord.SlashOption(
            description="Can add moderators",
        ),
        remove_moderator: bool = nextcord.SlashOption(
            description="Can remove moderators",
        ),
        is_immune: bool = nextcord.SlashOption(
            description="Is immune to moderation",
        ),
        edit_offences: bool = nextcord.SlashOption(
            description="Can edit offences",
        ),
        edit_cases: bool = nextcord.SlashOption(
            description="Can edit cases",
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        with guild_db_manager.get_session(interaction.guild.id) as session:
            existing_role: ModeratorRoles = (
                session.query(ModeratorRoles).filter_by(role_id=role.id).first()
            )

            if not existing_role:
                return await interaction.followup.send(
                    embed=SersiEmbed(
                        title="Role not found",
                        description=f"{role.mention} is not a moderation role. Please use the add command to add it.",
                    ),
                    ephemeral=True,
                )

            changes_made = False

            if authority_level:
                existing_role.authority_level = authority_level
                changes_made = True

            if can_warn:
                existing_role.can_warn = can_warn
                changes_made = True

            if can_timeout:
                existing_role.can_timeout = can_timeout
                changes_made = True

            if can_immediate_ban:
                existing_role.can_immediate_ban = can_immediate_ban
                changes_made = True

            if can_vote_ban:
                existing_role.can_vote_ban = can_vote_ban
                changes_made = True

            if can_unban:
                existing_role.can_unban = can_unban
                changes_made = True

            if can_reform:
                existing_role.can_reform = can_reform
                changes_made = True

            if can_blacklist:
                existing_role.can_blacklist = can_blacklist
                changes_made = True

            if can_kick:
                existing_role.can_kick = can_kick
                changes_made = True

            if declare_raid:
                existing_role.declare_raid = declare_raid
                changes_made = True

            if add_moderator:
                existing_role.add_moderator = add_moderator
                changes_made = True

            if remove_moderator:
                existing_role.remove_moderator = remove_moderator
                changes_made = True

            if is_immune:
                existing_role.is_immune = is_immune
                changes_made = True

            if edit_offences:
                existing_role.edit_offences = edit_offences
                changes_made = True

            if edit_cases:
                existing_role.edit_cases = edit_cases
                changes_made = True

            if not changes_made:
                return await interaction.followup.send(
                    embed=SersiEmbed(
                        title="No changes made",
                        description="No changes were made to the role.",
                    ),
                    ephemeral=True,
                )

            session.commit()

        await interaction.followup.send(
            embed=SersiEmbed(
                title="Role edited",
                description=f"{role.mention} has been edited.",
            ),
            ephemeral=True,
        )

    @application_checks.has_guild_permissions(administrator=True)
    @moderation_roles.subcommand(
        name="remove",
        description="Remove a moderation role",
    )
    async def remove(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(
            description="Role to remove", required=True
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        with guild_db_manager.get_session(interaction.guild.id) as session:
            existing_role: ModeratorRoles = (
                session.query(ModeratorRoles).filter_by(role_id=role.id).first()
            )

            if not existing_role:
                return await interaction.followup.send(
                    embed=SersiEmbed(
                        title="Role not found",
                        description=f"{role.mention} is not a moderation role.",
                    ),
                    ephemeral=True,
                )

            session.delete(existing_role)
            session.commit()

        await interaction.followup.send(
            embed=SersiEmbed(
                title="Role removed",
                description=f"{role.mention} has been removed as a moderation role.",
            ),
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(Moderation_roles(bot))
