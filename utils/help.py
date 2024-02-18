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
