import os
import nextcord

from utils.base import encode_button_id, encode_snowflake, decode_snowflake
from utils.config import Configuration
from utils.sersi_embed import SersiEmbed


parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config_path = os.path.join(parent_dir, "persistent_data/config.yaml")

CONFIG = Configuration.from_yaml_file(config_path)


class HelpCommunityButton(nextcord.ui.Button):
    def __init__(
        self,
        currently_selected: bool = False,
        embed_message_id: int | None = None,
        author_id: int = 0,
        preferred_view: str = "desktop",
    ):
        super().__init__(
            style=(
                nextcord.ButtonStyle.blurple
                if not currently_selected
                else nextcord.ButtonStyle.green
            ),
            label="Community",
            custom_id=encode_button_id(
                "help",
                help_type="community",
                embed_message_id=encode_snowflake(embed_message_id),
                author_id=encode_snowflake(author_id),
                preferred_view=preferred_view,
            ),
            disabled=False,
        )


class HelpMiscButton(nextcord.ui.Button):
    def __init__(
        self,
        currently_selected: bool = False,
        embed_message_id: int | None = None,
        author_id: int = 0,
        preferred_view: str = "desktop",
    ):
        super().__init__(
            style=(
                nextcord.ButtonStyle.blurple
                if not currently_selected
                else nextcord.ButtonStyle.green
            ),
            label="Misc",
            custom_id=encode_button_id(
                "help",
                help_type="misc",
                embed_message_id=encode_snowflake(embed_message_id),
                author_id=encode_snowflake(author_id),
                preferred_view=preferred_view,
            ),
            disabled=False,
        )


class HelpModerationButton(nextcord.ui.Button):
    def __init__(
        self,
        currently_selected: bool = False,
        embed_message_id: int | None = None,
        author_id: int = 0,
        preferred_view: str = "desktop",
    ):
        super().__init__(
            style=(
                nextcord.ButtonStyle.blurple
                if not currently_selected
                else nextcord.ButtonStyle.green
            ),
            label="Moderation",
            custom_id=encode_button_id(
                "help",
                help_type="moderation",
                embed_message_id=encode_snowflake(embed_message_id),
                author_id=encode_snowflake(author_id),
                preferred_view=preferred_view,
            ),
            disabled=False,
        )


class HelpCloseButton(nextcord.ui.Button):
    def __init__(self, embed_message_id: int | None = None, author_id: int = 0):
        super().__init__(
            style=nextcord.ButtonStyle.danger,
            label="Close",
            custom_id=encode_button_id(
                "help",
                help_type="close",
                embed_message_id=encode_snowflake(embed_message_id),
                author_id=encode_snowflake(author_id),
            ),
            disabled=False,
        )


class CommunitySelectedDropdown(nextcord.ui.Select):
    def __init__(
        self,
        embed_message_id: int | None = None,
        author_id: int = 0,
        preferred_view: str = "desktop",
    ):
        super().__init__(
            placeholder="Select a community command category",
            options=[
                nextcord.SelectOption(
                    label="Adult Access",
                    value="adult_access",
                    description="Commands relating to Adult Access features.",
                ),
                nextcord.SelectOption(
                    label="Fun",
                    value="jokes",
                    description="Commands relating to joke features.",
                ),
                nextcord.SelectOption(
                    label="Polls",
                    value="polls",
                    description="Commands relating to polls.",
                ),
                nextcord.SelectOption(
                    label="Suggestions",
                    value="suggestions",
                    description="Commands relating to suggestions.",
                ),
                nextcord.SelectOption(
                    label="Timer",
                    value="timer",
                    description="Commands relating to timers.",
                ),
                nextcord.SelectOption(
                    label="Voice",
                    value="voice",
                    description="Commands relating to voice features.",
                ),
            ],
            custom_id=encode_button_id(
                "community",
                embed_message_id=encode_snowflake(embed_message_id),
                author_id=encode_snowflake(author_id),
                preferred_view=preferred_view,
            ),
        )


class MiscSelectedDropdown(nextcord.ui.Select):
    def __init__(
        self,
        embed_message_id: int | None = None,
        author_id: int = 0,
        preferred_view: str = "desktop",
    ):
        super().__init__(
            placeholder="Select a misc command category",
            options=[
                nextcord.SelectOption(
                    label="Config",
                    value="config_1",
                    description="Commands relating to config features.",
                ),
                nextcord.SelectOption(
                    label="Config (II)",  # This is due to the 4096 character limit on the description
                    value="config_2",
                    description="Commands relating to config features.",
                ),
                nextcord.SelectOption(
                    label="Config (III)",  # This is due to the 6000 length limit on the description
                    value="config_3",
                    description="Commands relating to config features.",
                ),
                nextcord.SelectOption(
                    label="Config (IV)",  # This is due to the 6000 length limit on the description
                    value="config_4",
                    description="Commands relating to config features.",
                ),
                nextcord.SelectOption(
                    label="Embeds",
                    value="embeds",
                    description="Commands relating to embed features.",
                ),
                nextcord.SelectOption(
                    label="Help",
                    value="help",
                    description="Commands relating to help features.",
                ),
                nextcord.SelectOption(
                    label="Staff Management (I)",  # This is due to the 4096 character limit on the description
                    value="staff_1",
                    description="Commands relating to staff management features.",
                ),
                nextcord.SelectOption(
                    label="Staff Management (II)",
                    value="staff_2",
                    description="Commands relating to staff management features.",
                ),
                nextcord.SelectOption(
                    label="Staff Management (III)",
                    value="staff_3",
                    description="Commands relating to staff management features.",
                ),
                nextcord.SelectOption(
                    label="Staff Management (IV)",
                    value="staff_4",
                    description="Commands relating to staff management features.",
                ),
                nextcord.SelectOption(
                    label="Staff Management (V)",
                    value="staff_5",
                    description="Commands relating to staff management features.",
                ),
                nextcord.SelectOption(
                    label="Tickets (I)",
                    value="tickets_1",
                    description="Commands relating to ticket features.",
                ),
                nextcord.SelectOption(
                    label="Tickets (II)",
                    value="tickets_2",
                    description="Commands relating to ticket features.",
                ),
            ],
            custom_id=encode_button_id(
                "misc",
                embed_message_id=encode_snowflake(embed_message_id),
                author_id=encode_snowflake(author_id),
                preferred_view=preferred_view,
            ),
        )


class ModerationSelectedDropdown(nextcord.ui.Select):
    def __init__(
        self,
        embed_message_id: int | None = None,
        author_id: int = 0,
        preferred_view: str = "desktop",
    ):
        super().__init__(
            placeholder="Select a moderation command category",
            options=[
                nextcord.SelectOption(
                    label="Applications",
                    value="applications",
                    description="Commands relating to application features.",
                ),
                nextcord.SelectOption(
                    label="Archive",
                    value="archive",
                    description="Commands relating to channel archiving features.",
                ),
                nextcord.SelectOption(
                    label="Ban",
                    value="ban",
                    description="Commands relating to banning features.",
                ),
                nextcord.SelectOption(
                    label="Cases (I)",
                    value="cases_1",
                    description="Commands relating to case features.",
                ),
                nextcord.SelectOption(
                    label="Cases (II)",
                    value="cases_2",
                    description="Commands relating to case features.",
                ),
                nextcord.SelectOption(
                    label="Compliance",
                    value="compliance",
                    description="Commands relating to compliance features.",
                ),
                nextcord.SelectOption(
                    label="Notes",
                    value="notes",
                    description="Commands relating to note features.",
                ),
                nextcord.SelectOption(
                    label="Probation",
                    value="probation",
                    description="Commands relating to probation features.",
                ),
                nextcord.SelectOption(
                    label="Purge",
                    value="purge",
                    description="Commands relating to purging features.",
                ),
                nextcord.SelectOption(
                    label="Reformation",
                    value="reformation",
                    description="Commands relating to reformation features.",
                ),
                nextcord.SelectOption(
                    label="Slur Detection",
                    value="slur_detection",
                    description="Commands relating to slur detection features.",
                ),
                nextcord.SelectOption(
                    label="Timeout",
                    value="timeout",
                    description="Commands relating to timeout features.",
                ),
            ],
            custom_id=encode_button_id(
                "moderation",
                embed_message_id=encode_snowflake(embed_message_id),
                author_id=encode_snowflake(author_id),
                preferred_view=preferred_view,
            ),
        )


class HelpView(nextcord.ui.View):
    def __init__(
        self,
        selected_type: str | None = None,
        embed_message_id: int | None = None,
        author_id: int = 0,
        preferred_view: str = "desktop",
    ):
        super().__init__(timeout=None, auto_defer=False)
        match selected_type:
            case "community":
                self.add_item(
                    HelpCommunityButton(
                        currently_selected=True,
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpMiscButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpModerationButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpCloseButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                    )
                )
                self.add_item(
                    CommunitySelectedDropdown(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
            case "misc":
                self.add_item(
                    HelpCommunityButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpMiscButton(
                        currently_selected=True,
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpModerationButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpCloseButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                    )
                )
                self.add_item(
                    MiscSelectedDropdown(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
            case "moderation":
                self.add_item(
                    HelpCommunityButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpMiscButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpModerationButton(
                        currently_selected=True,
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpCloseButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                    )
                )
                self.add_item(
                    ModerationSelectedDropdown(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
            case _:
                self.add_item(
                    HelpCommunityButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpMiscButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpModerationButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                        preferred_view=preferred_view,
                    )
                )
                self.add_item(
                    HelpCloseButton(
                        embed_message_id=embed_message_id,
                        author_id=author_id,
                    )
                )


def verify_author(original_author_id: str, interaction: nextcord.Interaction) -> bool:
    return decode_snowflake(original_author_id) == interaction.user.id


class SersiHelpEmbeds:
    @staticmethod
    def community_selected_embed(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description="Please select a category from the dropdown to view commands.",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description="Please select a category from the dropdown to view commands.\n\n"
                "This is the mobile version of the help menu. Please use the desktop version for a better experience.",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def adult_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</adult_access bypass:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The user you want to give access to.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for giving access.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Give a user access to adult channels.`\n\n"
                f"</adult_access blacklist_remove:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The user you want to remove from the blacklist.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for removing the user from the blacklist.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a user from the adult blacklist.`\n\n"
                f"</adult_access revoke:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The user you want to revoke access from.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for revoking access.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Revoke a user's access to adult channels. Blacklists user.`\n\n"
                f"</adult_access verify:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The user you want to verify.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`dd: The day of the user's birth.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mm: The month of the user's birth.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`yyyy: The year of the user's birth.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Verify a user's age to give them access to adult channels.`",
            ).set_footer(text="Sersi Help")
        else:
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</adult_access bypass:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</adult_access blacklist_remove:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</adult_access revoke:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</adult_access verify:1184950643824275596>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`dd`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mm`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`yyyy`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def fun_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</fun coinflip:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Flip a coin.`\n\n"
                f"</fun nevermod:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The user who will never be modded.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Prevent a user from being modded.`\n\n"
                f"</fun roll:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`dice: The number of dice to roll.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`sides: The number of sides on the dice.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`advantage: Whether to roll with advantage.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`disadvantage: Whether to roll with disadvantage.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`base: The base number to add to the roll.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`advanced: Whether to show information about each dice.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Roll a dice.`\n\n"
                f"</fun uwuify:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`message: The text to uwuify.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Uwuify a message.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</fun coinflip:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</fun nevermod:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</fun roll:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`dice`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`sides`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`advantage`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`disadvantage`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`base`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`advanced`\n\n"
                f"</fun uwuify:1168667156251164773>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`message`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def poll_dropdown_embed(preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</poll create:1166849339763732581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`query: The question to ask.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`type: The type of poll to create.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Single Choice.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Multiple Choice.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option1: The first option for the poll.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option2: The second option for the poll.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option3`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option4`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option5`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option6`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option7`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option8`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option9`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option10`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Create a poll.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</poll create:1166849339763732581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`query`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`type`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option1`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option2`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option3`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option4`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option5`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option6`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option7`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option8`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option9`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`option10`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def suggestion_dropdown_embed(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</suggestion submit:1169773626736791655>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion: The suggestion to make.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion_media: Any media URL part of the suggestion.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Submit a suggestion for review.`\n\n"
                f"</suggestion review:1169773626736791655>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.cet).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion_id: The ID of the suggestion to review.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome: The outcome of the review.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Approve`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Deny`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the outcome.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Review a suggestion.`\n\n"
                f"</suggestion mark:1169773626736791655>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.cet).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion_id: The ID of the suggestion to mark.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome: The mark to apply to the suggestion.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Considering`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Planned`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`In Progress`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`On Hold`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Completed`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Not Happening`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the mark.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Mark a suggestion.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</suggestion submit:1169773626736791655>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion_media`\n\n"
                f"</suggestion review:1169773626736791655>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.cet).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion_id`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</suggestion mark:1169773626736791655>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.cet).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`suggestion_id`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def timer_dropdown_embed(preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</timer:1168667246021845182>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`time_minutes: The number of minutes for the timer.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Create a timer.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</timer:1168667246021845182>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`time_minutes`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def voice_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</mass_move:1172948462652903454>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`current: The channel to move users from.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`target: The channel to move users to.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Mass move members from one VC to another.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Community Commands",
                description=f"</mass_move:1172948462652903454>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`current`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`target`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def misc_selected_embed(preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description="Please select a category from the dropdown to view commands.",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description="Please select a category from the dropdown to view commands.\n\n"
                "This is the mobile version of the help menu. Please use the desktop version for a better experience.",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def config_dropdown_embed_1(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config ignored add_category:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category: The category to ignore.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Ignore a category from being tracked.`\n\n"
                f"</config ignored add_channel:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel: The channel to ignore.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Ignore a channel from being tracked.`\n\n"
                f"</config ignored remove_category:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category: The category to stop ignoring.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Stop ignoring a category from being tracked.`\n\n"
                f"</config ignored remove_channel:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel: The channel to stop ignoring.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Stop ignoring a channel from being tracked.`\n\n",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config ignored add_category:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config ignored add_channel:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config ignored remove_category:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config ignored remove_channel:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def config_dropdown_embed_2(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config list:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`section: The section to list.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channels`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ignored_channels`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ignored_categories`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`roles`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`permission_roles`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`punishment_roles`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`opt_in_roles`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`emotes`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`guilds`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`List a section of the config.`\n\n"
                f"</config opt_in_roles add:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to add to the opt-in roles.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a role to the opt-in roles.`\n\n"
                f"</config opt_in_roles remove:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to remove from the opt-in roles.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a role from the opt-in roles.`\n\n"
                f"</config punishment_roles add:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to add to the punishment roles.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a role to the punishment roles.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config list:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`section`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config opt_in_roles add:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config opt_in_roles remove:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config punishment_roles add:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def config_dropdown_embed_3(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config punishment_roles remove:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to remove from the punishment roles.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a role from the punishment roles.`\n\n"
                f"</config reload:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Reload the config.`\n\n"
                f"</config set_channel:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`setting: The setting to set.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`alert`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`logging`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`false_positives`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mod_logs`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`dm_forward`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mod_applications`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`cet_applications`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ageverification`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`compliance_review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`dark_mod_review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`senior_mod_review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel: The channel to set.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Set a channel in the config.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config punishment_roles remove:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config reload:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config set_channel:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`setting`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def config_dropdown_embed_4(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config set_permission_role:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`setting: The setting to set.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`staff`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reformist`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`cet`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`cet_lead`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`compliance`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`senior_moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`dark_moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to set.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Set a permission role in the config.`\n\n"
                f"</config set_role:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`setting: The setting to set.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reformation`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reformed`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`probation`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`never_mod`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`civil_engineering_initiate`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`newbie`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`honourable_member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`adult_access`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`adult_verified`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to set.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Set a role in the config.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</config set_permission_role:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`setting`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</config set_role:1171881279734694008>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`setting`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def embed_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</embed send:1168667160571293820>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`type: The type of embed.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Administrator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Community Engagement`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Staff`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel: The channel to send the embed to.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`title: The title of the embed.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`body: The body of the embed.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Create an embed.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</embed send:1168667160571293820>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`type`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`channel`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`title`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`body`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def help_dropdown_embed(preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</help:1208444716618752000>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`command: The command to get help for.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`view_type: The type of view preferred.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Desktop View`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Mobile View`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Get help for a command.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Misc Commands",
                description=f"</help:1208444716618752000>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`command`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`view_type`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def staff_management_embed_1(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff add legacy_staff:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to add to the staff.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`branch: The branch to add the user to.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to add the user to.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`added_by: The user who added the user to the staff.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mentor: The mentor for the user if they had one.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add an existing staff member to the staff system.`\n\n"
                f"</staff add trial_moderator:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to add to the staff.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mentor: The mentor for the user.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a trial moderator to the staff system.`\n\n"
                f"</staff add promote:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to promote.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Promote a trial moderator to moderator.`\n\n"
                f"</staff add community_engagement:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to add to the staff.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a community engagement member to the staff system.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff add legacy_staff:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`branch`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`added_by`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mentor`\n\n"
                f"</staff add trial_moderator:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mentor`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</staff add promote:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</staff add community_engagement:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def staff_management_embed_2(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff add reinstate_moderator:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to reinstate.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Reinstate a moderator to the staff system.`\n\n"
                f"</staff add transfer:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to transfer.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`branch: The branch to transfer the user to.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role to transfer the user to.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Transfer a staff member to a different branch.`\n\n"
                f"</staff trial_mod_review:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to review.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`review_type: The type of review.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`First Review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Second Review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Third Review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Fourth Review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Fifth Review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Sixth Review`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome: The outcome of the review.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Pass`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Fail`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`comment: The comment for the review.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Review a trial moderator.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff add reinstate_moderator:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</staff add transfer:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`branch`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</staff trial_mod_review:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`review_type`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`comment`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def staff_management_embed_3(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff blacklist add:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to blacklist.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for blacklisting the user.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Blacklist a user from the staff system.`\n\n"
                f"</staff blacklist remove:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to remove from the blacklist.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for removing the user from the blacklist.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a user from the staff blacklist.`\n\n"
                f"</staff remove discharge:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to discharge.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for discharging the user.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason: To bypass the dual custody system.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Discharge a user from the staff system.`\n\n"
                f"</staff remove retire:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for retiring.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to retire.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Retire from the staff system.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff blacklist add:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</staff blacklist remove:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</staff remove discharge:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason`\n\n"
                f"</staff remove retire:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def staff_management_embed_4(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff modify mod_record:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to modify the record of.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mentor: The mentor for the user.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_start_day: The day the trial started.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_start_month: The month the trial started.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_start_year: The year the trial started.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_end_day: The day the trial ended.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_end_month: The month the trial ended.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_end_year: The year the trial ended.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_passed: The outcome of the trial.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Modify the moderator record of a user.`\n\n"
                f"</staff modify staff_record:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to modify the record of.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`branch: The branch the user is in.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role: The role the user has.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`added_by: The user who added the user to the staff.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`active: The status of the user.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`left_day: The day the user left.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`left_month: The month the user left.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`left_year: The year the user left.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`removed_by: The user who removed the user from the staff.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`discharge_type: The type of discharge.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`discharge_reason: The reason for the discharge.`\n\n"
                f"</staff modify trial_review:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to modify the review of.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`review_type: The type of review.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome: The outcome of the review.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`comment: The comment for the review.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Modify the trial review of a user.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff modify mod_record:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`mentor`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_start_day`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_start_month`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_start_year`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_end_day`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_end_month`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_end_year`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`trial_passed`\n\n"
                f"</staff modify staff_record:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`branch`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`role`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`added_by`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`active`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`left_day`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`left_month`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`left_year`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`removed_by`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`discharge_type`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`discharge_reason`\n"
                f"</staff modify trial_review:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`review_type`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`outcome`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`comment`\n\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def staff_management_embed_5(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff revoke_honoured_member:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The user to revoke the role from.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for revoking the role.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason: To bypass the dual custody system.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Revoke the honoured member role from a user.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Staff Management",
                description=f"</staff revoke_honoured_member:1207465701866995742>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def ticket_dropdown_embed_1(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Ticket Commands",
                description=f"</ticket audit:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket: The ticket ID or channel to audit.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Audit a ticket.`\n\n"
                f"</ticket close:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`closing_remarks: The remarks for closing the ticket.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket: The ticket ID or channel to close.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category: The category of the ticket.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`subcategory: The sub category of the ticket.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`send_survey: Whether to send a survey or not.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Close a ticket.`\n\n"
                f"</ticket create:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket_type: The type of ticket to create.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Moderation Lead`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Community Engagement`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Community Engagement Lead`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Administrator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`opening_remarks: The remarks for opening the ticket.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category: The category of the ticket.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Create a ticket.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Ticket Commands",
                description=f"</ticket audit:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</ticket close:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`closing_remarks`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`subcategory`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`send_survey`\n\n"
                f"</ticket create:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: `None`\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket_type`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`opening_remarks`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def ticket_dropdown_embed_2(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Ticket Commands",
                description=f"</ticket escalate:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`escalation_level: The level of escalation.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Moderation Lead`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Community Engagement`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Community Engagement Lead`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Administrator`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket: The ticket ID or channel to escalate.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Escalate a ticket.`\n\n"
                f"</ticket info:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket: The ticket ID or channel to get info on.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Get info on a ticket.`\n\n"
                f"</ticket recategorize:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category: The new category for the ticket.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`subcategory: The new subcategory for the ticket.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket: The ticket ID or channel to recategorize.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Recategorize a ticket.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Ticket Commands",
                description=f"</ticket escalate:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`escalation_level`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket`\n\n"
                f"</ticket info:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</ticket recategorize:1169396755788468345>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.staff).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`category`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`subcategory`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ticket`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def moderation_selected_embed(preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Moderation Commands",
                description="Please select a category from the dropdown to view commands.",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Moderation Commands",
                description="Please select a category from the dropdown to view commands.\n\n"
                "This is the mobile version of the help menu. Please use the desktop version for a better experience.",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def application_dropdown_embed(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Application Commands",
                description=f"</moderator_invite:1175169053606809620>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The member to invite.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Invite a user to apply to the moderation team.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Application Commands",
                description=f"</moderator_invite:1175169053606809620>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def archive_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Archive Commands",
                description=f"</archive:1166849338404778056>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`logged_channel: The channel to archive.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`output_channel: The channel to output the archive to.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Archive a channel.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Archive Commands",
                description=f"</archive:1166849338404778056>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {CONFIG.permission_roles.dark_moderator}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`logged_channel`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`output_channel`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def ban_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Ban Commands",
                description=f"</ban add:1169383803219882126>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender: The member to ban.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence: The reason for the ban.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`detail: The details of the ban.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`type: The type of ban.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Immediate Ban`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Vote Ban`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`timeout: Whether to timeout during a vote ban.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Ban a member.`\n\n"
                f"</ban remove:1169383803219882126>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender: The member to unban.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the unban.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ban_id: The ID of the ban to remove.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Unban a member.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Ban Commands",
                description=f"</ban add:1169383803219882126>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`detail`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`type`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`timeout`\n\n"
                f"</ban remove:1169383803219882126>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`ban_id`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def cases_dropdown_embed_1(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Case Commands",
                description=f"</cases detail:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id: The ID of the case to get details on.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`scrubbed: Whether the case is scrubbed or not.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Get details on a case.`\n\n"
                f"</cases list:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page: The page to view.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_type: The type of case to list.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`moderator: The moderator to list cases for.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender: The user to list cases for.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence: The offence to list cases for.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`List cases.`\n\n"
                f"</cases audit:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id: The ID of the case to audit.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Audit changes to a case.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Case Commands",
                description=f"</cases detail:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`scrubbed`\n\n"
                f"</cases list:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_type`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`moderator`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence`\n\n"
                f"</cases audit:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def cases_dropdown_embed_2(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Case Commands",
                description=f"</cases delete:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id: The ID of the case to delete.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the deletion.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Delete a case.`\n\n"
                f"</cases scrub:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id: The ID of the case to scrub.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the scrub.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Scrub a case.`\n\n"
                f"</cases edit:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_type: The type of case to edit.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id: The ID of the case to edit.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence: The new offence for the case.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`detail: The new details for the case.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`duration: The new duration for the timeout case.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`timespan: The new timespan for the timeout case.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`state: The new state for the reformation case.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Edit a case.`",
            ).set_footer(text="Sersi Help")

        else:
            return SersiEmbed(
                title="Sersi Help Menu - Case Commands",
                description=f"</cases delete:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.dark_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</cases scrub:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</cases edit:1169383795280056370>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_type`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`detail`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`duration`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`timespan`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`state`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def compliance_dropdown_embed(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Compliance Commands",
                description=f"</moderation_report create custom:1204461791497814087>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.compliance).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`start_day: The day the report starts.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`start_month: The month the report starts.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`start_year: The year the report starts.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`end_day: The day the report ends.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`end_month: The month the report ends.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`end_year: The year the report ends.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Create a custom moderation report.`\n\n"
                f"</moderation_report create preset:1204461791497814087>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.compliance).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`preset: The preset to use for the report.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Month to Date`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Quarter to Date`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Year to Date`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}{CONFIG.emotes.blank}`All Time`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Create a preset moderation report.`\n\n"
                f"</moderation_leaderboard:1207748753881043004>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_type: The type of case to view the leaderboard for.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`View the moderation leaderboard.`",
            ).set_footer(text="Sersi Help")

        else:

            return SersiEmbed(
                title="Sersi Help Menu - Compliance Commands",
                description=f"</moderation_report create custom:1204461791497814087>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.compliance).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`start_day`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`start_month`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`start_year`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`end_day`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`end_month`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`end_year`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</moderation_report create preset:1204461791497814087>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.compliance).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`preset`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</moderation_leaderboard:1207748753881043004>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_type`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def notes_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Note Commands",
                description=f"</notes add:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`noted: The member to add the note to.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`note: The note to add.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a note to a member.`\n\n"
                f"</notes delete:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the deletion.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`note_id: The ID of the note to delete.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The user to delete all notes for.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Delete a note.`\n\n"
                f"</notes detail:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`note_id: The ID of the note to get details on.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Get details on a note.`\n\n"
                f"</notes list:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user: The user to list notes for.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`author: The author to list notes for.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page: The page to view.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`List notes.`",
            ).set_footer(text="Sersi Help")

        else:

            return SersiEmbed(
                title="Sersi Help Menu - Note Commands",
                description=f"</notes add:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`noted`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`note`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</notes delete:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`note_id`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n\n"
                f"</notes detail:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`note_id`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</notes list:1170530851356950581>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`user`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`author`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def probation_dropdown_embed(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Probation Commands",
                description=f"</probation add:1169383712593563722>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to add to probation.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the probation.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason: Whether to bypass dual custody.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a member to probation.`\n\n"
                f"</probation remove:1169383712593563722>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to remove from probation.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the removal.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason: Whether to bypass dual custody.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a member from probation.`",
            ).set_footer(text="Sersi Help")

        else:

            return SersiEmbed(
                title="Sersi Help Menu - Probation Commands",
                description=f"</probation add:1169383712593563722>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason`\n\n"
                f"</probation remove:1169383712593563722>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def purge_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Purge Commands",
                description=f"</purge standard:1166849423788224613>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`amount: The amount of messages to purge.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to purge messages from.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Purge messages from a channel.`\n\n"
                f"</purge timed:1166849423788224613>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`time: How many minutes back should be purged.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to purge messages from.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Purge messages from a channel within a time frame.`",
            ).set_footer(text="Sersi Help")

        else:

            return SersiEmbed(
                title="Sersi Help Menu - Purge Commands",
                description=f"</purge standard:1166849423788224613>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`amount`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n\n"
                f"</purge timed:1166849423788224613>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`time`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def reformation_dropdown_embed(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Reformation Commands",
                description=f"</reformation add:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to reform.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence: The offence for the reformation.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`details: The details for the reformation.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a member to the reformation cente.`\n\n"
                f"</reformation delete_cell:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Delete a reformation cell.`\n\n"
                f"</reformation query_failed:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to query.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the query.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Query if attempts to reform should continue.`\n\n"
                f"</reformation query_release:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to query.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the query.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Query if a member should be released from the reformation center.`\n\n"
                f"</reformation release:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to release.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the release.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Release a member from the reformation center.`\n\n"
                f"</reformation remove_reformist:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member: The member to remove.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the removal.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a member from the reformation center.`",
            ).set_footer(text="Sersi Help")

        else:

            return SersiEmbed(
                title="Sersi Help Menu - Reformation Commands",
                description=f"</reformation add:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`details`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</reformation delete_cell:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</reformation query_failed:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n\n"
                f"</reformation query_release:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</reformation release:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.senior_moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</reformation remove_reformist:1169383883524022375>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`member`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def slur_detection_dropdown_embed(
        interaction: nextcord.Interaction, preferred_view: str
    ):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Slur Detection Commands",
                description=f"</slur_detection add_goodword:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`word: The word to add to the good word list.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a word to the good word list.`\n\n"
                f"</slur_detection add_slur:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`slur: The word to add to the slur list.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Add a word to the slur list.`\n\n"
                f"</slur_detection list_goodwords:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page: The page to view.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`List good words.`\n\n"
                f"</slur_detection list_slurs:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page: The page to view.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`List slurs.`\n\n"
                f"</slur_detection remove_goodword:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`word: The word to remove from the good word list.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a word from the good word list.`\n\n"
                f"</slur_detection remove_slur:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`slur: The word to remove from the slur list.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason: Whether to bypass dual custody.`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a word from the slur list.`",
            ).set_footer(text="Sersi Help")

        else:

            return SersiEmbed(
                title="Sersi Help Menu - Slur Detection Commands",
                description=f"</slur_detection add_goodword:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`word`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</slur_detection add_slur:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`slur`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</slur_detection list_goodwords:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page`\n\n"
                f"</slur_detection list_slurs:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`page`\n\n"
                f"</slur_detection remove_goodword:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`word`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</slur_detection remove_slur:1169383714057375866>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`slur`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`bypass_reason`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")

    @staticmethod
    def timeout_dropdown_embed(interaction: nextcord.Interaction, preferred_view: str):
        if preferred_view == "desktop":
            return SersiEmbed(
                title="Sersi Help Menu - Timeout Commands",
                description=f"</timeout add:1169383800090923068>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender: The member to timeout.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence: The offence for the timeout.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`detail: The details for the timeout.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`duration: The duration of the timeout.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`timespan: The timespan of the timeout.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Timeout a user.`\n\n"
                f"</timeout remove:1169383800090923068>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id: The case ID of the timeout to remove.`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason: The reason for the removal.`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"{CONFIG.emotes.blank}**Description**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`Remove a timeout.`",
            ).set_footer(text="Sersi Help")

        else:

            return SersiEmbed(
                title="Sersi Help Menu - Timeout Commands",
                description=f"</timeout add:1169383800090923068>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offender`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`offence`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`detail`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`duration`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`timespan`\n"
                f"{CONFIG.emotes.blank}**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n\n"
                f"</timeout remove:1169383800090923068>\n"
                f"{CONFIG.emotes.blank}**Required Role**: {interaction.guild.get_role(CONFIG.permission_roles.moderator).mention}\n"
                f"{CONFIG.emotes.blank}**Required Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`case_id`\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`reason`\n"
                f"**Optional Arguments**:\n"
                f"{CONFIG.emotes.blank}{CONFIG.emotes.blank}`None`\n"
                f"**This is the mobile version of the help menu. Please use the desktop version for a better experience.**",
            ).set_footer(text="Sersi Help")
