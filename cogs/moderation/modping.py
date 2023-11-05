import asyncio
from datetime import datetime, timezone

import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View

from utils import logs
from utils.sersi_embed import SersiEmbed
from utils.base import (
    modmention_check,
    convert_mention_to_id,
    ignored_message,
)
from utils.config import Configuration
from utils.database import db_session, BadFaithPingCase
from utils.perms import cb_is_mod


# from caseutils import case_history, bad_faith_ping_case


class ModPing(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    async def cb_action_taken(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Action Taken By", value=interaction.user.mention, inline=True
        )
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        logging_embed = SersiEmbed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
            footer="Sersi Moderator Ping Detection",
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=logging_embed)

        await logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    async def cb_action_not_necessary(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Action Not Necessary", value=interaction.user.mention, inline=True
        )
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        logging_embed = SersiEmbed(
            title="Action Not Necessary Pressed",
            description="A Moderator has deemed that no action is needed in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
            footer="Sersi Moderator Ping Detection",
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=logging_embed)

        await logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    async def cb_bad_faith_ping(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Bad Faith Ping", value=interaction.user.mention, inline=True
        )
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        logging_embed = SersiEmbed(
            title="Bad Faith Ping Pressed",
            description="A moderation ping has been deemed bad faith by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
            footer="Sersi Moderator Ping Detection",
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=logging_embed)

        for field in new_embed.fields:
            if field.name in ["User:"]:
                offender = interaction.guild.get_member(
                    convert_mention_to_id(field.value)
                )

        with db_session(interaction.user) as session:
            session.add(
                BadFaithPingCase(
                    offender=offender.id,
                    moderator=interaction.user.id,
                    report_url=interaction.message.jump_url,
                )
            )
            session.commit()

        await logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
            return

        if modmention_check(self.config, message.content):
            # Reply to user
            response_embed: nextcord.Embed = SersiEmbed(
                title="Moderator Ping Acknowledgment",
                description=f"{message.author.mention} moderators have been notified of your ping and will investigate when able to do so.",
                footer="Sersi Moderator Ping Detection",
            )
            await message.channel.send(embed=response_embed)
            await message.channel.send(
                message.guild.get_role(
                    self.config.permission_roles.trial_moderator
                ).mention,
                delete_after=1,
            )

            # notification for mods
            channel = self.bot.get_channel(self.config.channels.alert)
            alert_embed: nextcord.Embed = SersiEmbed(
                title="Moderator Ping",
                description="A moderation role has been pinged, please investigate the ping and take action as appropriate.",
                fields={
                    "Channel:": message.channel.mention,
                    "User:": message.author.mention,
                    "Context:": message.content,
                    "URL:": message.jump_url,
                },
                footer="Sersi Moderator Ping Detection",
            )

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            action_not_necessary = Button(label="Action Not Necessary")
            action_not_necessary.callback = self.cb_action_not_necessary

            bad_faith_ping = Button(label="Bad Faith Ping")
            bad_faith_ping.callback = self.cb_bad_faith_ping

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(action_not_necessary)
            button_view.add_item(bad_faith_ping)
            button_view.interaction_check = cb_is_mod

            alert = await channel.send(embed=alert_embed, view=button_view)

            await logs.create_alert_log(
                self.config, alert, logs.AlertType.Ping, alert.created_at
            )

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)
            # If there are less than 5 fields that means there is no field for response
            if len(updated_message.embeds[0].fields) < 5:
                await alert.reply(
                    content=f"{message.guild.get_role(self.config.permission_roles.moderator).mention} This alert has not had a recorded response."
                )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(ModPing(bot, kwargs["config"]))
