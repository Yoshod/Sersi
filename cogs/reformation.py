import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord.ext.commands.errors import MemberNotFound
from baseutils import *


class Reformation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.notModFail = f"{sersifail} Only moderators can use this command."

    # command
    @commands.command(aliases=['rn', 'reformneeded', 'reform'])
    async def reformationneeded(self, ctx, member: nextcord.Member, *reason):
        """send a user to reformation centre

        Sends a [member] to reformation centre for reform by giving said [member] the @Reformation role. Removes @Civil Engineering Initiate and all Opt-In-Roles.
        Permission Needed: Moderator, Trial Moderator
        """
        if not is_mod(ctx.author):
            await ctx.reply(self.notModFail)
            return

        reason_string = " ".join(reason)

        if reason_string.startswith("?r "):     # splices away the "?r" that moderators accustomed to wick might put in there
            reason_string = reason_string[3:]

        reformation_role = ctx.guild.get_role(get_config_int('ROLES', 'reformation'))

        await member.add_roles(reformation_role, reason=reason_string, atomic=True)

        role_obj = ctx.guild.get_role(get_config_int('ROLES', 'civil enginerring initiate'))
        await member.remove_roles(role_obj, reason=reason_string, atomic=True)

        for role in get_options('OPT IN ROLES'):
            role_obj = ctx.guild.get_role(get_config_int('PERMISSION ROLES', role))
            await member.remove_roles(role_obj, reason=reason_string, atomic=True)

        await ctx.send(f"Member {member.mention} has been sent to reformation by {ctx.author.mention} for reason: `{reason_string}`")

        # Giving a welcome to the person sent to reformation
        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'reformation'))
        welcome_embed = nextcord.Embed(
            title="Welcome to Reformation",
            description=f"Hello {member.mention}, you have been sent to reformation by {ctx.author.mention}. The reason given for this is `{reason_string}`. \n\nFor more information on reformation check out <#{get_config_int('CHANNELS', 'reformation info')}> or talk to a <@&{get_config_int('PERMISSION ROLES', 'reformist')}>.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        await channel.send(embed=welcome_embed)

        # # LOGGING
        embed = nextcord.Embed(
            title="User Has Been Sent to Reformation",
            description=f"Moderator {ctx.author.mention} ({ctx.author.id}) has sent user {member.mention} ({member.id}) to reformation.\n\n"
                        + f"**__Reason:__** {reason_string}",
            color=nextcord.Color.from_rgb(237, 91, 6))

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=embed)

    async def cb_rq_yes(self, interaction):
        if not is_mod(interaction.user):
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
                civil_enginerring_initiate  = interaction.guild.get_role(get_config_int('ROLES', 'civil enginerring initiate'))
                reformed                    = interaction.guild.get_role(get_config_int('ROLES', 'reformed'))

                await member.add_roles(civil_enginerring_initiate, reformed, reason="Released out of the Reformation Centre", atomic=True)
            except AttributeError:
                await interaction.send("Could not assign roles.")
            await member.remove_roles(interaction.guild.get_role(get_config_int('ROLES', 'reformation')), reason="Released out of the Reformation Centre", atomic=True)

            # logs
            log_embed = nextcord.Embed(
                title=f"Release: **{member.name}** ({member.id})",
                description=f"Reformation Inmate {member.name} was deemed well enough to be released back into the server.\nRelease has been approved by {', '.join(yes_men)}",
                color=nextcord.Color.from_rgb(237, 91, 6))
            channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
            await channel.send(embed=log_embed)
            await interaction.send(f"**{member.name}** ({member.id}) will now be freed.")

            # updates embed and removed buttons
            await interaction.message.edit(embed=new_embed, view=None)

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)

    async def cb_rf_yes(self, interaction):
        if not is_mod(interaction.user):
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

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
            await channel.send(embed=embed)

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
            await channel.send(embed=embed)

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
            await channel.send(embed=embed)
            await interaction.message.edit(embed=new_embed, view=None)

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)

    async def cb_no(self, interaction):
        if not is_mod(interaction.user):
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
        if not is_mod(interaction.user):
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

    @commands.command(aliases=['rq', 'reformquery', 'reformq'])
    async def reformationquery(self, ctx, member: nextcord.Member):
        """query releasing a user from reformation centre

        Sends query for release out of reformation centre for [member] into the information centre.
        Three 'Yes' votes will result in an automatic release.
        Permission Needed: Moderator, Trial Moderator
        """
        if not is_mod(ctx.author):
            await ctx.reply(self.notModFail)
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == get_config_int('ROLES', 'reformation'):
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

        channel = self.bot.get_channel(get_config_int('ROLES', 'alert'))
        await channel.send(embed=embedVar, view=button_view)

    async def cb_done(self, interaction):
        if not is_mod(interaction.user):
            await interaction.response.send_message("Sorry, you don't get to vote", ephemeral=True)
            return

        embed = interaction.message.embeds[0]
        embed.add_field(name="User was or is banned:", value=interaction.user.mention, inline=True)
        embed.color = nextcord.Color.from_rgb(0, 255, 0)
        await interaction.message.edit(embed=embed, view=None)

    @commands.command(aliases=['rf', 'reformfailed', 'reformfail', 'reformf'])
    async def reformationfailed(self, ctx, member: nextcord.Member):
        """query banning a user in reformation centre

        Sends query for ban of a [member] who is currently in the reformation centre.
        Members should have been in reformation of at least 14 Days.
        Three 'Yes' votes will result in a greenlight for a ban.
        Permission Needed: Moderator, Trial Moderator
        """
        if not is_mod(ctx.author):
            await ctx.reply(self.notModFail)
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == get_config_int('ROLES', 'reformation'):
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

        channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
        await channel.send(embed=embedVar, view=button_view)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        reformation_role = member.get_role(get_config_int('ROLES', 'reformation'))

        if reformation_role is not None:
            channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
            embed = nextcord.Embed(
                title=f"User **{member}** ({member.id}) has left the server while in the reformation centre!",
                description=f"User has left the server while having the <@&{get_config_int('ROLES', 'reformation')}> role. If they have not been banned, they should be hack-banned using wick now.",
                color=nextcord.Color.from_rgb(255, 255, 0))
            done = Button(label="User was or is banned", style=nextcord.ButtonStyle.green)
            done.callback = self.cb_done
            button_view = View(timeout=None)
            button_view.add_item(done)
            await channel.send(embed=embed, view=button_view)


def setup(bot):
    bot.add_cog(Reformation(bot))
