import nextcord
import ticketutils

from nextcord.ext import commands
from nextcord.ui import Button, View
from permutils import permcheck, is_dark_mod
from os import remove
from chat_exporter import export


class ModeratorTicket(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Moderator Ticket")

        self.issue = nextcord.ui.TextInput(
            label="What is the reason for your ticket:",
            max_length=1024,
            required=True,
            placeholder="Please give a brief reason for your ticket.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.issue)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        user = interaction.user

        if not ticketutils.ticket_check(user.id, "mod_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(interaction, user, "mod_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="MODERATION SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Mod Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted a Moderator Ticket",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name=self.issue.label,    value=self.issue.value,      inline=False)
        ticket_embed.set_footer(user.display_name, user.display_avatar.url)

        close_bttn = Button(custom_id=f"moderator-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class SeniorModeratorTicket(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Senior Moderator Ticket")

        self.issue = nextcord.ui.TextInput(
            label="What is the reason for your ticket:",
            max_length=1024,
            required=True,
            placeholder="Please give a brief reason for your ticket.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.issue)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        user = interaction.user

        if not ticketutils.ticket_check(user.id, "senior_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(interaction, user, "senior_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="MODERATION SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Senior Mod Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted a Senior Moderator Ticket",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name=self.issue.label,    value=self.issue.value,      inline=False)
        ticket_embed.set_footer(user.display_name, user.display_avatar.url)

        close_bttn = Button(custom_id=f"senior-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class AdministratorTicket(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Administrator Ticket")

        self.issue = nextcord.ui.TextInput(
            label="What is the reason for your ticket:",
            max_length=1024,
            required=True,
            placeholder="Please give a brief reason for your ticket.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.issue)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        user = interaction.user

        if not ticketutils.ticket_check(user.id, "admin_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(interaction, user, "admin_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="MODERATION SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Administrator Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted an Administrator Ticket",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name=self.issue.label,    value=self.issue.value,      inline=False)
        ticket_embed.set_footer(user.display_name)

        close_bttn = Button(custom_id=f"admin-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class VerificationTicket(nextcord.ui.Modal):
    def __init__(self):
        super().__init__("Verification Ticket")

        self.issue = nextcord.ui.TextInput(
            label="What is the reason for your ticket:",
            max_length=1024,
            required=True,
            placeholder="Please give a brief reason for your ticket.",
            style=nextcord.TextInputStyle.paragraph)
        self.add_item(self.issue)

    async def callback(self, interaction):
        """Run whenever the 'submit' button is pressed."""
        user = interaction.user

        if not ticketutils.ticket_check(user.id, "verification_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(interaction, user, "verification_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="VERIFICATON SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Verification Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted a Verification Ticket",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name=self.issue.label,    value=self.issue.value,      inline=False)
        ticket_embed.set_footer(user.display_name, user.display_avatar.url)

        close_bttn = Button(custom_id=f"verification-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class TicketingSystem(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config

    @commands.command()
    async def modtickets(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        ticket_embed = nextcord.Embed(
            title="Contact Server Staff",
            description="Select one of the buttons below to contact server staff. Please select the staff group most appropriate for your query.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name="Administrator", value=f"<@!{self.config.permission_roles.dark_moderator}> is best contacted for:\n- Complaints about Senior Moderators or Community Engagement Team\n- Business queries for Adam Something\n- You want something deleted from server logs")
        ticket_embed.add_field(name="Senior Moderator", value=f"<@!{self.config.permission_roles.senior_moderator}> is best contacted for:\n- Complaints about Moderators\n- Questions regarding server rules\n- Appealing moderator action taken against you")
        ticket_embed.add_field(name="Moderator", value=f"<@!{self.config.permission_roles.moderator}> is best contacted for:\n- Reporting user misconduct\n- Enquiries into moderator actions")
        admin = Button(custom_id="admin-ticket", label="Administrator Ticket", style=nextcord.ButtonStyle.red)
        senior = Button(custom_id="senior-moderator-ticket", label="Senior Moderator Ticket", style=nextcord.ButtonStyle.blurple)
        moderator = Button(custom_id="moderator-ticket", label="Moderator Ticket", style=nextcord.ButtonStyle.blurple)

        button_view = View(auto_defer=False)
        button_view.add_item(admin)
        button_view.add_item(senior)
        button_view.add_item(moderator)

        await ctx.send(embed=ticket_embed, view=button_view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            id_name, id_extra = interaction.data["custom_id"].split(":", 1)
        except ValueError:
            id_name = interaction.data["custom_id"]
            id_extra = None

        match id_name:
            case "admin-ticket":
                await interaction.response.send_modal(AdministratorTicket())
            case "senior-moderator-ticket":
                await interaction.response.send_modal(SeniorModeratorTicket())
            case "moderator-ticket":
                await interaction.response.send_modal(ModeratorTicket())
            case "verification-ticket":
                await interaction.response.send_modal(VerificationTicket())
            case "admin-ticket-close":
                pass
            case "senior-ticket-close":
                pass
            case "moderator-ticket-close":
                pass
            case "verification-ticket-close":
                pass


def setup(bot, **kwargs):
    bot.add_cog(TicketingSystem(bot, kwargs["config"]))
