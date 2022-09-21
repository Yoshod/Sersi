import nextcord
import ticketutils

from nextcord.ext import commands
from nextcord.ui import Button, View
from permutils import permcheck, is_dark_mod, is_senior_mod, is_mod
from configutils import Configuration


class ModeratorTicket(nextcord.ui.Modal):
    def __init__(self, config: Configuration):
        super().__init__("Moderator Ticket")
        self.config = config

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

        if not ticketutils.ticket_check(self.config, user.id, "mod_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(self.config, interaction, user, "mod_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="MODERATION SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Mod Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted a Moderator Ticket.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name="Initial Remarks:",    value=self.issue.value,      inline=False)
        ticket_embed.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        close_bttn = Button(custom_id=f"moderator-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class SeniorModeratorTicket(nextcord.ui.Modal):
    def __init__(self, config: Configuration):
        super().__init__("Senior Moderator Ticket")
        self.config = config

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

        if not ticketutils.ticket_check(self.config, user.id, "senior_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(self.config, interaction, user, "senior_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="MODERATION SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Senior Moderator Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted a Senior Moderator Ticket.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name="Initial Remarks",    value=self.issue.value,      inline=False)
        ticket_embed.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        close_bttn = Button(custom_id=f"senior-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class AdministratorTicket(nextcord.ui.Modal):
    def __init__(self, config: Configuration):
        super().__init__("Administrator Ticket")
        self.config = config

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

        if not ticketutils.ticket_check(self.config, user.id, "admin_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(self.config, interaction, user, "admin_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="MODERATION SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Administrator Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted an Administrator Ticket.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name="Initial Remarks:",    value=self.issue.value,      inline=False)
        ticket_embed.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        close_bttn = Button(custom_id=f"admin-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class VerificationTicket(nextcord.ui.Modal):
    def __init__(self, config: Configuration):
        super().__init__("Verification Ticket")
        self.config = config

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

        if not ticketutils.ticket_check(self.config, user.id, "verification_ticket"):
            return

        overwrites, case_name = ticketutils.ticket_prep(self.config, interaction, user, "verification_ticket")

        category = nextcord.utils.get(interaction.guild.categories, name="VERIFICATON SUPPORT")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        ticket_embed = nextcord.Embed(
            title="Verification Ticket Received",
            description=f"{user.mention} ({user.id}) has submitted a Verification Ticket.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        ticket_embed.add_field(name="Initial Remarks:", value=self.issue.value, inline=False)
        ticket_embed.set_footer(text=user.display_name, icon_url=user.display_avatar.url)

        close_bttn = Button(custom_id=f"verification-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

        button_view = View(auto_defer=False)
        button_view.add_item(close_bttn)

        await channel.send(embed=ticket_embed, view=button_view)


class TicketingSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def modtickets(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        ticket_embed = nextcord.Embed(
            title="Contact Server Staff",
            description="Select one of the buttons below to contact server staff. Please select the staff group most appropriate for your query. The examples below are just that, examples. They are not strict rules or limitations on which ticket should be used for your specific circumstances.",
            colour=nextcord.Color.from_rgb(237, 91, 6)
        )

        ticket_embed.add_field(name="Administrator",
                               value=f"<@&{self.config.permission_roles.dark_moderator}> is best contacted for:\n- Complaints about Senior Moderators or Community Engagement Team\n- Business queries for Adam Something\n- You want something deleted from server logs")
        admin = Button(custom_id="admin-ticket", label="Administrator Ticket", style=nextcord.ButtonStyle.red)

        ticket_embed.add_field(name="Senior Moderator",
                               value=f"<@&{self.config.permission_roles.senior_moderator}> is best contacted for:\n- Complaints about Moderators\n- Questions regarding server rules\n- Appealing moderator action taken against you")
        senior = Button(custom_id="senior-moderator-ticket", label="Senior Moderator Ticket", style=nextcord.ButtonStyle.blurple)

        ticket_embed.add_field(name="Moderator",
                               value=f"<@&{self.config.permission_roles.moderator}> is best contacted for:\n- Reporting user misconduct\n- Enquiries into moderator actions\n- Anonymous Chat Reports")
        moderator = Button(custom_id="moderator-ticket", label="Moderator Ticket", style=nextcord.ButtonStyle.blurple)

        button_view = View(auto_defer=False)
        button_view.add_item(admin)
        button_view.add_item(senior)
        button_view.add_item(moderator)

        await ctx.send(embed=ticket_embed, view=button_view)

    @commands.command()
    async def verificationtickets(self, ctx):
        if not await permcheck(ctx, is_dark_mod):
            return

        await ctx.message.delete()

        support_embed = nextcord.Embed(
            title="Get Verification Support",
            description="If you're having problems verifying then follow the next couple steps. If you still cannot verify then create a ticket pressing the button below.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        support_embed.add_field(name="VPNs", value="If you are using a VPN, please ensure it is turned off. If you live in a country where you have to use a VPN in order to access the internet please proceed to create a support ticket.", inline=False)
        support_embed.add_field(name="Account Age", value="If the account you are attempting to use in order to verify is too new then you will be unable to verify with that account. Reddit accounts below a certain Karma threshold are also ineligible for verification purposes.", inline=False)
        support_embed.add_field(name="Incognito Mode", value="If you have ever been logged into another discord account via browser, sometimes that account is still held in cache. Please try opening the AltDentifier link in an incognito/private window and try to verify through that.")
        support = Button(custom_id="support-ask", label="Open Ticket", style=nextcord.ButtonStyle.blurple)

        button_view = View(auto_defer=False)
        button_view.add_item(support)

        await ctx.send(embed=support_embed, view=button_view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction):
        try:
            id_name, id_extra = interaction.data["custom_id"].split(":", 1)
        except ValueError:
            id_name = interaction.data["custom_id"]
            id_extra = None

        match id_name:
            case "admin-ticket":
                await interaction.response.send_modal(AdministratorTicket(self.config))
            case "senior-moderator-ticket":
                await interaction.response.send_modal(SeniorModeratorTicket(self.config))
            case "moderator-ticket":
                await interaction.response.send_modal(ModeratorTicket(self.config))
            case "verification-ticket":
                await interaction.response.send_modal(VerificationTicket(self.config))

            case "support-ask":
                support = Button(custom_id="verification-ticket", label="✔️", style=nextcord.ButtonStyle.green)
                no_support = Button(custom_id="no-support", label="❌", style=nextcord.ButtonStyle.red)

                button_view = View(auto_defer=False)
                button_view.add_item(support)
                button_view.add_item(no_support)

                await interaction.response.send_message("Have you read the support ticket guidelines?", view=button_view, ephemeral=True)

            case "admin-ticket-close":
                if await permcheck(interaction, is_dark_mod):
                    user = self.bot.get_user(int(id_extra))
                    await ticketutils.ticket_close(self.config, interaction, user, "admin_ticket")
                    await interaction.channel.delete(reason="Ticket closed")

            case "senior-ticket-close":
                if await permcheck(interaction, is_senior_mod):
                    user = self.bot.get_user(int(id_extra))
                    await ticketutils.ticket_close(self.config, interaction, user, "senior_ticket")
                    await interaction.channel.delete(reason="Ticket closed")

            case "moderator-ticket-close":
                if await permcheck(interaction, is_mod):
                    user = self.bot.get_user(int(id_extra))
                    await ticketutils.ticket_close(self.config, interaction, user, "mod_ticket")
                    await interaction.channel.delete(reason="Ticket closed")

            case "verification-ticket-close":
                user = self.bot.get_user(int(id_extra))
                await ticketutils.ticket_close(self.config, interaction, user, "verification_ticket")
                await interaction.channel.delete(reason="Ticket closed")


def setup(bot, **kwargs):
    bot.add_cog(TicketingSystem(bot, kwargs["config"]))
