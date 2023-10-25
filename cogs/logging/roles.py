import nextcord


from nextcord.ext import commands
from utils.config import Configuration
from utils.perms import is_dark_mod, permcheck
from utils.sersi_embed import SersiEmbed
from nextcord.ui import View, Select


class MemberRoles(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def add_roles(self, ctx):
        """Single use Command for the 'Add Roles' Embed."""
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        interests_embed = SersiEmbed(
            title="Channel Opt-Ins",
            description="Select extra channels you wish to opt-in to seeing.",
        )

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
        )

        button_view = View(auto_defer=False)
        button_view.add_item(interests_dropdown)

        await ctx.send(embed=interests_embed, view=button_view)

        # Colour Roles
        colours_embed = SersiEmbed(
            title="Colour Roles",
            description="Select the colour you wish your username to show.",
        )

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
            options=colour_options, placeholder="Colours", max_values=1
        )

        button_view = View(auto_defer=False)
        button_view.add_item(colour_dropdown)

        await ctx.send(embed=colours_embed, view=button_view)

        # Ping Roles
        ping_embed = SersiEmbed(
            title="Notification Roles",
            description="Select the pingable roles you want.",
        )

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

        ping_dropdown = Select(options=ping_options, placeholder="Notification Roles")

        button_view = View(auto_defer=False)
        button_view.add_item(ping_dropdown)

        await ctx.send(embed=ping_embed, view=button_view)

        # Pronoun Roles
        pronouns_embed = SersiEmbed(
            title="Pronoun Roles",
            description="Select the pronouns which apply to you.",
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
            options=pronoun_options, placeholder="Pronouns", max_values=1
        )

        button_view = View(auto_defer=False)
        button_view.add_item(pronoun_dropdown)

        await ctx.send(embed=pronouns_embed, view=button_view)

        # Gendered Terms Roles
        gendered_terms_embed = SersiEmbed(
            title="Gendered Terms Roles",
            description="Select the gendered terms you are comfortable or not comfortable with.",
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
            options=terms_options, placeholder="Gendered Terms Roles"
        )

        button_view = View(auto_defer=False)
        button_view.add_item(terms_dropdown)

        await ctx.send(embed=gendered_terms_embed, view=button_view)

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: nextcord.Role):
        log: nextcord.AuditLogEntry = (
            await role.guild.audit_logs(
                action=nextcord.AuditLogAction.role_create, limit=1
            ).flatten()
        )[0]

        role_permissions: str = ""
        for permission, value in role.permissions:
            if value:
                role_permissions += f"{self.config.emotes.success} `{permission}`\n"

        await role.guild.get_channel(self.config.channels.role_logs).send(
            embed=SersiEmbed(
                description="A role was created",
                fields={
                    "Name": f"{role.mention} {role.name}",
                    "Colour": f"`{role.colour}`",
                    "Mentionable": role.mentionable,
                    "Hoist": role.hoist,
                    "Permissions": role_permissions,
                    "IDs": f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```",
                },
                colour=role.colour,
                footer="Sersi Role Logging",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: nextcord.Role):
        log: nextcord.AuditLogEntry = (
            await role.guild.audit_logs(
                action=nextcord.AuditLogAction.role_delete, limit=1
            ).flatten()
        )[0]

        role_permissions: str = ""
        for permission, value in role.permissions:
            if value:
                role_permissions += f"{self.config.emotes.success} `{permission}`\n"

        await role.guild.get_channel(self.config.channels.role_logs).send(
            embed=SersiEmbed(
                description="A role was deleted",
                fields={
                    "Name": f"{role.name}",
                    "Colour": f"`{role.colour}`",
                    "Mentionable": role.mentionable,
                    "Hoist": role.hoist,
                    "Permissions": role_permissions,
                    "IDs": f"```ini\nRole = {role.id}\nPerpetrator = {log.user.id}```",
                },
                colour=role.colour,
                footer="Sersi Role Logging",
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)
        )

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: nextcord.Role, after: nextcord.Role):
        log: nextcord.AuditLogEntry = (
            await after.guild.audit_logs(
                action=nextcord.AuditLogAction.role_update, limit=1
            ).flatten()
        )[0]

        logging_embed: nextcord.Embed = SersiEmbed(
            description=f"Role {after.mention} {after.name} was updated",
            colour=after.colour
            if int(after.colour) != 0
            else nextcord.Color.from_rgb(237, 91, 6),
            footer="Sersi Role Logging",
        )

        if before.permissions != after.permissions:
            before_permissions: str = ""
            after_permissions: str = ""
            for before_permission, before_value in before.permissions:
                for after_permission, after_value in after.permissions:
                    if (
                        before_permission == after_permission
                        and before_value != after_value
                    ):
                        match before_value:
                            case True:
                                before_permissions += f"{self.config.emotes.success} `{before_permission}`\n"
                            case False:
                                before_permissions += (
                                    f"{self.config.emotes.fail} `{before_permission}`\n"
                                )

                        match after_value:
                            case True:
                                after_permissions += f"{self.config.emotes.success} `{after_permission}`\n"
                            case False:
                                after_permissions += (
                                    f"{self.config.emotes.fail} `{after_permission}`\n"
                                )

            logging_embed.add_field(
                name="Permissions Changed",
                value=f"Before:\n{before_permissions}\nAfter:\n{after_permissions}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.colour != after.colour:
            logging_embed.add_field(
                name="Colour",
                value=f"Before:\n{before.colour}\nAfter:\n{after.colour}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.mentionable != after.mentionable:
            logging_embed.add_field(
                name="Mentionable",
                value=f"Before:\n{before.mentionable}\nAfter:\n{after.mentionable}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.hoist != after.hoist:
            logging_embed.add_field(
                name="Hoist",
                value=f"Before:\n{before.hoist}\nAfter:\n{after.hoist}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if before.name != after.name:
            logging_embed.add_field(
                name="Name",
                value=f"Before:\n{before.name}\nAfter:\n{after.name}",
                inline=False,
            ).set_author(name=log.user, icon_url=log.user.display_avatar.url)

        if logging_embed.fields:
            await after.guild.get_channel(self.config.channels.role_logs).send(
                embed=logging_embed
            )


def setup(bot, **kwargs):
    bot.add_cog(MemberRoles(bot, kwargs["config"]))
