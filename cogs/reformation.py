import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord.ext.commands.errors import MemberNotFound
from baseutils import *


class Reformation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notModFail = "<:sersifail:979070135799279698> Only moderators can use this command."

    # command
    @commands.command()
    async def rn(self, ctx, member: nextcord.Member, *args):
        """Reform Needed.

        Sends a user to reformation centre for reform by giving said user the @Reformation role. Removes @Civil Engineering Initiate and all Opt-In-Roles.
        Permission Needed: Moderator, Trial Moderator
        """
        if not isMod(ctx.author.roles):
            await ctx.reply(self.notModFail)
            return

        try:
            reason_string = " ".join(args)
            reformation_role = ctx.guild.get_role(getReformationRole(ctx.guild.id))

            await member.add_roles(reformation_role, reason=reason_string, atomic=True)
            try:
                role_ids = [878040658244403253, 960558372837523476, 960558399471378483,
                            960558452109885450, 960558507403382784, 960558557332406293,
                            960558615209582672, 960558657672732712, 960558722839642212,
                            960558757463605298, 960558800442646578, 960558452109885450,
                            902291483040837684]
                for role in role_ids:
                    await member.remove_roles(ctx.guild.get_role(role), reason=reason_string, atomic=True)
            except AttributeError:
                await ctx.reply("Could not remove roles.")

            await ctx.send(f"Memeber {member.mention} has been sent to reformation by {ctx.author.mention} for reson: {reason_string}")

            # Giving a welcome to the person sent to reformation
            try:
                channel = self.bot.get_channel(943180985632169984)
                welcome_embed = nextcord.Embed(
                    tile="Welcome to Reformation",
                    description=f"Hello {member.mention}, you have been sent to reformation by {ctx.author.mention}. The reason given for this is `{reason_string}`. \n\nFor more information on reformation check out <#878292548785958982> or talk to a <@&943193811574751314>.",
                    color=nextcord.Color.from_rgb(237, 91, 6))
                await channel.send(embed=welcome_embed)

            except AttributeError:
                pass

            # # LOGGING
            embed = nextcord.Embed(
                title="User Has Been Sent to Reformation",
                description=f"Moderator {ctx.author.mention} ({ctx.author.id}) has sent user {member.mention} ({member.id}) to reformation.\n\n"
                            + f"**__Reason:__** {reason_string}",
                color=nextcord.Color.from_rgb(237, 91, 6))

            channel = self.bot.get_channel(getLoggingChannel(ctx.guild.id))
            await channel.send(embed=embed)

            channel = self.bot.get_channel(getModlogsChannel(ctx.guild.id))
            await channel.send(embed=embed)

        except MemberNotFound:
            await ctx.send("Member not found!")

    async def cb_rq_yes(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("Sorry, you don't get to vote", ephemeral=True)
            return

        new_embed = interaction.message.embeds[0]
        # check if user has already voted
        for field in new_embed.fields:
            if field.value == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        # make vote visible
        new_embed.add_field(name="Voted Yes:", value=interaction.user.mention, inline=True)
        # retrieve current amount of votes and iterate by 1
        yes_votes = new_embed.description[-1]
        yes_votes = int(yes_votes) + 1

        # automatically releases inmate at 3 yes votes
        if (yes_votes >= 3):

            # get member object of member to be released
            member_string   = new_embed.footer.text
            member_id       = int(member_string)
            member          = interaction.guild.get_member(member_id)

            # fetch yes voters
            yes_men = []
            for field in new_embed.fields:
                if field.name == "Voted Yes:":
                    yes_men.append(field.value)

            # roles
            try:
                civil_enginerring_initiate  = interaction.guild.get_role(878040658244403253)
                reformed                    = interaction.guild.get_role(878289678623703080)

                await member.add_roles(civil_enginerring_initiate, reformed, reason="Released out of the Reformation Centre", atomic=True)
            except AttributeError:
                await interaction.send("Could not assign roles.")
            await member.remove_roles(interaction.guild.get_role(getReformationRole(interaction.guild.id)), reason="Released out of the Reformation Centre", atomic=True)

            # logs
            log_embed = nextcord.Embed(
                title=f"Release: **{member.name}** ({member.id})",
                description=f"Reformation Inmate {member.name} was deemed well enough to be released back into the server.\nRelease has been approved by {', '.join(yes_men)}",
                color=nextcord.Color.from_rgb(237, 91, 6))
            channel = self.bot.get_channel(getModlogsChannel(interaction.guild.id))
            await channel.send(embed=log_embed)
            await interaction.send(f"**{member.name}** ({member.id}) will now be freed.")

            # updates embed and removed buttons
            await interaction.message.edit(embed=new_embed, view=None)

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)

    async def cb_rf_yes(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("Sorry, you don't get to vote", ephemeral=True)
            return

        new_embed = interaction.message.embeds[0]
        # check if user has already voted
        for field in new_embed.fields:
            if field.value == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        # make vote visible
        new_embed.add_field(name="Voted Yes:", value=interaction.user.mention, inline=True)
        # retrieve current amount of votes and iterate by 1
        yes_votes = new_embed.description[-1]
        yes_votes = int(yes_votes) + 1

        # automatically releases inmate at 3 yes votes
        if (yes_votes >= 3):

            member_string   = new_embed.footer.text
            member_id       = int(member_string)
            member          = interaction.guild.get_member(member_id)

            yes_men = []
            for field in new_embed.fields:
                if field.name == "Voted Yes:":
                    yes_men.append(field.value)

            embed = nextcord.Embed(
                title="Reformation Failed",
                description=f"Reformation Inmate {member.name} has been deemed unreformable by {', '.join(yes_men)}\n\nThey can be banned **given appropiate reason** by a moderators discretion.",
                color=nextcord.Color.from_rgb(0, 0, 0))

            channel = self.bot.get_channel(getAlertChannel(interaction.guild.id))
            await channel.send(embed=embed)

            channel = self.bot.get_channel(getLoggingChannel(interaction.guild.id))
            await channel.send(embed=embed)

            channel = self.bot.get_channel(getModlogsChannel(interaction.guild.id))
            await channel.send(embed=embed)

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)

    async def cb_no(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("Sorry, you don't get to vote", ephemeral=True)
            return

        new_embed = interaction.message.embeds[0]
        # check if user has already voted
        for field in new_embed.fields:
            if field.value == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        # make vote visible
        new_embed.add_field(name="Voted No:", value=interaction.user.mention, inline=True)
        await interaction.message.edit(embed=new_embed)

    async def cb_maybe(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("Sorry, you don't get to vote", ephemeral=True)
            return

        new_embed = interaction.message.embeds[0]
        # check if user has already voted
        for field in new_embed.fields:
            if field.value == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        # make vote visible
        new_embed.add_field(name="Voted Maybe:", value=interaction.user.mention, inline=True)
        await interaction.message.edit(embed=new_embed)

    @commands.command()
    async def rq(self, ctx, member: nextcord.Member):
        """Reformation Query.

        Sends query for release out of reformation centre for [member] into the information centre.
        Three 'Yes' votes will result in an automatic release.
        Permission Needed: Moderator, Trial Moderator
        """
        if not isMod(ctx.author.roles):
            await ctx.reply(self.notModFail)
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == getReformationRole(ctx.guild.id):
                is_in_reformation = True
        if not is_in_reformation:
            await ctx.send("Member is not in reformation.")
            return

        try:
            embedVar = nextcord.Embed(
                title=f"Reformation Query: **{member.name}** ({member.id})",
                description=f"Reformation Inmate {member.name} was deemed well enough to start a query about their release\nQuery started by {ctx.author.mention} ({ctx.author.id})\n\nYes Votes: 0",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.set_footer(text=f"{member.id}")
        except MemberNotFound:
            await ctx.send("Member not found!")

        yes = Button(label="Yes", style=nextcord.ButtonStyle.green)
        yes.callback = self.cb_rq_yes

        no = Button(label="No", style=nextcord.ButtonStyle.red)
        no.callback = self.cb_no

        maybe = Button(label="Maybe")
        maybe.callback = self.cb_maybe

        button_view = View(timeout=None)
        button_view.add_item(yes)
        button_view.add_item(no)
        button_view.add_item(maybe)

        channel = self.bot.get_channel(getAlertChannel(ctx.guild.id))
        await channel.send(embed=embedVar, view=button_view)

    async def cb_done(self, interaction):
        if not isMod(interaction.user.roles):
            await interaction.response.send_message("Sorry, you don't get to vote", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.add_field(name="User was or is banned:", value=interaction.user.mention, inline=True)
        embed.color = nextcord.Color.from_rgb(0, 255, 0)
        await interaction.message.edit(embed=embed, view=None)

    @commands.command()
    async def rf(self, ctx, member: nextcord.Member):
        """Reformation Failed.

        Sends query for ban of a [member] who is currently in the reformation centre.
        Members should have been in reformation of at least 14 Days.
        Three 'Yes' votes will result in a greenlight for a ban.
        Permission Needed: Moderator, Trial Moderator
        """
        if not isMod(ctx.author.roles):
            await ctx.reply(self.notModFail)
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == getReformationRole(ctx.guild.id):
                is_in_reformation = True
        if not is_in_reformation:
            await ctx.send("Member is not in reformation.")
            return

        try:
            embedVar = nextcord.Embed(
                title=f"Reformation Failed Query: **{member.name}** ({member.id})",
                description=f"Reformation Inmate {member.name} seems to not be able to be reformed. Should the reformation process therefore be given up and the user be banned?\nQuery started by {ctx.author.mention} ({ctx.author.id})\n\nYes Votes: 0",
                color=nextcord.Color.from_rgb(237, 91, 6))
            embedVar.set_footer(text=f"{member.id}")
        except MemberNotFound:
            await ctx.send("Member not found!")

        yes = Button(label="Yes", style=nextcord.ButtonStyle.green)
        yes.callback = self.cb_rf_yes

        no = Button(label="No", style=nextcord.ButtonStyle.red)
        no.callback = self.cb_no

        maybe = Button(label="Maybe")
        maybe.callback = self.cb_maybe

        button_view = View(timeout=None)
        button_view.add_item(yes)
        button_view.add_item(no)
        button_view.add_item(maybe)

        channel = self.bot.get_channel(getAlertChannel(ctx.guild.id))
        await channel.send(embed=embedVar, view=button_view)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        reformation_role = member.get_role(getReformationRole(member.guild.id))

        if reformation_role is not None:
            channel = self.bot.get_channel(getAlertChannel(member.guild.id))
            embed = nextcord.Embed(
                title=f"User **{member}** ({member.id}) has left the server while in the reformation centre!",
                description=f"User has left the server while having the @reformation role. If they have not been banned, they should be hack-banned using wick now.",
                color=nextcord.Color.from_rgb(255, 255, 0))
            done = Button(label="User was or is banned", style=nextcord.ButtonStyle.green)
            done.callback = self.cb_done
            button_view = View(timeout=None)
            button_view.add_item(done)
            await channel.send(embed=embed, view=button_view)


def setup(bot):
    bot.add_cog(Reformation(bot))
