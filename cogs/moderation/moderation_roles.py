import nextcord
from nextcord.ext import commands, application_checks
from utils.database import SessionLocal, ModeratorRoles
from utils.sersi_embed import SersiEmbed
from utils.language import lang_manager
from utils.modules import check_module_enabled
from utils.logging import create_log


class Moderation_roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="moderation_roles",
        description="Moderation roles",
        guild_ids=[977377117895536640, 1166770860787515422, 1383162647171567626],
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

        if not check_module_enabled(interaction.guild.id, "moderation"):
            return await interaction.followup.send(
                embed=SersiEmbed(
                    title=lang_manager.get_string(
                        interaction.guild.id, "module_disabled.title"
                    ),
                    description=lang_manager.get_string(
                        interaction.guild.id,
                        "module_disabled.description",
                        module_name="Moderation",
                    ),
                ),
                ephemeral=True,
            )

        with SessionLocal() as session:
            existing_role: ModeratorRoles = (
                session.query(ModeratorRoles)
                .filter_by(role_id=role.id, guild_id=interaction.guild.id)
                .first()
            )

            if existing_role:
                return await interaction.followup.send(
                    embed=SersiEmbed(
                        title=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.add.already_exists_title",
                        ),
                        description=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.add.already_exists_description",
                            role_mention=role.mention,
                        ),
                    ),
                    ephemeral=True,
                )

            same_auth_level = (
                session.query(ModeratorRoles)
                .filter_by(
                    authority_level=authority_level, guild_id=interaction.guild.id
                )
                .first()
            )

            new_role = ModeratorRoles(
                guild_id=interaction.guild.id,
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
                edit_cases=edit_cases,
            )

            session.add(new_role)
            session.commit()

        if same_auth_level:
            embed_text = lang_manager.get_string(
                interaction.guild.id,
                "moderation_roles.add.description_warning",
                role_mention=role.mention,
                authority_level=authority_level,
            )
        else:
            embed_text = lang_manager.get_string(
                interaction.guild.id,
                "moderation_roles.add.description",
                role_mention=role.mention,
            )

        embed = SersiEmbed(
            title=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.title"
            ),
            description=embed_text,
        )

        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.permissions.name"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.permissions.value"
            ),
            inline=False,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.authority_level"
            ),
            value=str(authority_level),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.warn"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_warn else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.timeout"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_timeout else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.immediate_ban"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_immediate_ban else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.vote_ban"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_vote_ban else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.unban"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_unban else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.reform"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_reform else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.blacklist"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_blacklist else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.kick"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if can_kick else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.declare_raid"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if declare_raid else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.add_moderator"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if add_moderator else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.remove_moderator"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if remove_moderator else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.immune"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if is_immune else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.edit_offences"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if edit_offences else "no"
            ),
            inline=True,
        )
        embed.add_field(
            name=lang_manager.get_string(
                interaction.guild.id, "moderation_roles.add.fields.edit_cases"
            ),
            value=lang_manager.get_string(
                interaction.guild.id, "yes" if edit_cases else "no"
            ),
            inline=True,
        )

        await interaction.followup.send(
            embed=embed,
            ephemeral=True,
        )

        await create_log(
            interaction.guild,
            "moderation_role_add",
            "moderation",
            embed=embed,
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
            required=False,
        ),
        can_warn: bool = nextcord.SlashOption(
            description="Can issue warnings",
            required=False,
        ),
        can_timeout: bool = nextcord.SlashOption(
            description="Can timeout users",
            required=False,
        ),
        can_immediate_ban: bool = nextcord.SlashOption(
            description="Can ban without a vote",
            required=False,
        ),
        can_vote_ban: bool = nextcord.SlashOption(
            description="Can trigger and vote in ban votes",
            required=False,
        ),
        can_unban: bool = nextcord.SlashOption(
            description="Can unban users",
            required=False,
        ),
        can_reform: bool = nextcord.SlashOption(
            description="Can reform users",
            required=False,
        ),
        can_blacklist: bool = nextcord.SlashOption(
            description="Can blacklist users",
            required=False,
        ),
        can_kick: bool = nextcord.SlashOption(
            description="Can kick users",
            required=False,
        ),
        declare_raid: bool = nextcord.SlashOption(
            description="Can declare a raid",
            required=False,
        ),
        add_moderator: bool = nextcord.SlashOption(
            description="Can add moderators",
            required=False,
        ),
        remove_moderator: bool = nextcord.SlashOption(
            description="Can remove moderators",
            required=False,
        ),
        is_immune: bool = nextcord.SlashOption(
            description="Is immune to moderation",
            required=False,
        ),
        edit_offences: bool = nextcord.SlashOption(
            description="Can edit offences",
            required=False,
        ),
        edit_cases: bool = nextcord.SlashOption(
            description="Can edit cases",
            required=False,
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        with SessionLocal() as session:
            existing_role: ModeratorRoles = (
                session.query(ModeratorRoles)
                .filter_by(role_id=role.id, guild_id=interaction.guild.id)
                .first()
            )

            if not existing_role:
                return await interaction.followup.send(
                    embed=SersiEmbed(
                        title=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.edit.not_found.title",
                        ),
                        description=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.edit.not_found.description",
                            role_mention=role.mention,
                        ),
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
                        title=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.edit.no_changes.title",
                        ),
                        description=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.edit.no_changes.description",
                        ),
                    ),
                    ephemeral=True,
                )

            session.commit()

        await interaction.followup.send(
            embed=SersiEmbed(
                title=lang_manager.get_string(
                    interaction.guild.id, "moderation_roles.edit.success.title"
                ),
                description=lang_manager.get_string(
                    interaction.guild.id,
                    "moderation_roles.edit.success.description",
                    role_mention=role.mention,
                ),
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

        with SessionLocal() as session:
            existing_role: ModeratorRoles = (
                session.query(ModeratorRoles)
                .filter_by(role_id=role.id, guild_id=interaction.guild.id)
                .first()
            )

            if not existing_role:
                return await interaction.followup.send(
                    embed=SersiEmbed(
                        title=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.remove.not_found.title",
                        ),
                        description=lang_manager.get_string(
                            interaction.guild.id,
                            "moderation_roles.remove.not_found.description",
                            role_mention=role.mention,
                        ),
                    ),
                    ephemeral=True,
                )

            session.delete(existing_role)
            session.commit()

        await interaction.followup.send(
            embed=SersiEmbed(
                title=lang_manager.get_string(
                    interaction.guild.id, "moderation_roles.remove.success.title"
                ),
                description=lang_manager.get_string(
                    interaction.guild.id,
                    "moderation_roles.remove.success.description",
                    role_mention=role.mention,
                ),
            ),
            ephemeral=True,
        )


def setup(bot: commands.Bot):
    bot.add_cog(Moderation_roles(bot))
