import nextcord
import asyncio

from nextcord.ext import commands
from nextcord.ui import Button, View
from datetime import datetime, timezone

import utils
from utils import logs
from utils.base import modmention_check, SersiEmbed, convert_mention_to_id
from utils.perms import cb_is_mod
from utils.cases import create_bad_faith_ping_case
from utils.config import Configuration

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

        create_bad_faith_ping_case(
            self.config, interaction.message.jump_url, offender, interaction.user
        )

        await logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is not None:
            adam_something = message.guild.get_member(809891646606409779)
        else:
            return  # ignores message if it is a DM

        if message.author.bot:  # ignores message if message is by bot
            return

        if message.channel.category.name in [
            "Important stuff",
            "Administration Centre",
            "The Staff Zone",
            "The Mod Zone",
            "The CET Zone",
            "Moderation Support",
        ]:
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
                f"<@&{self.config.permission_roles.trial_moderator}>", delete_after=1
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
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )

        elif (
            adam_something is not None
            and adam_something.mentioned_in(message)
            and not message.mention_everyone
            and message.type is not nextcord.MessageType.reply
        ):  # adam something ping
            channel = self.bot.get_channel(self.config.channels.alert)
            alert_embed: nextcord.Embed = SersiEmbed(
                title="Adam Something Ping",
                description="Some pleb just thought they were good enough to ping our benevolent server owner, "
                "Adam Something.",
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

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(action_not_necessary)
            button_view.interaction_check = cb_is_mod

            alert = await channel.send(embed=alert_embed, view=button_view)

            await asyncio.sleep(10800)  # 3 hours
            updated_message = await alert.channel.fetch_message(alert.id)

            # If there are less than 5 fields that means there is no field for response
            if len(updated_message.embeds[0].fields) < 5:
                await alert.reply(
                    content=f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response."
                )


def setup(bot, **kwargs):
    bot.add_cog(ModPing(bot, kwargs["config"]))
