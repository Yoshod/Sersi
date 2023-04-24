import asyncio
from datetime import datetime, timezone
import re

import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View

import logutils
from baseutils import sanitize_mention, SersiEmbed, PageView
from caseutils import slur_history, slur_virgin, create_slur_case, fetch_offender_cases
from configutils import Configuration
from permutils import cb_is_mod
from slurdetector import (
    load_slurdetector,
    detect_slur,
)
from noteutils import get_note_by_user


def format_entry(entry):
    if len(entry[3]) >= 16:
        return "`{}`... <t:{}:R>".format(entry[3][:15], entry[4])
    else:
        return "`{}` <t:{}:R>".format(entry[3], entry[4])


class Slur(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail
        load_slurdetector()

    def _get_previous_cases(self, user: nextcord.Member, slurs: list[str]) -> str:
        print("Im fucking gayer")
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
                prev_offences = f"{self.config.emotes.success} The user has a history of using a slur detected in this message:"
                for slur_cases in cases:
                    prev_offences += f"\n`{slur_cases[0]}` {slur_cases[2]}"

                return prev_offences

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

        timestamp = datetime.now(timezone.utc)

        create_slur_case(
            self.config,
            case_data[1],
            interaction.message.jump_url,
            member,
            interaction.user,
        )

        await logutils.update_response(self.config, interaction.message, timestamp)

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

    async def cb_view_cases(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        original_embed = interaction.message.embeds[0]

        for field in original_embed.fields:
            if field.name.lower() == "user:":
                offender = interaction.guild.get_member(
                    int(re.sub(r"\D", "", field.value))
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

    async def cb_view_notes(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)

        original_embed = interaction.message.embeds[0]

        for field in original_embed.fields:
            if field.name.lower() == "user:":
                user = interaction.guild.get_member(int(re.sub(r"\D", "", field.value)))
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
            if len(message.content) < 1024:
                citation = message.content
            else:
                citation = "`MESSAGE TOO LONG`"

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            acceptable_use = Button(label="Acceptable Use")
            acceptable_use.callback = self.cb_acceptable_use

            false_positive = Button(label="False Positive")
            false_positive.callback = self.cb_false_positive

            view_cases = Button(label="View Slur Cases", row=1)
            view_cases.callback = self.cb_view_cases

            view_notes = Button(label="View Notes", row=1)
            view_notes.callback = self.cb_view_notes

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.add_item(view_cases)
            button_view.add_item(view_notes)
            button_view.interaction_check = cb_is_mod

            print("Im fucking gay")

            alert = await self.bot.get_channel(self.config.channels.alert).send(
                embed=SersiEmbed(
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
                            message.author, detected_slurs
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

            view_cases = Button(label="View Slur Cases", row=1)
            view_cases.callback = self.cb_view_cases

            view_notes = Button(label="View Notes", row=1)
            view_notes.callback = self.cb_view_notes

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.add_item(view_cases)
            button_view.add_item(view_notes)
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
                        "Previous Slur Uses:": self._get_previous_cases(after, slurs),
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

            view_cases = Button(label="View Slur Cases", row=1)
            view_cases.callback = self.cb_view_cases

            view_notes = Button(label="View Notes", row=1)
            view_notes.callback = self.cb_view_notes

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.add_item(view_cases)
            button_view.add_item(view_notes)
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
                        "Previous Slur Uses:": self._get_previous_cases(after, slurs),
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

            view_cases = Button(label="View Slur Cases", row=1)
            view_cases.callback = self.cb_view_cases

            view_notes = Button(label="View Notes", row=1)
            view_notes.callback = self.cb_view_notes

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(acceptable_use)
            button_view.add_item(false_positive)
            button_view.add_item(view_cases)
            button_view.add_item(view_notes)
            button_view.interaction_check = cb_is_mod

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
