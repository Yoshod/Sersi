import asyncio
from datetime import datetime, timezone

import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View

import logutils
from baseutils import SersiEmbed
from configutils import Configuration
from permutils import cb_is_mod


class Perspective(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config

    def ask_perspective(self, message: str):
        # stuff here
        return ...

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
            title="Action Taken on Toxicity",
            description="Perspective has found a message to be toxic, action taken by moderators.",
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
            title="Action Taken on Toxicity",
            description="Perspective has found a message to be toxic, action taken by moderators.",
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

    async def cb_not_toxic(self, interaction):
        # update alert embed
        initial_alert = interaction.message.embeds[0]
        initial_alert.add_field(
            name="Action Taken By",
            value=interaction.user.mention,
            inline=False,
        )
        initial_alert.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=initial_alert, view=None)

        # Logging
        logging_embed = SersiEmbed(
            title="Action Taken on Toxicity",
            description="Perspective has found a message to be toxic, action taken by moderators.",
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
        detected_slurs = self.ask_perspective(message.content)

        # ignores message if sent inside the administration centre
        if message.channel.category.name == "Administration Centre":
            return
        # ignores message if message is by bot
        elif message.author == self.bot.user:
            return

        # look for stuff here in the response
        elif len(detected_slurs) > 0:
            information_centre = self.bot.get_channel(self.config.channels.alert)

            if len(message.content) < 1024:
                citation: str = message.content
            else:
                citation: str = "`MESSAGE TOO LONG`"

            toxic_embed = SersiEmbed(
                title="Toxicity Detected (AI)",
                description="Perspective AI has deemed a message to contain toxicity. Moderation action is advised.",
                footer="Sersi Toxicity Detection Alert powered by Perspective API",
                fields={
                    "Channel:": message.channel.mention,
                    "User:": message.author.mention,
                    "Message:": citation,
                    "URL:": message.jump_url,
                },
            )



            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            dismiss = Button(label="Dismiss")
            dismiss.callback = self.cb_dismiss

            not_toxic = Button(label="Not Toxic")
            not_toxic.callback = self.cb_not_toxic

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(dismiss)
            button_view.add_item(not_toxic)
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
