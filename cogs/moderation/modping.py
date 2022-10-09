import nextcord
import asyncio

from nextcord.ext import commands
from nextcord.ui import Button, View

from baseutils import modmention_check, SersiEmbed
from permutils import cb_is_mod
from configutils import Configuration
from caseutils import case_history, bad_faith_ping_case


class ModPing(commands.Cog):

    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    async def cb_action_taken(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        embedLogVar = SersiEmbed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})"
            })

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=embedLogVar)

    async def cb_action_not_neccesary(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Not Neccesary", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        embedLogVar = SersiEmbed(
            title="Action Not Necessary Pressed",
            description="A Moderator has deemed that no action is needed in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})"
            })

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=embedLogVar)

    async def cb_bad_faith_ping(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Bad Faith Ping", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        embedLogVar = SersiEmbed(
            title="Bad Faith Ping Pressed",
            description="A moderation ping has been deemed bad faith by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})"
            })

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=embedLogVar)

        case_data = []
        for field in new_embed.fields:
            if field.name in ["User:"]:
                case_data.append(field.value)

        member = interaction.guild.get_member(case_data[0])

        unique_id = case_history(self.config, member.id, "Bad Faith Ping")
        bad_faith_ping_case(self.config, unique_id, interaction.message.jump_url, member.id, interaction.user.id)

    # events
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild is not None:
            adam_something = message.guild.get_member(809891646606409779)
        else:
            return              # ignores message if it is a DM

        if message.author.bot:  # ignores message if message is by bot
            return

        if message.channel.category.name in ["Important stuff", "Administration Centre", "The Staff Zone"]:  # ignores certain channels on ASC, given by Juniper
            return

        if modmention_check(self.config, message.content):
            # Reply to user
            embedVar = SersiEmbed(
                title="Moderator Ping Acknowledgment",
                description=f"{message.author.mention} moderators have been notified of your ping and will investigate when able to do so.",
                footer="Sersi Ping Detection Alert")
            await message.channel.send(embed=embedVar)
            await message.channel.send(f"<@&{self.config.permission_roles.trial_moderator}>", delete_after=1)

            # notification for mods
            channel = self.bot.get_channel(self.config.channels.alert)
            embedVar = SersiEmbed(
                title="Moderator Ping",
                description="A moderation role has been pinged, please investigate the ping and take action as appropriate.",
                fields={
                    "Channel:": message.channel.mention,
                    "User:": message.author.mention,
                    "Context:": message.content,
                    "URL:": message.jump_url
                },
                footer="Sersi Ping Detection Alert")

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            action_not_neccesary = Button(label="Action Not Neccesary")
            action_not_neccesary.callback = self.cb_action_not_neccesary

            bad_faith_ping = Button(label="Bad Faith Ping")
            bad_faith_ping.callback = self.cb_bad_faith_ping

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(action_not_neccesary)
            button_view.add_item(bad_faith_ping)
            button_view.interaction_check = cb_is_mod

            alert = await channel.send(embed=embedVar, view=button_view)

            await asyncio.sleep(10800)  # 3 hours
            if alert.components:  # message has components like ActionRow, Button, SelectMenu
                await alert.reply(content=f"<@&{self.config.permission_roles.moderator}> untreated alert.")

        # elif "<@809891646606409779>" in message.content:   # adam something ping

        elif adam_something is not None and adam_something.mentioned_in(message) and not message.mention_everyone:  # adam something ping

            # notification for mods
            channel = self.bot.get_channel(self.config.channels.alert)
            embedVar = SersiEmbed(
                title="Moderator Ping",
                description="A moderation role has been pinged, please investigate the ping and take action as appropriate.",
                fields={
                    "Channel:": message.channel.mention,
                    "User:": message.author.mention,
                    "Context:": message.content,
                    "URL:": message.jump_url
                },
                footer="Sersi Ping Detection Alert")

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            action_not_neccesary = Button(label="Action Not Neccesary")
            action_not_neccesary.callback = self.cb_action_not_neccesary

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(action_not_neccesary)
            button_view.interaction_check = cb_is_mod

            alert = await channel.send(embed=embedVar, view=button_view)

            await asyncio.sleep(10800)  # 3 hours
            if alert.components:  # message has components like ActionRow, Button, SelectMenu
                await alert.reply(content=f"<@&{self.config.permission_roles.moderator}> untreated alert.")


def setup(bot, **kwargs):
    bot.add_cog(ModPing(bot, kwargs["config"]))
