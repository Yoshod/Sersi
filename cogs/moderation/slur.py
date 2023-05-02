import asyncio
from datetime import datetime, timezone
import nextcord
from nextcord.ext import commands

import utils
from utils import logs
from utils.base import (
    sanitize_mention,
    SersiEmbed,
    PageView,
    format_entry,
    convert_mention_to_id,
)
from utils.cases import slur_history, slur_virgin, create_slur_case, fetch_offender_cases
from utils.config import Configuration
from utils.notes import get_note_by_user
from utils.perms import cb_is_mod
from slurdetector import (
    load_slurdetector,
    detect_slur,
)


class ActionTakenButton(nextcord.ui.Button):
    def __init__(self, config: Configuration):
        super().__init__(label="Action Taken")
        self.config = config

    async def callback(self, interaction: nextcord.Interaction) -> None:
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Action Taken By", value=interaction.user.mention, inline=False
        )
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Action Taken Pressed",
                description="Action has been taken by a moderator in response to a report.",
                fields={
                    "Report:": interaction.message.jump_url,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                },
            )
        )

        case_data = []
        for field in new_embed.fields:
            if field.name in ["User:", "Slurs Found:"]:
                case_data.append(field.value)

        member = interaction.guild.get_member(int(sanitize_mention(case_data[0])))

        timestamp = datetime.now(timezone.utc)

        create_slur_case(
            self.config,
            case_data[1],
            interaction.message.jump_url,
            member,
            interaction.user,
        )

        await utils.logs.update_response(self.config, interaction.message, timestamp)


class AcceptableUseButton(nextcord.ui.Button):
    def __init__(self, config: Configuration):
        super().__init__(label="Acceptable Use")
        self.config = config

    async def callback(self, interaction: nextcord.Interaction) -> None:
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Usage Deemed Acceptable By",
            value=interaction.user.mention,
            inline=False,
        )
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Acceptable Use Pressed",
                description="Usage of a slur has been deemed acceptable by a moderator in response to a report.",
                fields={
                    "Report:": interaction.message.jump_url,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                },
            )
        )

        await utils.logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )


class FalsePositiveButton(nextcord.ui.Button):
    def __init__(self, config: Configuration):
        super().__init__(label="False Positive")
        self.config = config

    async def callback(self, interaction: nextcord.Interaction) -> None:
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Deemed As False Positive By:",
            value=interaction.user.mention,
            inline=False,
        )
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)
        channel = interaction.guild.get_channel(self.config.channels.false_positives)

        logging_embed: nextcord.Embed = SersiEmbed(title="Marked as false positive")

        for field in new_embed.fields:
            if field.name in ["Context:", "Slurs Found:"]:
                logging_embed.add_field(
                    name=field.name, value=field.value, inline=False
                )

        logging_embed.add_field(
            name="Report URL:", value=interaction.message.jump_url, inline=False
        )
        await channel.send(embed=logging_embed)

        # Logging
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="False Positive Pressed",
                description="Detected slur has been deemed a false positive by a moderator in response to a report.",
                fields={
                    "Report:": interaction.message.jump_url,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                },
            )
        )

        await utils.logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )


class ViewCasesButton(nextcord.ui.Button):
    def __init__(self, config: Configuration):
        super().__init__(label="View Slur Cases", row=1)
        self.config = config

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        original_embed = interaction.message.embeds[0]

        for field in original_embed.fields:
            if field.name.lower() == "user:":
                offender = interaction.guild.get_member(
                    convert_mention_to_id(field.value)
                )
                break

        else:
            interaction.followup.send(
                f"{self.config.emotes.fail} Failed to return user cases"
            )
            return

        cases_embed = SersiEmbed(title=f"{offender.name}'s Cases")
        cases_embed.set_thumbnail(offender.display_avatar.url)

        view = PageView(
            config=self.config,
            base_embed=cases_embed,
            fetch_function=fetch_offender_cases,
            author=interaction.user,
            entry_form="{entry[1]} <t:{entry[2]}:R>",
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            offender=offender,
            case_type="slur_cases",
        )

        await view.send_followup(interaction)


class ViewNotesButton(nextcord.ui.Button):
    def __init__(self, config: Configuration):
        super().__init__(label="View Notes", row=1)
        self.config = config

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        original_embed = interaction.message.embeds[0]

        for field in original_embed.fields:
            if field.name.lower() == "user:":
                user = interaction.guild.get_member(convert_mention_to_id(field.value))
                break

        else:
            interaction.followup.send(
                f"{self.config.emotes.fail} Failed to return user notes"
            )
            return

        note_embed = SersiEmbed(title=f"{user.name}'s Notes")
        note_embed.set_thumbnail(user.display_avatar.url)

        view = PageView(
            config=self.config,
            base_embed=note_embed,
            fetch_function=get_note_by_user,
            author=interaction.user,
            entry_form=format_entry,
            field_title="{entries[0][0]}",
            inline_fields=False,
            cols=10,
            per_col=1,
            init_page=0,
            user_id=str(user.id),
        )

        await view.send_followup(interaction)


class SlurAlertButtons(nextcord.ui.View):
    def __init__(self, config: Configuration, interaction_check):
        super().__init__(timeout=None)
        self.add_item(ActionTakenButton(config))
        self.add_item(AcceptableUseButton(config))
        self.add_item(FalsePositiveButton(config))
        self.add_item(ViewCasesButton(config))
        self.add_item(ViewNotesButton(config))
        self.interaction_check(interaction_check)


class Slur(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail
        load_slurdetector()

    def _get_previous_cases(
        self, user: nextcord.User | nextcord.Member, slurs: list[str]
    ) -> str:
        slur_test = slur_virgin(self.config, user)
        if slur_test:
            return f"{self.config.emotes.fail} The user is a first time offender."

        else:
            cases = slur_history(self.config, user, slurs)

            if not cases:
                return (
                    f"{self.config.emotes.success} The user has a history of using slurs that were not detected "
                    f"in this message."
                )

            else:
                prev_offences = (
                    f"{self.config.emotes.success} The user has a history of using a slur detected in "
                    "this message:"
                )
                for slur_cases in cases:
                    prev_offences += f"\n`{slur_cases[0]}` {slur_cases[2]}"

                return prev_offences

    # events
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.message.Message):
        if message.content.startswith(self.bot.command_prefix):
            return

        detected_slurs: list[str] = detect_slur(message.content)

        if message.channel.category.name == "Administration Centre":
            # ignores message if sent inside the administration centre
            return

        if message.author == self.bot.user:
            # ignores message if message is by bot
            return

        elif len(detected_slurs) > 0:  # checks slur heat

            alert = await self.bot.get_channel(self.config.channels.alert).send(
                embed=SersiEmbed(
                    title="Slur(s) Detected",
                    description="A slur has been detected. Moderation action is advised.",
                    footer="Sersi Slur Detection Alert",
                    fields={
                        "Channel:": message.channel.mention,
                        "User:": message.author.mention,
                        "Context:": message.content
                        if len(message.content) < 1024
                        else "`MESSAGE TOO LONG`",
                        "Slurs Found:": ", ".join(set(detected_slurs)),
                        "URL:": message.jump_url,
                        "Previous Slur Uses:": self._get_previous_cases(
                            message.author, detected_slurs
                        ),
                    },
                ),
                view=SlurAlertButtons(self.config, cb_is_mod),
            )

            await utils.logs.create_alert_log(
                self.config, alert, utils.logs.AlertType.Slur, alert.created_at
            )

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)
            if not updated_message.edited_at:
                await alert.reply(
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )

    @commands.Cog.listener()
    async def on_presence_update(self, before: nextcord.Member, after: nextcord.Member):
        slurs: list[str] = detect_slur(after.status)
        if slurs:
            alert: nextcord.Message = await after.guild.get_channel(
                self.config.channels.alert
            ).send(
                embed=SersiEmbed(
                    title="Member changed their status to contain slurs",
                    description="A slur has been detected. Moderation action is advised.",
                    footer="Sersi Slur Detection Alert",
                    fields={
                        "User:": after.mention,
                        "Status:": after.status,
                        "Slurs Found:": ", ".join(set(slurs)),
                        "Previous Slur Uses:": self._get_previous_cases(after, slurs),
                    },
                ),
                view=SlurAlertButtons(self.config, cb_is_mod),
            )

            await utils.logs.create_alert_log(
                self.config, alert, utils.logs.AlertType.Slur, alert.created_at
            )

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)
            if not updated_message.edited_at:
                await alert.reply(
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )

    @commands.Cog.listener()
    async def on_user_update(self, before: nextcord.User, after: nextcord.User):
        slurs: list[str] = detect_slur(after.name)
        if slurs:
            alert: nextcord.Message = await self.bot.get_channel(
                self.config.channels.alert
            ).send(
                embed=SersiEmbed(
                    title="Member changed their username to contain slurs",
                    description="A slur has been detected. Moderation action is advised.",
                    footer="Sersi Slur Detection Alert",
                    fields={
                        "User:": after.mention,
                        "Name:": after.name,
                        "Slurs Found:": ", ".join(set(slurs)),
                        "Previous Slur Uses:": self._get_previous_cases(after, slurs),
                    },
                ),
                view=SlurAlertButtons(self.config, cb_is_mod),
            )

            await utils.logs.create_alert_log(
                self.config, alert, utils.logs.AlertType.Slur, alert.created_at
            )

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)
            if not updated_message.edited_at:
                await alert.reply(
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )

    @commands.Cog.listener()
    async def on_member_update(self, before: nextcord.Member, after: nextcord.Member):
        slurs: list[str] = detect_slur(after.nick)
        if slurs:
            alert: nextcord.Message = await self.bot.get_channel(
                self.config.channels.alert
            ).send(
                embed=SersiEmbed(
                    title="Member changed their nickname to contain slurs",
                    description="A slur has been detected. Moderation action is advised.",
                    footer="Sersi Slur Detection Alert",
                    fields={
                        "User:": after.mention,
                        "Nickname:": after.nick,
                        "Slurs Found:": ", ".join(set(slurs)),
                        "Previous Slur Uses:": self._get_previous_cases(after, slurs),
                    },
                ),
                view=SlurAlertButtons(self.config, cb_is_mod),
            )

            await utils.logs.create_alert_log(
                self.config, alert, utils.logs.AlertType.Slur, alert.created_at
            )

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)
            if not updated_message.edited_at:
                await alert.reply(
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )


def setup(bot, **kwargs):
    bot.add_cog(Slur(bot, kwargs["config"]))
