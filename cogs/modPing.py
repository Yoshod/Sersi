import nextcord
from baseutils import *

from nextcord.ext import commands
from nextcord.ui import Button, View


class ModPing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cb_action_taken(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
        embedLogVar = nextcord.Embed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.\n\n__Report:__\n"
            + str(interaction.message.jump_url)
            + "\n\n__Moderator:__\n"
            + f"{interaction.user.mention} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        await channel.send(embed=embedLogVar)

    async def cb_action_not_neccesary(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Not Neccesary", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
        embedLogVar = nextcord.Embed(
            title="Action Not Necessary Pressed",
            description="A Moderator has deemed that no action is needed in response to a report.\n\n__Report:__\n"
            + str(interaction.message.jump_url)
            + "\n\n__Moderator:__\n"
            + f"{interaction.user.mention} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        await channel.send(embed=embedLogVar)

    async def cb_bad_faith_ping(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Bad Faith Ping", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
        embedLogVar = nextcord.Embed(
            title="Bad Faith Ping Pressed",
            description="A moderation ping has been deemed bad faith by a moderator in response to a report.\n\n__Report:__\n"
            + str(interaction.message.jump_url)
            + "\n\n__Moderator:__\n"
            + f"{interaction.user.mention} ({interaction.user.id})",
            color=nextcord.Color.from_rgb(237, 91, 6))
        await channel.send(embed=embedLogVar)

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:  # ignores message if message is by bot
            return

        elif checkForMods(message.content):
            # Reply to user
            embedVar = nextcord.Embed(
                title="Moderator Ping Acknowledgment",
                description=(message.author.mention) + " moderators have been notified of your ping and will investigate when able to do so.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.set_footer(text="Sersi Ping Detection Alert")
            await message.channel.send(embed=embedVar)
            await message.channel.send("<@&883255791610638366>", delete_after=0.1)

            # notification for mods
            channel = self.bot.get_channel(getAlertChannel(message.guild.id))
            embedVar = nextcord.Embed(
                title="Moderator Ping",
                description="A moderation role has been pinged, please investigate the ping and take action as appropriate.\n\n__Channel:__\n"
                + str(message.channel.mention)
                + "\n\n__User:__\n"
                + str(message.author.mention)
                + "\n\n__Context:__\n"
                + str(message.content)
                + "\n\n__URL:__\n"
                + str(message.jump_url),
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.set_footer(text="Sersi Ping Detection Alert")

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

            await channel.send(embed=embedVar, view=button_view)


def setup(bot):
    bot.add_cog(ModPing(bot))
