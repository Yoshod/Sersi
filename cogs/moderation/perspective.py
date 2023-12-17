import asyncio
from dataclasses import dataclass

import nextcord
import requests
from nextcord.ext import commands
from nextcord.ui import Button, View

import discordTokens
from utils.alerts import add_response_time, create_alert_log, AlertType
from utils.sersi_embed import SersiEmbed
from utils.base import ignored_message
from utils.config import Configuration
from utils.perms import cb_is_mod


@dataclass
class PerspectiveEvaluation:
    toxic: float
    flirt: float
    nsfw: float
    severe_toxic: float
    identity_attack: float
    insult: float
    profanity: float
    threat: float
    incoherent: float
    spam: float
    unsubstantial: float
    obscene: float
    inflammatory: float
    likely_to_reject: float


class Perspective(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    async def ask_perspective(
        self, message: str, attributes: list[str] = None
    ) -> PerspectiveEvaluation:
        if not attributes:
            attributes = ["TOXICITY"]

        response = requests.post(
            f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={discordTokens.getPerspectiveToken()}",
            json={
                "comment": {"text": message},
                "languages": ["en"],
                "requestedAttributes": {attr.upper(): {} for attr in attributes},
                "doNotStore": True,
            },
            headers={"Content-Type": "application/json; charset=UTF-8"},
        )
        if response.status_code == 200:

            def evaluation(attr):
                if attr not in response.json()["attributeScores"]:
                    return -0.0
                return response.json()["attributeScores"][attr]["summaryScore"]["value"]

            return PerspectiveEvaluation(
                toxic=evaluation("TOXICITY"),
                flirt=evaluation("FLIRTATION"),
                nsfw=evaluation("SEXUALLY_EXPLICIT"),
                severe_toxic=evaluation("SEVERE_TOXICITY"),
                identity_attack=evaluation("IDENTITY_ATTACK"),
                insult=evaluation("INSULT"),
                profanity=evaluation("PROFANITY"),
                threat=evaluation("THREAT"),
                incoherent=evaluation("INCOHERENT"),
                spam=evaluation("SPAM"),
                unsubstantial=evaluation("UNSUBSTANTIAL"),
                obscene=evaluation("OBSCENE"),
                inflammatory=evaluation("INFLAMMATORY"),
                likely_to_reject=evaluation("LIKELY_TO_REJECT"),
            )
        else:
            error_channel = self.bot.get_channel(self.config.channels.errors)
            error_embed = SersiEmbed(
                title="Perspective Error",
                fields=response.json()["error"],
                colour=nextcord.Colour.brand_red(),
            )
            await error_channel.send(embed=error_embed)

    @commands.command(aliases=["inv"])
    async def investigate(self, context: commands.Context, *, message: str):
        """Investigate a message for toxicity."""
        evaluation: PerspectiveEvaluation = await self.ask_perspective(
            message,
            [
                "SEVERE_TOXICITY",
                "FLIRTATION",
                "SEXUALLY_EXPLICIT",
                "TOXICITY",
                "IDENTITY_ATTACK",
                "INSULT",
                "PROFANITY",
                "THREAT",
                "INCOHERENT",
                "SPAM",
                "UNSUBSTANTIAL",
                "OBSCENE",
                "INFLAMMATORY",
                "LIKELY_TO_REJECT",
            ],
        )

        await context.reply(
            (
                f"`Toxicity: {evaluation.toxic *100:.2f}%`\n"
                f"`Flirtation: {evaluation.flirt *100:.2f}%`\n"
                f"`Sexually Explicit: {evaluation.nsfw *100:.2f}%`\n"
                f"`Severe Toxicity: {evaluation.severe_toxic *100:.2f}%`\n"
                f"`Identity Attack: {evaluation.identity_attack *100:.2f}%`\n"
                f"`Insult: {evaluation.insult *100:.2f}%`\n"
                f"`Profanity: {evaluation.profanity *100:.2f}%`\n"
                f"`Threat: {evaluation.threat *100:.2f}%`\n"
                f"`Incoherent: {evaluation.incoherent *100:.2f}%`\n"
                f"`Spam: {evaluation.spam *100:.2f}%`\n"
                f"`Unsubstantial: {evaluation.unsubstantial *100:.2f}%`\n"
                f"`Obscene: {evaluation.obscene *100:.2f}%`\n"
                f"`Inflammatory: {evaluation.inflammatory *100:.2f}%`\n"
                f"`Likely to Reject: {evaluation.likely_to_reject *100:.2f}%`\n"
            )
        )

    async def cb_action_taken(self, interaction: nextcord.Interaction):
        """Is a Callback for when the action taken button is pressed."""
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

        add_response_time(interaction.message)

    async def cb_dismiss(self, interaction: nextcord.Interaction):
        """Is a Callback for when the dismiss button is pressed."""
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

        add_response_time(interaction.message)

    async def cb_not_problematic(self, interaction: nextcord.Interaction):
        """Is a Callback for when the not problematic button is pressed."""
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

        add_response_time(interaction.message)

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.message.Message):
        if ignored_message(self.config, message):
            return

        if len(message.content) < 10:
            return
        # ignores message if sent outside general chat.
        if (
            not message.channel.id == 856262304337100832
            and message.guild.id == 856262303795380224
        ):
            return

        evaluation: PerspectiveEvaluation = await self.ask_perspective(
            message.content, ["TOXICITY", "FLIRTATION", "SEXUALLY_EXPLICIT"]
        )
        # exit if error has occured
        if evaluation is None:
            return

        # look for stuff here in the response
        problems: list[str] = []
        if evaluation.toxic >= 0.9:
            problems.append("toxicity")
        elif evaluation.flirt >= 0.95:
            problems.append("flirtation")
        elif evaluation.nsfw >= 0.9:
            problems.append("nsfw")

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

        create_alert_log(message, AlertType.Toxic)

        await asyncio.sleep(10800)  # 3 hours
        updated_message = await alert.channel.fetch_message(alert.id)
        # If there are less than 6 fields that means there is no field for response
        if len(updated_message.embeds[0].fields) < 6:
            await alert.reply(
                f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
            )


def setup(bot: commands.Bot, **kwargs):
    if kwargs["config"].bot.dev_mode:
        bot.add_cog(Perspective(bot, kwargs["config"]))
