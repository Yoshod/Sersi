import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone

import nextcord
import requests
from nextcord.ext import commands
from nextcord.ui import Button, View

import discordTokens
import logutils
from baseutils import SersiEmbed
from configutils import Configuration
from permutils import cb_is_mod


@dataclass
class PerspectiveEvaluation:
    toxic: float
    flirt: float
    nsfw: float


class Perspective(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    def ask_perspective(self, message: str) -> PerspectiveEvaluation:

        response = requests.post(
            f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={discordTokens.getPerspectiveToken()}",
            json={
                "comment": {"text": message},
                "languages": ["en"],
                "requestedAttributes": {
                    "TOXICITY": {},
                    "FLIRTATION": {},
                    "SEXUALLY_EXPLICIT": {},
                },
                "doNotStore": True,
            },
            headers={"Content-Type": "application/json; charset=UTF-8"},
        )
        # fmt: off
        return PerspectiveEvaluation(
            toxic=response.json()["attributeScores"]["TOXICITY"]["summaryScore"]["value"],
            flirt=response.json()["attributeScores"]["FLIRTATION"]["summaryScore"]["value"],
            nsfw=response.json()["attributeScores"]["SEXUALLY_EXPLICIT"]["summaryScore"]["value"],
        )
        # fmt: on

    async def cb_action_taken(self, interaction):
        # update alert embed
        initial_alert = interaction.message.embeds[0]
        initial_alert.add_field(
            name="Action Taken By",
            value=interaction.user.mention,
            inline=False,
        )
        initial_alert.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=initial_alert, view=None)

        # Logging
        logging_embed = SersiEmbed(
            title="Action Taken on Perspective Alert Dismissed",
            description="Perspective has found a message to be problematic, action taken by moderators.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
        )
        sersi_logs = self.bot.get_channel(self.config.channels.logging)
        await sersi_logs.send(embed=logging_embed)

        await logutils.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    async def cb_dismiss(self, interaction):
        # update alert embed
        initial_alert = interaction.message.embeds[0]
        initial_alert.add_field(
            name="Dismissed By",
            value=interaction.user.mention,
            inline=False,
        )
        initial_alert.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=initial_alert, view=None)

        # Logging
        logging_embed = SersiEmbed(
            title="Perspective Alert Dismissed",
            description="Perspective has found a message to be problematic, dismissed by moderators.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
        )
        sersi_logs = self.bot.get_channel(self.config.channels.logging)
        await sersi_logs.send(embed=logging_embed)

        await logutils.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    async def cb_not_problematic(self, interaction):
        # update alert embed
        initial_alert = interaction.message.embeds[0]
        initial_alert.add_field(
            name="Not Problematic By",
            value=interaction.user.mention,
            inline=False,
        )
        initial_alert.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=initial_alert, view=None)

        # Logging
        logging_embed = SersiEmbed(
            title="Perspective Alert deemed Not Problematic",
            description="Perspective has found a message to be problematic, overruled by moderators.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
        )
        sersi_logs = self.bot.get_channel(self.config.channels.logging)
        await sersi_logs.send(embed=logging_embed)

        await logutils.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.message.Message):
        evaluation: PerspectiveEvaluation = self.ask_perspective(message.content)

        # ignores message if sent inside the administration centre
        if message.channel.category.name == "Administration Centre":
            return
        # ignores message if message is by bot
        elif message.author == self.bot.user:
            return

        # look for stuff here in the response
        problems: dict[str:float] = {}
        if evaluation.toxic >= 0.8:
            problems["toxicity"] = evaluation.toxic
        elif evaluation.flirt >= 0.95:
            problems["flirtation"] = evaluation.flirt
        elif evaluation.nsfw >= 0.8:
            problems["nsfw"] = evaluation.nsfw

        # stop here if there are no problems at all
        if not problems:
            return

        information_centre = self.bot.get_channel(self.config.channels.alert)

        if len(message.content) < 1024:
            citation: str = message.content
        else:
            citation: str = "`MESSAGE TOO LONG`"

        toxic_embed = SersiEmbed(
            title=f"AI dectected `{', '.join([value.upper() for value in problems])}` in Message!",
            description="Perspective AI has deemed a message to be problematic. Moderation action is advised.",
            footer="Sersi Problematic Message Detection Alert powered by Perspective API",
            fields={
                "Channel:": message.channel.mention,
                "User:": message.author.mention,
                "Message:": citation,
                "URL:": message.jump_url,
                "Confidence:": (
                    f"`Toxicity: {evaluation.toxic *100:.2f}%`\n"
                    f"`Flirtation: {evaluation.flirt *100:.2f}%`\n"
                    f"`Sexually Explicit: {evaluation.nsfw *100:.2f}%`\n"
                ),
            },
        )

        action_taken = Button(label="Action Taken")
        action_taken.callback = self.cb_action_taken

        dismiss = Button(label="Dismiss")
        dismiss.callback = self.cb_dismiss

        not_problematic = Button(label="Not Problematic")
        not_problematic.callback = self.cb_not_problematic

        button_view = View(timeout=None)
        button_view.add_item(action_taken)
        button_view.add_item(dismiss)
        button_view.add_item(not_problematic)
        button_view.interaction_check = cb_is_mod

        alert = await information_centre.send(embed=toxic_embed, view=button_view)

        await logutils.create_alert_log(
            self.config, alert, logutils.AlertType.Toxic, alert.created_at
        )

        await asyncio.sleep(10800)  # 3 hours
        updated_message = await alert.channel.fetch_message(alert.id)
        # If there are less than 6 fields that means there is no field for response
        if len(updated_message.embeds[0].fields) < 6:
            await alert.reply(
                f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
            )


def setup(bot, **kwargs):
    bot.add_cog(Perspective(bot, kwargs["config"]))
