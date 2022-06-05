import nextcord
from baseutils import *

from nextcord.ext import commands
from nextcord.ui import Button, View


class ModPing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cb_action_taken(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("You don't get to decide on this", ephemeral=True)
            return

        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
        embedLogVar = nextcord.Embed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_action_not_neccesary(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("You don't get to decide on this", ephemeral=True)
            return

        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Not Neccesary", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
        embedLogVar = nextcord.Embed(
            title="Action Not Necessary Pressed",
            description="A Moderator has deemed that no action is needed in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_bad_faith_ping(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("You don't get to decide on this", ephemeral=True)
            return

        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Bad Faith Ping", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
        embedLogVar = nextcord.Embed(
            title="Bad Faith Ping Pressed",
            description="A moderation ping has been deemed bad faith by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:  # ignores message if message is by bot
            return

        elif message.channel.id in [875807914802176020, 963893512141692958, 856430951630110740]:  # ignores certain channels on ASC, given by Juniper
            return

        elif checkForMods(message.content):
            # Reply to user
            embedVar = nextcord.Embed(
                title="Moderator Ping Acknowledgment",
                description=f"{message.author.mention} moderators have been notified of your ping and will investigate when able to do so.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.set_footer(text="Sersi Ping Detection Alert")
            await message.channel.send(embed=embedVar)
            await message.channel.send("<@&883255791610638366>", delete_after=0.1)

            # notification for mods
            channel = self.bot.get_channel(getAlertChannel(message.guild.id))
            embedVar = nextcord.Embed(
                title="Moderator Ping",
                description="A moderation role has been pinged, please investigate the ping and take action as appropriate.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.add_field(name="Channel:", value=message.channel.mention, inline=False)
            embedVar.add_field(name="User:", value=message.author.mention, inline=False)
            embedVar.add_field(name="Context:", value=message.content, inline=False)
            embedVar.add_field(name="URL:", value=message.jump_url, inline=False)
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

        elif "<@809891646606409779>" in message.content:   # adam something ping

            # notification for mods
            channel = self.bot.get_channel(getAlertChannel(message.guild.id))
            embedVar = nextcord.Embed(
                title="Adam Something Ping",
                description="Adam Something has been pinged, please take appropriate action.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.add_field(name="Channel:", value=message.channel.mention, inline=False)
            embedVar.add_field(name="User:", value=message.author.mention, inline=False)
            embedVar.add_field(name="Context:", value=message.content, inline=False)
            embedVar.add_field(name="URL:", value=message.jump_url, inline=False)
            embedVar.set_footer(text="Sersi Ping Detection Alert")

            action_taken = Button(label="Action Taken")
            action_taken.callback = self.cb_action_taken

            button_view = View(timeout=None)
            button_view.add_item(action_taken)

            await channel.send(embed=embedVar, view=button_view)


def setup(bot):
    bot.add_cog(ModPing(bot))
