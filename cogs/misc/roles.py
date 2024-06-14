from nextcord.ext import commands, tasks
from utils.base import convert_to_timedelta
from utils.config import Configuration
import datetime
import pytz
from utils.perms import is_staff, permcheck, is_admin, is_level, blacklist_check
from utils.sersi_embed import SersiEmbed
from nextcord.ui import View, Select, Button
from utils.database import db_session, StickyRoles, TemporaryRoles, IssuedTemporaryRoles
import nextcord


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
                custom_id="roles-reformist_opt_in",
            )
        )
        view.add_item(
            Button(
                style=nextcord.ButtonStyle.red,
                label="Opt Out",
                custom_id="roles-reformist_opt_out",
            )
        )

        await ctx.send(embed=reformist_embed, view=view)

    @commands.command()
    async def add_roles(self, ctx: commands.Context):
        """Single use Command for the 'Add Roles' Embed."""
        if not await permcheck(ctx, is_admin):
            return

        await ctx.message.delete()

        # This command is a work in progress and disabled for now
        if not self.config.bot.dev_mode:
            await ctx.send(
                "This command is work in progress and disabled for now.",
                delete_after=10,
            )
            return

        interests_options = [
            nextcord.SelectOption(
                label="Gaming",
                description="Access to the Gaming related channels",
                emoji="🎮",
                value="gaming",
            ),
            nextcord.SelectOption(
                label="TechCompsci",
                description="Access to the Tech and Computer Science related channels",
                emoji="🖥️",
                value="tech",
            ),
            nextcord.SelectOption(
                label="Food & Housework",
                description="Access to the Food and Housework related channels",
                emoji="🍹",
                value="food",
            ),
            nextcord.SelectOption(
                label="History",
                description="Access to the History related channels",
                emoji="🏰",
                value="history",
            ),
            nextcord.SelectOption(
                label="Art Writing & Creativity",
                description="Access to the Art, Writing, and other Creative related channels",
                emoji="🎨",
                value="art",
            ),
            nextcord.SelectOption(
                label="Anime & Manga",
                description="Access to the Anime and Manga related channels",
                emoji="🏯",
                value="anime",
            ),
            nextcord.SelectOption(
                label="Furry",
                description="Access to the Furry related channels",
                emoji="🐾",
                value="furry",
            ),
            nextcord.SelectOption(
                label="Models",
                description="Access to the Modelling related channels",
                emoji="🖌️",
                value="models",
            ),
            nextcord.SelectOption(
                label="Shillposting",
                description="Access to the Shillposting related channels",
                emoji="💸",
                value="shillposting",
            ),
            nextcord.SelectOption(
                label="Photography",
                description="Access to the Photography related channels",
                emoji="📷",
                value="photo",
            ),
            nextcord.SelectOption(
                label="Environment",
                description="Access to the Environment related channels",
                emoji="♻️",
                value="enviro",
            ),
        ]

        interests_dropdown = Select(
            options=interests_options,
            placeholder="Interests",
            custom_id="interests-selection",
        )

        # Colour Roles
        colour_options = [
            nextcord.SelectOption(
                label="Light Red",
                description="Light Red",
                value="l_red",
            ),
            nextcord.SelectOption(
                label="Red",
                description="Red",
                value="red",
            ),
            nextcord.SelectOption(
                label="Dark Red",
                description="Dark Red",
                value="d_red",
            ),
            nextcord.SelectOption(
                label="Light Orange",
                description="Light Orange",
                value="l_orange",
            ),
            nextcord.SelectOption(
                label="Orange",
                description="Orange",
                value="orange",
            ),
            nextcord.SelectOption(
                label="Dark Orange",
                description="Dark Orange",
                value="d_orange",
            ),
            nextcord.SelectOption(
                label="Light Yellow",
                description="Light Yellow",
                value="l_yellow",
            ),
            nextcord.SelectOption(
                label="Yellow",
                description="Yellow",
                value="yellow",
            ),
            nextcord.SelectOption(
                label="Dark Yellow",
                description="Dark Yellow",
                value="d_yellow",
            ),
            nextcord.SelectOption(
                label="Light Green",
                description="Light Green",
                value="l_green",
            ),
            nextcord.SelectOption(
                label="Green",
                description="Green",
                value="green",
            ),
            nextcord.SelectOption(
                label="Dark Green",
                description="Dark Green",
                value="d_green",
            ),
            nextcord.SelectOption(
                label="Light Blue",
                description="Light Blue",
                value="l_blue",
            ),
            nextcord.SelectOption(
                label="Blue",
                description="Blue",
                value="blue",
            ),
            nextcord.SelectOption(
                label="Dark Blue",
                description="Dark Blue",
                value="d_blue",
            ),
            nextcord.SelectOption(
                label="Light Purple",
                description="Light Purple",
                value="l_purple",
            ),
            nextcord.SelectOption(
                label="Purple",
                description="Purple",
                value="purple",
            ),
            nextcord.SelectOption(
                label="Dark Purple",
                description="Dark Purple",
                value="d_purple",
            ),
            nextcord.SelectOption(
                label="Light Pink",
                description="Light Pink",
                value="l_pink",
            ),
            nextcord.SelectOption(
                label="Pink",
                description="Pink",
                value="pink",
            ),
            nextcord.SelectOption(
                label="Dark Pink",
                description="Dark Pink",
                value="d_pink",
            ),
        ]

        colour_dropdown = Select(
            options=colour_options,
            placeholder="Colours",
            max_values=1,
            custom_id="colour-selection",
        )

        # Ping Roles
        ping_options = [
            nextcord.SelectOption(
                label="Server Updates",
                description="Whenever there's server changes",
                value="server_updates",
            ),
            nextcord.SelectOption(
                label="Server Events",
                description="Whenever we host events e.g. agario",
                value="server_events",
            ),
            nextcord.SelectOption(
                label="Voice Chat",
                description="Can be pinged by anyone looking to voice chat",
                value="voice_chat",
            ),
            nextcord.SelectOption(
                label="Question of The Week",
                description="Our sometimes more often than weekly question",
                value="qotw",
            ),
        ]

        ping_dropdown = Select(
            options=ping_options,
            placeholder="Notification Roles",
            custom_id="ping-selection",
        )

        pronoun_options = [
            nextcord.SelectOption(
                label="Any/All",
                value="anyall",
            ),
            nextcord.SelectOption(
                label="He/Him",
                value="hehim",
            ),
            nextcord.SelectOption(
                label="He/They",
                value="hethey",
            ),
            nextcord.SelectOption(
                label="They/Them",
                value="theythem",
            ),
            nextcord.SelectOption(
                label="She/They",
                value="shethey",
            ),
            nextcord.SelectOption(
                label="She/Her",
                value="sheher",
            ),
            nextcord.SelectOption(
                label="Ask For Pronouns",
                value="askme",
            ),
            nextcord.SelectOption(
                label="Questioning",
                value="unsure",
            ),
            nextcord.SelectOption(
                label="Nouns Only | No Pronouns",
                value="nopronouns",
            ),
        ]

        pronoun_dropdown = Select(
            options=pronoun_options,
            placeholder="Pronouns",
            max_values=1,
            custom_id="pronoun-selection",
        )

        # Gendered Terms Roles
        opt_in_embed = SersiEmbed(
            title="Pick Your Roles",
            description="You can pick a variety of roles to suit your needs!",
        )

        terms_options = [
            nextcord.SelectOption(
                label="Dude Positve",
                description="You are okay being referred to as dude",
                value="dude_positive",
            ),
            nextcord.SelectOption(
                label="Dude Negative",
                description="You are not okay being referred to as dude",
                value="dude_negative",
            ),
            nextcord.SelectOption(
                label="Guys Positive",
                description="In a group context you are okay being referred to as a guy",
                value="guys_positive",
            ),
            nextcord.SelectOption(
                label="Guys Negative",
                description="In any context you are not okay being referred to as a guy",
                value="guys_negative",
            ),
        ]

        terms_dropdown = Select(
            options=terms_options,
            placeholder="Gendered Terms Roles",
            custom_id="gendered-terms-selection",
        )

        button_view = View(auto_defer=False)
        button_view.add_item(interests_dropdown)
        button_view.add_item(colour_dropdown)
        button_view.add_item(ping_dropdown)
        button_view.add_item(pronoun_dropdown)
        button_view.add_item(terms_dropdown)

        await ctx.send(embed=opt_in_embed, view=button_view)

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
        if not interaction.data["custom_id"].startswith("roles"):
            return

        match interaction.data["custom_id"]:
            case "roles-reformist_opt_in":
                if blacklist_check(interaction.user, "Reformist"):
                    await interaction.response.send_message(
                        "You are blacklisted from the Reformist role.",
                        ephemeral=True,
                    )
                    return
                if not is_level(interaction.user, 4):
                    await interaction.response.send_message(
                        "You must be level 4 or above to be eligible for the reformist role.",
                        ephemeral=True,
                    )
                    return
                reformation_role = interaction.guild.get_role(
                    self.config.roles.reform.inmate
                )
                if reformation_role in interaction.user.roles:
                    await interaction.response.send_message(
                        "You are currently in reformation and cannot opt in to the Reformist role.",
                        ephemeral=True,
                    )
                    return

                reformist_role = interaction.guild.get_role(
                    self.config.roles.reform.reformist
                )
                await interaction.user.add_roles(
                    reformist_role,
                    reason="Reformist role self assignment",
                )
                await interaction.response.send_message(
                    "You have been given the Reformist role.",
                    ephemeral=True,
                )

            case "roles-reformist_opt_out":
                reformist_role = interaction.guild.get_role(
                    self.config.roles.reform.reformist
                )
                await interaction.user.remove_roles(
                    reformist_role,
                    reason="Reformist role self assignment",
                )
                await interaction.response.send_message(
                    "You have been removed from the Reformist role.",
                    ephemeral=True,
                )

        # try:
        #     dropdown_value = interaction.data["values"][0]
        # except KeyError:
        #     return

        # match dropdown_value:
        #     case ["gaming"]:
        #         print("identified case")
        #         print(self.config.opt_in_roles)
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["gaming"],
        #             reason="Sersi role self assignment",
        #         )
        #         print("role given")

        #     case ["tech"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["tech_compsci"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["food"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["food_and_drink"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["history"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["history"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["art"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["art"],
        #             reason="Sersi role self assignment",
        #         )
        #     case ["anime"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["anime"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["furry"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["furry"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["models"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["models"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["shillposting"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["shillposting"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["photo"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["photography"],
        #             reason="Sersi role self assignment",
        #         )

        #     case ["enviro"]:
        #         await interaction.user.add_roles(
        #             self.config.opt_in_roles["environment"],
        #             reason="Sersi role self assignment",
        #         )

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

    @give_temporary_role.on_autocomplete("role")
    async def role_autocomplete(interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_staff):
            return

        with db_session() as session:
            roles = session.query(TemporaryRoles).all()

        return [role.role_name for role in roles]

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
            role = self.bot.get_guild(self.config.guilds.main).get_role(role.role_id)

            if member is None or role is None:
                continue

            try:
                await member.remove_roles(role, reason="Temporary role expired")

            except nextcord.HTTPException:
                pass

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


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Roles(bot, kwargs["config"]))
