from nextcord.ext import commands
from utils.config import Configuration
import datetime
import pytz
from utils.perms import is_dark_mod, permcheck
from utils.sersi_embed import SersiEmbed
from nextcord.ui import View, Select
import nextcord


class Roles(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def add_roles(self, ctx):
        """Single use Command for the 'Add Roles' Embed."""
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        interests_embed = SersiEmbed(
            title="Channel Opt-Ins",
            description="Select extra channels you wish to opt-in to seeing.",
        )

        interests_options = [
            nextcord.SelectOption(
                label="Gaming",
                description="Access to the Gaming related channels",
                emoji="🎮",
                value="gaming",
            ),
            nextcord.SelectOption(
                label="TechCompsci",
                description="Access to the Tech and Computer Science related channels",
                emoji="🖥️",
                value="tech",
            ),
            nextcord.SelectOption(
                label="Food & Housework",
                description="Access to the Food and Housework related channels",
                emoji="🍹",
                value="food",
            ),
            nextcord.SelectOption(
                label="History",
                description="Access to the History related channels",
                emoji="🏰",
                value="history",
            ),
            nextcord.SelectOption(
                label="Art Writing & Creativity",
                description="Access to the Art, Writing, and other Creative related channels",
                emoji="🎨",
                value="art",
            ),
            nextcord.SelectOption(
                label="Anime & Manga",
                description="Access to the Anime and Manga related channels",
                emoji="🏯",
                value="anime",
            ),
            nextcord.SelectOption(
                label="Furry",
                description="Access to the Furry related channels",
                emoji="🐾",
                value="furry",
            ),
            nextcord.SelectOption(
                label="Models",
                description="Access to the Modelling related channels",
                emoji="🖌️",
                value="models",
            ),
            nextcord.SelectOption(
                label="Shillposting",
                description="Access to the Shillposting related channels",
                emoji="💸",
                value="shillposting",
            ),
            nextcord.SelectOption(
                label="Photography",
                description="Access to the Photography related channels",
                emoji="📷",
                value="photo",
            ),
            nextcord.SelectOption(
                label="Environment",
                description="Access to the Environment related channels",
                emoji="♻️",
                value="enviro",
            ),
        ]

        interests_dropdown = Select(
            options=interests_options,
            placeholder="Interests",
        )

        button_view = View(auto_defer=False)
        button_view.add_item(interests_dropdown)

        await ctx.send(embed=interests_embed, view=button_view)

        # Colour Roles
        colours_embed = SersiEmbed(
            title="Colour Roles",
            description="Select the colour you wish your username to show.",
        )

        colour_options = [
            nextcord.SelectOption(
                label="Light Red",
                description="Light Red",
                value="l_red",
            ),
            nextcord.SelectOption(
                label="Red",
                description="Red",
                value="red",
            ),
            nextcord.SelectOption(
                label="Dark Red",
                description="Dark Red",
                value="d_red",
            ),
            nextcord.SelectOption(
                label="Light Orange",
                description="Light Orange",
                value="l_orange",
            ),
            nextcord.SelectOption(
                label="Orange",
                description="Orange",
                value="orange",
            ),
            nextcord.SelectOption(
                label="Dark Orange",
                description="Dark Orange",
                value="d_orange",
            ),
            nextcord.SelectOption(
                label="Light Yellow",
                description="Light Yellow",
                value="l_yellow",
            ),
            nextcord.SelectOption(
                label="Yellow",
                description="Yellow",
                value="yellow",
            ),
            nextcord.SelectOption(
                label="Dark Yellow",
                description="Dark Yellow",
                value="d_yellow",
            ),
            nextcord.SelectOption(
                label="Light Green",
                description="Light Green",
                value="l_green",
            ),
            nextcord.SelectOption(
                label="Green",
                description="Green",
                value="green",
            ),
            nextcord.SelectOption(
                label="Dark Green",
                description="Dark Green",
                value="d_green",
            ),
            nextcord.SelectOption(
                label="Light Blue",
                description="Light Blue",
                value="l_blue",
            ),
            nextcord.SelectOption(
                label="Blue",
                description="Blue",
                value="blue",
            ),
            nextcord.SelectOption(
                label="Dark Blue",
                description="Dark Blue",
                value="d_blue",
            ),
            nextcord.SelectOption(
                label="Light Purple",
                description="Light Purple",
                value="l_purple",
            ),
            nextcord.SelectOption(
                label="Purple",
                description="Purple",
                value="purple",
            ),
            nextcord.SelectOption(
                label="Dark Purple",
                description="Dark Purple",
                value="d_purple",
            ),
            nextcord.SelectOption(
                label="Light Pink",
                description="Light Pink",
                value="l_pink",
            ),
            nextcord.SelectOption(
                label="Pink",
                description="Pink",
                value="pink",
            ),
            nextcord.SelectOption(
                label="Dark Pink",
                description="Dark Pink",
                value="d_pink",
            ),
        ]

        colour_dropdown = Select(
            options=colour_options, placeholder="Colours", max_values=1
        )

        button_view = View(auto_defer=False)
        button_view.add_item(colour_dropdown)

        await ctx.send(embed=colours_embed, view=button_view)

        # Ping Roles
        ping_embed = SersiEmbed(
            title="Notification Roles",
            description="Select the pingable roles you want.",
        )

        ping_options = [
            nextcord.SelectOption(
                label="Server Updates",
                description="Whenever there's server changes",
                value="server_updates",
            ),
            nextcord.SelectOption(
                label="Server Events",
                description="Whenever we host events e.g. agario",
                value="server_events",
            ),
            nextcord.SelectOption(
                label="Voice Chat",
                description="Can be pinged by anyone looking to voice chat",
                value="voice_chat",
            ),
            nextcord.SelectOption(
                label="Question of The Week",
                description="Our sometimes more often than weekly question",
                value="qotw",
            ),
        ]

        ping_dropdown = Select(options=ping_options, placeholder="Notification Roles")

        button_view = View(auto_defer=False)
        button_view.add_item(ping_dropdown)

        await ctx.send(embed=ping_embed, view=button_view)

        # Pronoun Roles
        pronouns_embed = SersiEmbed(
            title="Pronoun Roles",
            description="Select the pronouns which apply to you.",
        )

        pronoun_options = [
            nextcord.SelectOption(
                label="Any/All",
                value="anyall",
            ),
            nextcord.SelectOption(
                label="He/Him",
                value="hehim",
            ),
            nextcord.SelectOption(
                label="He/They",
                value="hethey",
            ),
            nextcord.SelectOption(
                label="They/Them",
                value="theythem",
            ),
            nextcord.SelectOption(
                label="She/They",
                value="shethey",
            ),
            nextcord.SelectOption(
                label="She/Her",
                value="sheher",
            ),
            nextcord.SelectOption(
                label="Ask For Pronouns",
                value="askme",
            ),
            nextcord.SelectOption(
                label="Questioning",
                value="unsure",
            ),
            nextcord.SelectOption(
                label="Nouns Only | No Pronouns",
                value="nopronouns",
            ),
        ]

        pronoun_dropdown = Select(
            options=pronoun_options, placeholder="Pronouns", max_values=1
        )

        button_view = View(auto_defer=False)
        button_view.add_item(pronoun_dropdown)

        await ctx.send(embed=pronouns_embed, view=button_view)

        # Gendered Terms Roles
        gendered_terms_embed = SersiEmbed(
            title="Gendered Terms Roles",
            description="Select the gendered terms you are comfortable or not comfortable with.",
        )

        terms_options = [
            nextcord.SelectOption(
                label="Dude Positve",
                description="You are okay being referred to as dude",
                value="dude_positive",
            ),
            nextcord.SelectOption(
                label="Dude Negative",
                description="You are not okay being referred to as dude",
                value="dude_negative",
            ),
            nextcord.SelectOption(
                label="Guys Positive",
                description="In a group context you are okay being referred to as a guy",
                value="guys_positive",
            ),
            nextcord.SelectOption(
                label="Guys Negative",
                description="In any context you are not okay being referred to as a guy",
                value="guys_negative",
            ),
        ]

        terms_dropdown = Select(
            options=terms_options, placeholder="Gendered Terms Roles"
        )

        button_view = View(auto_defer=False)
        button_view.add_item(terms_dropdown)

        await ctx.send(embed=gendered_terms_embed, view=button_view)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:  # do not apply newbie role do bots
            return

        newbie_role = member.guild.get_role(self.config.roles.newbie)
        await member.add_roles(newbie_role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # ignores message if message is by bot
            return

        if message.guild is None:  # ignores if message is a DM
            return

        newbie_role = message.guild.get_role(self.config.roles.newbie)

        if newbie_role in message.author.roles:
            now = datetime.datetime.now()
            aware_now = now.replace(tzinfo=pytz.UTC)
            time_passed = aware_now - message.author.joined_at

            if time_passed.days > 3:
                await message.author.remove_roles(newbie_role)


def setup(bot, **kwargs):
    bot.add_cog(Roles(bot, kwargs["config"]))
