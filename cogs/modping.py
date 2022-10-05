import nextcord

from nextcord.ext import commands
from nextcord.ui import Button, View

from baseutils import modmention_check
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
        channel = self.bot.get_channel(self.config.channels.logging)
        embedLogVar = nextcord.Embed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_action_not_neccesary(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Not Neccesary", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedLogVar = nextcord.Embed(
            title="Action Not Necessary Pressed",
            description="A Moderator has deemed that no action is needed in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_bad_faith_ping(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Bad Faith Ping", value=interaction.user.mention, inline=True)
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)
        # Logging
        channel = self.bot.get_channel(self.config.channels.logging)
        embedLogVar = nextcord.Embed(
            title="Bad Faith Ping Pressed",
            description="A moderation ping has been deemed bad faith by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

        case_data = []
        for field in new_embed.fields:
            if field.name in ["User:"]:
                case_data.append(field.value)

        converter = commands.MemberConverter()
        member = await converter.convert(self, case_data[0])

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

        elif message.channel.category.name in ["Important stuff", "Administration Centre", "The Staff Zone"]:  # ignores certain channels on ASC, given by Juniper
            return

        elif modmention_check(self.config, message.content):
            # Reply to user
            embedVar = nextcord.Embed(
                title="Moderator Ping Acknowledgment",
                description=f"{message.author.mention} moderators have been notified of your ping and will investigate when able to do so.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.set_footer(text="Sersi Ping Detection Alert")
            await message.channel.send(embed=embedVar)
            await message.channel.send(f"<@&{self.config.permission_roles.trial_moderator}>", delete_after=1)

            # notification for mods
            channel = self.bot.get_channel(self.config.channels.alert)
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
            button_view.interaction_check = cb_is_mod

            await channel.send(embed=embedVar, view=button_view)

        # elif "<@809891646606409779>" in message.content:   # adam something ping

        elif adam_something is not None and adam_something.mentioned_in(message) and not message.mention_everyone:  # adam something ping

            # notification for mods
            channel = self.bot.get_channel(self.config.channels.alert)
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

            action_not_neccesary = Button(label="Action Not Neccesary")
            action_not_neccesary.callback = self.cb_action_not_neccesary

            button_view = View(timeout=None)
            button_view.add_item(action_taken)
            button_view.add_item(action_not_neccesary)
            button_view.interaction_check = cb_is_mod

            await channel.send(embed=embedVar, view=button_view)


def setup(bot, **kwargs):
    bot.add_cog(ModPing(bot, kwargs["config"]))
