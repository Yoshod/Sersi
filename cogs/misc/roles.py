from nextcord.ext import commands, tasks
from utils.base import convert_to_timedelta, decode_button_id, encode_button_id
from utils.config import Configuration
import datetime
import pytz
from utils.embeds import fetch_all_temporary_roles, fetch_all_issued_temporary_roles
from utils.perms import is_staff, permcheck, is_admin, is_level, blacklist_check
from utils.sersi_embed import SersiEmbed
from nextcord.ui import View, Select, Button
from utils.database import (
    db_session,
    StickyRoles,
    TemporaryRoles,
    IssuedTemporaryRoles,
    OptInCategories,
    OptInRoles,
)
import nextcord

from utils.views import PageView


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        if self.bot.is_ready():
            self.sticky_roles_cleanup.start()
            self.temporary_role_removal.start()

    def cog_unload(self):
        self.sticky_roles_cleanup.cancel()
        self.temporary_role_removal.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.sticky_roles_cleanup.start()
        self.temporary_role_removal.start()

    @commands.command()
    async def reformist_opt_in(self, ctx: commands.Context):
        """Embed for the Reformist role opt-in in reformation information."""
        if not await permcheck(ctx, is_admin):
            return

        await ctx.message.delete()

        reformist_embed = SersiEmbed(
            title="Reformist Role",
            description="This role is for people who are interested in helping to "
            "reform members who have been sent to the reformation centre by the "
            "moderation team. If you would like to opt in to this role, please click"
            'the "Opt In" button below. You will be pinged whenever a member is sent '
            "to the reformation centre. You can opt out at any time by clicking the "
            '"Opt Out" button below.',
            thumbnail_url=ctx.guild.icon.url,
        )
        view = View(auto_defer=False)
        view.add_item(
            Button(
                style=nextcord.ButtonStyle.green,
                label="Opt In",
                custom_id=encode_button_id(
                    "roles", role_id=self.config.roles.reform, required_level=3
                ),
            )
        )
        view.add_item(
            Button(
                style=nextcord.ButtonStyle.red,
                label="Opt Out",
                custom_id=encode_button_id(
                    "roles", role_id=self.config.roles.reform, required_level=3
                ),
            )
        )

        await ctx.send(embed=reformist_embed, view=view)

    @commands.command()
    async def add_roles(self, ctx: commands.Context):
        """Single use Command for the 'Add Roles' Embed."""
        if not await permcheck(ctx, is_admin):
            return

        await ctx.message.delete()

        with db_session() as session:
            categories = session.query(OptInCategories).all()

            opt_in_roles = session.query(OptInRoles).all()

        for category in categories:
            category_roles = [
                role
                for role in opt_in_roles
                if role.role_category == category.category_name
            ]

            embed = SersiEmbed(
                title=f"{category.category_name} Roles",
                description=category.category_description,
                thumbnail_url=ctx.guild.icon.url,
            )

            view = View(auto_defer=False)
            for role in category_roles:  # Filthy code
                try:
                    view.add_item(
                        Button(
                            style=nextcord.ButtonStyle.blurple,
                            label=role.role_name,
                            emoji=(
                                role.role_emoji
                                if not role.role_emoji.isdigit()
                                else None
                            ),
                            custom_id=encode_button_id(
                                "roles",
                                role_id=role.role_id,
                                required_level=role.required_level_role,
                            ),
                        )
                    )

                except AttributeError:
                    view.add_item(
                        Button(
                            style=nextcord.ButtonStyle.blurple,
                            label=role.role_name,
                            custom_id=encode_button_id(
                                "roles",
                                role_id=role.role_id,
                                required_level=role.required_level_role,
                            ),
                        )
                    )

            await ctx.send(
                embed=embed,
                view=view,
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        if member.bot:  # do not apply newbie role do bots
            return

        with db_session() as session:
            sticky_roles = session.query(StickyRoles).filter_by(user_id=member.id).all()

            if not sticky_roles:
                newbie_role = member.guild.get_role(self.config.roles.access.newbie)
                await member.add_roles(newbie_role)
                return

            for sticky_role in sticky_roles:
                role = member.guild.get_role(sticky_role.role_id)
                if role is not None:
                    await member.add_roles(role)

            session.query(StickyRoles).filter_by(user_id=member.id).delete()
            session.commit()

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:  # ignores message if message is by bot
            return

        if message.guild is None:  # ignores if message is a DM
            return

        newbie_role = message.guild.get_role(self.config.roles.access.newbie)

        if newbie_role in message.author.roles:
            now = datetime.datetime.now()
            aware_now = now.replace(tzinfo=pytz.UTC)
            time_passed = aware_now - message.author.joined_at

            if time_passed.days > 3:
                await message.author.remove_roles(newbie_role)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        acceptable_starts = ["roles"]
        if not interaction.data["custom_id"].startswith(tuple(acceptable_starts)):
            return

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        await interaction.response.defer(ephemeral=True)

        if action == "roles":
            role_id = kwargs["role_id"]

            print(role_id)

            role = interaction.guild.get_role(int(role_id))

            print(role.id)
            print(role.name)

            if role is None:
                raise Exception("Role not found.")

            member = interaction.guild.get_member(interaction.user.id)

            if role in member.roles:
                await member.remove_roles(role)
                await interaction.followup.send(
                    f"{self.config.emotes.success} {role.mention} has been removed.",
                    ephemeral=True,
                )
                return

            if kwargs["role_id"] == self.config.roles.reform:
                if not await blacklist_check(member):
                    await interaction.followup.send(
                        f"{self.config.emotes.fail} You are not blacklisted and cannot opt in to the Reformist role.",
                        ephemeral=True,
                    )
                    return

            try:
                if int(kwargs["required_level"]) > 0:
                    if is_level(member, int(kwargs["required_level"])):
                        await member.add_roles(role)
                        await interaction.followup.send(
                            f"{self.config.emotes.success} {role.mention} has been added.",
                            ephemeral=True,
                        )
                        return

                    await interaction.followup.send(
                        f"{self.config.emotes.fail} You do not have the required level to add this role. You must be at least level {kwargs['required_level']}.",
                        ephemeral=True,
                    )
                    return
            except ValueError:
                pass

            await member.add_roles(role)
            await interaction.followup.send(
                f"{self.config.emotes.success} {role.mention} has been added.",
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        if member.bot:
            return

        if await permcheck(member, is_staff):
            return

        with db_session() as session:
            counter = 0
            for role in member.roles:
                if counter == 0:
                    counter += 1
                    continue

                sticky_role = StickyRoles(
                    role_id=role.id,
                    user_id=member.id,
                )
                session.add(sticky_role)

            session.commit()

    @tasks.loop(hours=24)
    async def sticky_roles_cleanup(self):
        twenty_eight_days_ago = datetime.datetime.now() - datetime.timedelta(days=28)
        twenty_eight_days_ago = twenty_eight_days_ago.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        with db_session() as session:
            session.query(StickyRoles).filter(
                StickyRoles.leave_date >= twenty_eight_days_ago
            ).delete()

    @nextcord.slash_command(
        name="roles",
        description="Role commands",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def roles(self, interaction: nextcord.Interaction):
        pass

    @roles.subcommand(
        name="give_temporary_role",
        description="Give a user a temporary role",
    )
    async def give_temporary_role(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        role: nextcord.Role,
        duration: int = nextcord.SlashOption(
            name="duration",
            description="The length of time the user should receive the role",
            min_value=1,
            max_value=10080,
            required=True,
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
            required=True,
        ),
        reason: str = nextcord.SlashOption(
            name="reason",
            description="The reason for giving the role",
            required=True,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            role_exists = (
                session.query(TemporaryRoles).filter_by(role_id=role.id).first()
            )

        if not role_exists:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The role you have provided is not a temporary role.",
                ephemeral=True,
            )
            return

        if role in member.roles:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The user already has the role you are trying to assign.",
                ephemeral=True,
            )
            return

        role_expiration: datetime.timedelta = convert_to_timedelta(timespan, duration)

        role_expiration_hours = role_expiration.total_seconds() / 3600

        if role_expiration_hours > 672:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The maximum duration for a temporary role is 28 days.",
                ephemeral=True,
            )
            return

        if role_expiration_hours < 0.25:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The minimum duration for a temporary role is 15 minutes.",
                ephemeral=True,
            )
            return

        role_expiration = datetime.datetime.now() + role_expiration

        role: nextcord.Role = interaction.guild.get_role(role_exists.role_id)

        with db_session() as session:
            issued_role = IssuedTemporaryRoles(
                role_id=role.id,
                user_id=member.id,
                expiry_date=role_expiration,
                added_by=interaction.user.id,
                reason=reason,
            )
            session.add(issued_role)
            session.commit()

        await member.add_roles(
            role, reason=f"Temporary role added by {interaction.user.name}"
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} The role has been added to the user.",
            ephemeral=True,
        )

    @roles.subcommand(
        name="remove_temporary_role",
        description="Remove a user's temporary role",
    )
    async def remove_temporary_role(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        role: nextcord.Role,
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            issued_role = (
                session.query(IssuedTemporaryRoles)
                .filter_by(user_id=member.id, role_id=role.id)
                .first()
            )

            if issued_role is None:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The user does not have the role you are trying to remove or it is not a temporary role.",
                    ephemeral=True,
                )
                return

            session.delete(issued_role)
            session.commit()

        await member.remove_roles(
            role, reason=f"Temporary role removed by {interaction.user.name}"
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} The role has been removed from the user.",
            ephemeral=True,
        )

    @tasks.loop(minutes=1)
    async def temporary_role_removal(self):
        with db_session() as session:
            roles = session.query(IssuedTemporaryRoles).all()

        for role in roles:
            if role.expiry_date > datetime.datetime.now():
                continue

            member = self.bot.get_guild(self.config.guilds.main).get_member(
                role.user_id
            )
            discord_role = self.bot.get_guild(self.config.guilds.main).get_role(
                role.role_id
            )

            if member is None or discord_role is None:
                continue

            try:
                await member.remove_roles(discord_role, reason="Temporary role expired")

            except nextcord.HTTPException:
                pass

            with db_session() as session:
                session.delete(role)
                session.commit()

    @roles.subcommand(
        name="create_temporary_role",
        description="Create a temporary role",
    )
    async def create_temporary_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role,
        description: str = nextcord.SlashOption(
            description="The description of the role",
            required=True,
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            role_exists = (
                session.query(TemporaryRoles).filter_by(role_id=role.id).first()
            )

        if role_exists:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The role you have provided already exists as a temporary role.",
                ephemeral=True,
            )
            return

        forbidden_permissions = [
            "administrator",
            "manage_guild",
            "manage_roles",
            "manage_channels",
            "manage_messages",
            "manage_webhooks",
            "manage_emojis",
            "manage_nicknames",
            "manage_threads",
            "moderate_members",
            "ban_members",
            "kick_members",
            "view_audit_log",
            "view_guild_insights",
            "send_tts_messages",
            "priority_speaker",
            "create_private_threads",
            "create_instant_invite",
            "create_public_threads",
            "move_members",
            "mute_members",
            "deafen_members",
        ]

        has_permissions = any(
            getattr(role.permissions, permission)
            for permission in forbidden_permissions
        )

        if has_permissions:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The role you have provided has forbidden permissions.",
                ephemeral=True,
            )
            return

        with db_session() as session:
            temporary_role = TemporaryRoles(
                role_id=role.id,
                role_name=role.name,
                role_description=description,
            )
            session.add(temporary_role)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} The role has been added as a temporary role.",
            ephemeral=True,
        )

    @roles.subcommand(
        name="unmake_temporary_role",
        description="Remove a temporary role",
    )
    async def unmake_temporary_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role,
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            role_exists = (
                session.query(TemporaryRoles).filter_by(role_id=role.id).first()
            )

            if role_exists is None:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The role you have provided does not exist as a temporary role.",
                    ephemeral=True,
                )
                return

            session.delete(role_exists)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} The role has been removed as a temporary role.",
            ephemeral=True,
        )

    @roles.subcommand(
        name="list_temporary_roles",
        description="List all temporary roles",
    )
    async def list_temporary_roles(
        self,
        interaction: nextcord.Interaction,
        page: int = nextcord.SlashOption(
            description="The page number to view",
            required=False,
            default=1,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        autoposts_embed = SersiEmbed(
            title=f"{interaction.guild.name} Temporary Roles",
            description=f"Temporary Roles for {interaction.guild.name}",
        )

        view = PageView(
            config=self.config,
            base_embed=autoposts_embed,
            fetch_function=fetch_all_temporary_roles,
            author=interaction.user,
            entry_form="{entry}",
            field_title="{entries[0].list_entry_header}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
        )

        await view.send_followup(interaction)

    @roles.subcommand(
        name="list_issued_temporary_roles",
        description="List all issued temporary roles",
    )
    async def list_issued_temporary_roles(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role = nextcord.SlashOption(
            description="The role to view",
            required=False,
        ),
        issued_to: nextcord.Member = nextcord.SlashOption(
            description="The member who was issued the role",
            required=False,
        ),
        issued_by: nextcord.Member = nextcord.SlashOption(
            description="The member who issued the role",
            required=False,
        ),
        page: int = nextcord.SlashOption(
            description="The page number to view",
            required=False,
            default=1,
        ),
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        autoposts_embed = SersiEmbed(
            title=f"{interaction.guild.name} Issued Temporary Roles",
            description=f"Issued Temporary Roles for {interaction.guild.name}",
        )

        view = PageView(
            config=self.config,
            base_embed=autoposts_embed,
            fetch_function=fetch_all_issued_temporary_roles,
            author=interaction.user,
            entry_form="{entry}",
            field_title="{entries[0].list_entry_header}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=int(page),
            role=role if role else None,
            issued_to=issued_to if issued_to else None,
            issued_by=issued_by if issued_by else None,
        )

        await view.send_followup(interaction)

    @roles.subcommand(
        name="add_opt_in",
        description="Make a role opt-in",
    )
    async def add_opt_in(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role,
        category: str = nextcord.SlashOption(
            description="The category of the role",
            required=True,
        ),
        required_level: int = nextcord.SlashOption(
            description="The required level to opt-in to the role",
            required=False,
            min_value=1,
        ),
        emoji: str = nextcord.SlashOption(
            description="The emoji to use for the role",
            required=False,
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            category_exists = (
                session.query(OptInCategories).filter_by(category_name=category).first()
            )

        if category_exists is None:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The category you have provided does not exist.",
                ephemeral=True,
            )
            return

        forbidden_permissions = [
            "administrator",
            "manage_guild",
            "manage_roles",
            "manage_channels",
            "manage_messages",
            "manage_webhooks",
            "manage_emojis",
            "manage_nicknames",
            "manage_threads",
            "moderate_members",
            "ban_members",
            "kick_members",
            "view_audit_log",
            "view_guild_insights",
            "send_tts_messages",
            "priority_speaker",
            "create_private_threads",
            "create_instant_invite",
            "create_public_threads",
            "move_members",
            "mute_members",
            "deafen_members",
        ]

        has_permissions = any(
            getattr(role.permissions, permission)
            for permission in forbidden_permissions
        )

        if has_permissions:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The role you have provided has forbidden permissions.",
                ephemeral=True,
            )
            return

        with db_session() as session:
            opt_in_role = OptInRoles(
                role_id=role.id,
                role_name=role.name,
                role_category=category,
                role_emoji=emoji if emoji else None,
                required_level_role=required_level if required_level else None,
            )
            session.add(opt_in_role)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} The role has been added as an opt-in role.",
            ephemeral=True,
        )

    @add_opt_in.on_autocomplete("category")
    async def autocomplete_category(
        self, interaction: nextcord.Interaction, category: str
    ):
        with db_session() as session:
            categories: list[OptInCategories] = (
                session.query(OptInCategories)
                .filter(OptInCategories.category_name.ilike(f"%{category}%"))
                .group_by(OptInCategories.category_name)
                .limit(25)
                .all()
            )

        return [category.category_name for category in categories]

    @roles.subcommand(
        name="remove_opt_in",
        description="Remove a role opt-in",
    )
    async def remove_opt_in(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role,
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            role_exists = session.query(OptInRoles).filter_by(role_id=role.id).first()

            if role_exists is None:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The role you have provided does not exist as an opt-in role.",
                    ephemeral=True,
                )
                return

            session.delete(role_exists)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} The role has been removed as an opt-in role.",
            ephemeral=True,
        )

    @roles.subcommand(
        name="add_category",
        description="Add a category for role opt-ins",
    )
    async def add_category(
        self,
        interaction: nextcord.Interaction,
        category: str,
        description: str,
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            category_exists = (
                session.query(OptInCategories).filter_by(category_name=category).first()
            )

        if category_exists:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The category you have provided already exists.",
                ephemeral=True,
            )
            return

        with db_session() as session:
            opt_in_category = OptInCategories(
                category_name=category,
                category_description=description,
            )
            session.add(opt_in_category)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} The category has been added.",
            ephemeral=True,
        )

    @roles.subcommand(
        name="remove_category",
        description="Remove a category for role opt-ins",
    )
    async def remove_category(
        self,
        interaction: nextcord.Interaction,
        category: str,
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            category_exists = (
                session.query(OptInCategories).filter_by(category_name=category).first()
            )

            if category_exists is None:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The category you have provided does not exist.",
                    ephemeral=True,
                )
                return

            roles_in_category = (
                session.query(OptInRoles).filter_by(role_category=category).all()
            )

            if roles_in_category:
                await interaction.followup.send(
                    f"{self.config.emotes.fail} The category you have provided has roles in it. Please remove the roles before removing the category.",
                    ephemeral=True,
                )
                return

            session.delete(category_exists)
            session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} The category has been removed.",
            ephemeral=True,
        )

    @roles.subcommand(
        name="edit_role",
        description="Edit a role",
    )
    async def edit_opt_in_role(
        self,
        interaction: nextcord.Interaction,
        role: nextcord.Role,
        category: str = nextcord.SlashOption(
            description="The category of the role",
            required=False,
        ),
        emoji: str = nextcord.SlashOption(
            description="The emoji to use for the role",
            required=False,
        ),
        required_level: int = nextcord.SlashOption(
            description="The required level to opt-in to the role",
            required=False,
            min_value=0,
        ),
    ):
        if not await permcheck(interaction, is_admin):
            return

        await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            role_exists = session.query(OptInRoles).filter_by(role_id=role.id).first()

        if role_exists is None:
            await interaction.followup.send(
                f"{self.config.emotes.fail} The role you have provided does not exist as an opt-in role.",
                ephemeral=True,
            )
            return

        if category:
            role_exists.role_category = category

        if emoji:
            role_exists.role_emoji = emoji

        if required_level:
            role_exists.required_level_role = (
                required_level if required_level > 0 else None
            )

        session.commit()

        await interaction.followup.send(
            f"{self.config.emotes.success} The role has been edited.",
            ephemeral=True,
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Roles(bot, kwargs["config"]))
