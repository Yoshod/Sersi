import os
import nextcord
from nextcord.ext import commands
from utils.base import decode_button_id, decode_snowflake

from utils.help import (
    HelpView,
    verify_author,
    SersiHelpEmbeds as SersiHelp,
)
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

grandparent_dir = os.path.dirname(parent_dir)

config_path = os.path.join(grandparent_dir, "persistent_data/config.yaml")

CONFIG = Configuration.from_yaml_file(config_path)


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        name="help",
        description="Shows the help command",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def help(
        self,
        interaction: nextcord.Interaction,
        view_type: str = nextcord.SlashOption(
            name="view_type",
            description="Force the help menu to be sent as a desktop view.",
            choices={
                "Desktop View": "desktop",
                "Mobile View": "mobile",
            },
            required=False,
        ),
    ):
        embed_message: nextcord.Message = await interaction.channel.send(
            embed=SersiEmbed(
                title="Sersi Help Menu",
                description="For more information on specific commands, please use the buttons below.",
            ).set_footer(text="Sersi Help", icon_url=self.bot.user.avatar.url)
        )

        preferred_view = view_type

        if not view_type:
            is_mobile = interaction.user.is_on_mobile()

            preferred_view = "mobile" if is_mobile else "desktop"

        view = HelpView(
            selected_type=None,
            embed_message_id=embed_message.id,
            author_id=interaction.user.id,
            preferred_view=preferred_view,
        )

        await embed_message.edit(view=view)

        await interaction.response.send_message(
            "The help menu has been sent to this channel.",
            ephemeral=True,
            delete_after=1,
        )

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        acceptable_starts = ["help", "community", "misc", "moderation"]

        if not interaction.data["custom_id"].startswith(tuple(acceptable_starts)):
            return

        action, args, kwargs = decode_button_id(interaction.data["custom_id"])

        if not verify_author(kwargs["author_id"], interaction):
            await interaction.response.send_message(
                f"{CONFIG.emotes.fail} You are not the author of this help menu.",
                ephemeral=True,
            )
            return

        if action == "help":
            match kwargs["help_type"]:
                case "community":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.community_selected_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="community",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                    await interaction.response.send_message(
                        f"{CONFIG.emotes.success} The help menu has been updated.",
                        ephemeral=True,
                        delete_after=1,
                    )
                case "misc":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.misc_selected_embed(kwargs["preferred_view"]),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "moderation":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.moderation_selected_embed(
                            kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )
                case "close":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    if message:
                        await message.delete()
                        await interaction.response.send_message(
                            f"{CONFIG.emotes.success} The help menu has been closed.",
                            ephemeral=True,
                        )

                    else:
                        await interaction.response.send_message(
                            f"{CONFIG.emotes.fail} The help menu has already been closed.",
                            ephemeral=True,
                        )

        elif action == "community":
            selected_dropdown = interaction.data["values"][0]

            match selected_dropdown:
                case "adult_access":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.adult_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="community",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "jokes":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.fun_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="community",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "polls":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.poll_dropdown_embed(kwargs["preferred_view"]),
                        view=HelpView(
                            selected_type="community",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "suggestions":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.suggestion_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="community",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "timer":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.timer_dropdown_embed(kwargs["preferred_view"]),
                        view=HelpView(
                            selected_type="community",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "voice":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.voice_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="community",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

        elif action == "misc":
            selected_dropdown = interaction.data["values"][0]

            match selected_dropdown:
                case "config_1":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.config_dropdown_embed_1(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "config_2":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.config_dropdown_embed_2(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "config_3":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.config_dropdown_embed_3(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "config_4":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.config_dropdown_embed_4(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "embeds":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.embed_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "help":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.help_dropdown_embed(kwargs["preferred_view"]),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "staff_1":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.staff_management_embed_1(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "staff_2":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.staff_management_embed_2(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "staff_3":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.staff_management_embed_3(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "staff_4":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.staff_management_embed_4(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "staff_5":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.staff_management_embed_5(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "tickets_1":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.ticket_dropdown_embed_1(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "tickets_2":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )
                    await message.edit(
                        embed=SersiHelp.ticket_dropdown_embed_2(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="misc",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

        elif action == "moderation":
            selected_dropdown = interaction.data["values"][0]

            match selected_dropdown:
                case "applications":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.application_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "archive":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.archive_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "ban":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.ban_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "cases_1":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.cases_dropdown_embed_1(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "cases_2":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.cases_dropdown_embed_2(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "compliance":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.compliance_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "notes":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.notes_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

                case "probation":
                    message = await interaction.channel.fetch_message(
                        decode_snowflake(kwargs["embed_message_id"])
                    )

                    await message.edit(
                        embed=SersiHelp.probation_dropdown_embed(
                            interaction, kwargs["preferred_view"]
                        ),
                        view=HelpView(
                            selected_type="moderation",
                            embed_message_id=message.id,
                            author_id=interaction.user.id,
                            preferred_view=kwargs["preferred_view"],
                        ),
                    )

        await interaction.response.send_message(
            f"{CONFIG.emotes.success} The help menu has been updated.",
            ephemeral=True,
            delete_after=1,
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Help(bot))
