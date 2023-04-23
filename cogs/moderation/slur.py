import asyncio
import pickle
from datetime import datetime, timezone

import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View

import logutils
from baseutils import sanitize_mention, SersiEmbed
from caseutils import slur_case, case_history
from configutils import Configuration
from permutils import cb_is_mod
from slurdetector import (
    load_slurdetector,
    detect_slur,
)


class Slur(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail
        load_slurdetector()

    def _get_previous_cases(self, user_id: int, slurs: list[str]) -> str:
        with open(self.config.datafiles.casehistory, "rb") as file:
            cases: dict[int:list] = pickle.load(file)
            # --> dict of list; one dict entry per user ID

        user_history: list = cases.get(user_id, [])
        # -> list of user offenses, empty list if none

        slur_virgin: bool = True
        previous_offenses: list[str] = []

        for case in user_history:
            if case[1] == "Slur Usage":
                slur_virgin = False

                # check if slur was done before
                uid = case[0]
                with open(self.config.datafiles.casedetails, "rb") as file:
                    case_details = pickle.load(file)
                    slur_used = case_details[uid][1]

                    previous_slurs = slur_used.split(", ")

                    if any(new_slur in previous_slurs for new_slur in slurs):
                        # slur has been said before by user
                        report_url = case_details[uid][2]
                        previous_offenses.append(f"`{uid}` [Jump!]({report_url})")

        if not slur_virgin and not previous_offenses:
            # user has said slurs before, however not that particular one
            return (
                f"{self.config.emotes.success} The user has a history of using slurs that were not detected "
                f"in this message."
            )

        elif previous_offenses:  # user has said that slur before
            prev_offenses = "\n".join(previous_offenses)
            if len(prev_offenses) < 900:
                return (
                    f"{self.config.emotes.success} The user has a history of using a slur detected in this "
                    f"message:\n{prev_offenses}"
                )

            else:
                return "`CASE LIST TOO LONG`"

        else:
            return f"{self.config.emotes.fail} The user is a first time offender."

    async def cb_action_taken(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Action Taken By", value=interaction.user.mention, inline=False
        )
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        await self.bot.get_channel(self.config.channels.logging).send(
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

        unique_id = case_history(self.config, member.id, "Slur Usage")
        slur_case(
            self.config,
            unique_id,
            case_data[1],
            interaction.message.jump_url,
            member.id,
            interaction.user.id,
        )

        await logutils.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    async def cb_acceptable_use(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Usage Deemed Acceptable By",
            value=interaction.user.mention,
            inline=False,
        )
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Acceptable Use Pressed",
                description="Usage of a slur has been deemed acceptable by a moderator in response to a report.",
                fields={
                    "Report:": interaction.message.jump_url,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                },
            )
        )

        await logutils.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    async def cb_false_positive(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Deemed As False Positive By:",
            value=interaction.user.mention,
            inline=False,
        )
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)
        channel = self.bot.get_channel(self.config.channels.false_positives)

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
        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="False Positive Pressed",
                description="Detected slur has been deemed a false positive by a moderator in response to a report.",
                fields={
                    "Report:": interaction.message.jump_url,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                },
            )
        )

        await logutils.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    # events
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.message.Message):
        if message.content.startswith(self.bot.command_prefix):
            return

        detected_slurs = detect_slur(message.content)

        if message.channel.category.name == "Administration Centre":
            # ignores message if sent inside the administration centre
            return

        if message.author == self.bot.user:
            # ignores message if message is by bot
            return

        elif len(detected_slurs) > 0:  # checks slur heat
            channel = self.bot.get_channel(self.config.channels.alert)

            if len(message.content) < 1024:
                citation = message.content
            else:
                citation = "`MESSAGE TOO LONG`"

            slurembed = SersiEmbed(
                title="Slur(s) Detected",
                description="A slur has been detected. Moderation action is advised.",
                footer="Sersi Slur Detection Alert",
                fields={
                    "Channel:": message.channel.mention,
                    "User:": message.author.mention,
                    "Context:": citation,
                    "Slurs Found:": ", ".join(set(detected_slurs)),
                    "URL:": message.jump_url,
                    "Previous Slur Uses:": self._get_previous_cases(
                        message.author.id, detected_slurs
                    ),
                },
            )

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            acceptable_use = Button(label="Acceptable Use")
            acceptable_use.callback = self.cb_acceptable_use

            false_positive = Button(label="False Positive")
            false_positive.callback = self.cb_false_positive

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.interaction_check = cb_is_mod

            alert = await channel.send(embed=slurembed, view=button_view)

            await logutils.create_alert_log(
                self.config, alert, logutils.AlertType.Slur, alert.created_at
            )

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)
            if (
                len(updated_message.embeds[0].fields) < 7
            ):  # If there are less than 7 fields that means there is no field for response
                await alert.reply(
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )

    @commands.Cog.listener()
    async def on_presence_update(self, before: nextcord.Member, after: nextcord.Member):

        slurs: list[str] = detect_slur(after.status)
        if slurs:

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            acceptable_use = Button(label="Acceptable Use")
            acceptable_use.callback = self.cb_acceptable_use

            false_positive = Button(label="False Positive")
            false_positive.callback = self.cb_false_positive

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.interaction_check = cb_is_mod

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
                        "Previous Slur Uses:": self._get_previous_cases(
                            after.id, slurs
                        ),
                    },
                ),
                view=button_view,
            )

            await logutils.create_alert_log(
                self.config, alert, logutils.AlertType.Slur, alert.created_at
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
            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            acceptable_use = Button(label="Acceptable Use")
            acceptable_use.callback = self.cb_acceptable_use

            false_positive = Button(label="False Positive")
            false_positive.callback = self.cb_false_positive

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.interaction_check = cb_is_mod

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
                        "Previous Slur Uses:": self._get_previous_cases(
                            after.id, slurs
                        ),
                    },
                ),
                view=button_view,
            )

            await logutils.create_alert_log(
                self.config, alert, logutils.AlertType.Slur, alert.created_at
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
            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            acceptable_use = Button(label="Acceptable Use")
            acceptable_use.callback = self.cb_acceptable_use

            false_positive = Button(label="False Positive")
            false_positive.callback = self.cb_false_positive

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.interaction_check = cb_is_mod

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
                        "Previous Slur Uses:": self._get_previous_cases(
                            after.id, slurs
                        ),
                    },
                ),
                view=button_view,
            )

            await logutils.create_alert_log(
                self.config, alert, logutils.AlertType.Slur, alert.created_at
            )

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)
            if not updated_message.edited_at:
                await alert.reply(
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )


def setup(bot, **kwargs):
    bot.add_cog(Slur(bot, kwargs["config"]))
