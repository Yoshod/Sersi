import nextcord
import pickle
import io
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord.ext.commands.errors import MemberNotFound
from os import remove
from chat_exporter import export

from baseutils import ConfirmView, ban
from configutils import get_config_int, get_options, get_config
from permutils import is_senior_mod, permcheck, is_mod, cb_is_mod, is_custom_role
from caseutils import case_history, reform_case


class Reformation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sersifail = get_config('EMOTES', 'fail')
        self.case_history_file = "Files/Cases/casehistory.pkl"
        self.case_details_file = "Files/Cases/casedetails.pkl"

    async def cb_rn_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            elif field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        # give reformation role
        reformation_role = interaction.guild.get_role(get_config_int('ROLES', 'reformation'))
        await member.add_roles(reformation_role, reason=reason, atomic=True)

        # remove civil engineering initiate
        role_obj = interaction.guild.get_role(get_config_int('ROLES', 'civil engineering initiate'))
        await member.remove_roles(role_obj, reason=reason, atomic=True)

        # remove opt-ins
        roles = member.roles
        for role in get_options('OPT IN ROLES'):
            role_obj = interaction.guild.get_role(get_config_int('PERMISSION ROLES', role))
            if role_obj in roles:
                await member.remove_roles(role_obj, reason=reason, atomic=True)

        await interaction.message.edit(f"Member {member.mention} has been sent to reformation by {interaction.user.mention} for reason: `{reason}`", embed=None, view=None)

        # Giving a welcome to the person sent to reformation
        welcome_embed = nextcord.Embed(
            title="Welcome to Reformation",
            description=f"Hello {member.mention}, you have been sent to reformation by {interaction.user.mention}. The reason given for this is `{reason}`. \n\nFor more information on reformation check out <#{get_config_int('CHANNELS', 'reformation info')}> or talk to a <@&{get_config_int('PERMISSION ROLES', 'reformist')}>.",
            color=nextcord.Color.from_rgb(237, 91, 6))

        # # LOGGING
        embed = nextcord.Embed(
            title="User Has Been Sent to Reformation",
            description=f"Moderator {interaction.user.mention} ({interaction.user.id}) has sent user {member.mention} ({member.id}) to reformation.\n\n"
                        + f"**__Reason:__**\n{reason}",
            color=nextcord.Color.from_rgb(237, 91, 6))

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
        await channel.send(embed=embed)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'reformpubliclog'))
        await channel.send(embed=embed)

        overwrites = {
            interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True),
            interaction.guild.get_role(get_config_int('PERMISSION ROLES', 'reformist')): nextcord.PermissionOverwrite(read_messages=True),
            interaction.guild.get_role(get_config_int('PERMISSION ROLES', 'moderator')): nextcord.PermissionOverwrite(read_messages=True),
            member: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=False, embed_links=False, attach_files=False, use_external_emojis=False)
        }
        try:
            with open("Files/Reformation/reformationcases.pkl", "rb") as file:
                reformation_list = pickle.load(file)

        except (EOFError, TypeError):
            reformation_list = {}

        with open("Files/Reformation/reformationiter.txt", "r") as file:
            case_num = file.readline()
            case_num = int(case_num) + 1

        remove("Files/Reformation/reformationiter.txt")

        with open("Files/Reformation/reformationiter.txt", "w") as file:
            file.write(str(case_num))

        case_name = (f"reformation-case-{str(case_num).zfill(4)}")

        case_details = [case_name, case_num, interaction.user.id, reason]
        reformation_list[member.id] = case_details

        category = nextcord.utils.get(interaction.guild.categories, name="REFORMATION ROOMS")
        channel = await interaction.guild.create_text_channel(case_name, overwrites=overwrites, category=category)

        with open("Files/Reformation/reformationcases.pkl", "wb") as file:
            pickle.dump(reformation_list, file)

        unique_id = case_history(member.id, "Reformation")
        reform_case(unique_id, case_num, member.id, interaction.user.id, channel.id, reason)

        channel = nextcord.utils.get(interaction.guild.channels, name=case_name)
        await channel.send(embed=welcome_embed)

    # command
    @commands.command(aliases=['rn', 'reformneeded', 'reform'])
    async def reformationneeded(self, ctx, member: nextcord.Member, *, reason=""):
        """Send a user to reformation centre.

        Sends a [member] to reformation centre for reform by giving said [member] the @Reformation role. Removes @Civil Engineering Initiate and all Opt-In-Roles.
        Permission Needed: Moderator, Trial Moderator.
        """

        if not await permcheck(ctx, is_mod):
            return

        if reason.startswith("?r "):     # splices away the "?r" that moderators accustomed to wick might put in there
            reason = reason[3:]

        elif reason == "":
            await ctx.send(f"{ctx.author.mention} please provide a reason.")
            return

        dialog_embed = nextcord.Embed(
            title="Reform Member",
            description="Following member will be sent to reformation:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason)

        await ConfirmView(self.cb_rn_proceed).send_as_reply(ctx, embed=dialog_embed)

    async def cb_rq_yes(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Voted Yes:", value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*", inline=True)

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
                civil_engineering_initiate  = interaction.guild.get_role(get_config_int('ROLES', 'civil engineering initiate'))
                reformed                    = interaction.guild.get_role(get_config_int('ROLES', 'reformed'))

                await member.add_roles(civil_engineering_initiate, reformed, reason="Released out of the Reformation Centre", atomic=True)
            except AttributeError:
                await interaction.send("Could not assign roles.")
            await member.remove_roles(interaction.guild.get_role(get_config_int('ROLES', 'reformation')), reason="Released out of the Reformation Centre", atomic=True)

            # logs
            log_embed = nextcord.Embed(
                title=f"Successful Reformation: **{member.name}** ({member.id})",
                description=f"Reformation Member {member.name} was deemed well enough to be considered reformed.\nThis has been approved by {', '.join(yes_men)}.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
            await channel.send(embed=log_embed)
            await interaction.send(f"**{member.name}** ({member.id}) will now be considered reformed.")

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'reformpubliclog'))
            await channel.send(embed=log_embed)

            # updates embed and removed buttons
            await interaction.message.edit(embed=new_embed, view=None)

            # close case
            with open("Files/Reformation/reformationcases.pkl", "rb") as file:
                reformation_list = pickle.load(file)

            channel_name = reformation_list[member.id][0]
            channel = nextcord.utils.get(interaction.guild.channels, name=channel_name)

            transcript = await export(channel, military_time=True)

            if transcript is None:
                await channel.delete()
                channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")

            else:
                transcript_file = nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{channel_name}.html",
                )

            await channel.delete()
            channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
            await channel.send(embed=log_embed, file=transcript_file)

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)

    async def cb_rq_yes_open_modal(self, interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        await interaction.response.send_modal(ReasonModal("Reason for voting Yes", self.cb_rq_yes))

    async def cb_rf_yes(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Voted Yes:", value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*", inline=True)
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

            # get person cases
            case_history = {}
            with open(self.case_history_file, "rb") as file:
                case_history = pickle.load(file)

            user_history = case_history[member_id][::-1]    # filter for member_id, most recent first

            for case in user_history:
                if case[1] == "Reformation":
                    case_id = case[0]

            # lookup most recent ref case
            case_details = {}
            with open(self.case_details_file, "rb") as file:
                case_details = pickle.load(file)

            # get reason
            reason = case_details[case_id][5]

            # await member.ban(reason=f"Reformation Failed: {reason}", delete_message_days=0)
            await ban(member, "rf", reason=f"Reformation Failed: {reason}")

            # transript
            with open("Files/Reformation/reformationcases.pkl", "rb") as file:
                reformation_list = pickle.load(file)
            room_channel_name = reformation_list[member.id][0]
            room_channel = nextcord.utils.get(interaction.guild.channels, name=room_channel_name)

            transcript = await export(room_channel, military_time=True)

            if transcript is None:
                channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")
            else:
                transcript_file = nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{room_channel_name}.html",
                )

            await room_channel.delete()

            embed = nextcord.Embed(
                title="Reformation Failed",
                description=f"Reformation Inmate {member.name} has been deemed unreformable by {', '.join(yes_men)}\n\nInitial reason for Reformation was: `{reason}`. They have been banned automatically.",
                color=nextcord.Color.from_rgb(0, 0, 0))

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
            await channel.send(embed=embed)

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
            await channel.send(embed=embed)

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
            await channel.send(embed=embed, file=transcript_file)

            await interaction.message.edit(embed=new_embed, view=None)

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)

    async def cb_rf_yes_open_modal(self, interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        await interaction.response.send_modal(ReasonModal("Reason for voting Yes", self.cb_rf_yes))

    async def cb_no(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Voted No:", value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*", inline=True)
        await interaction.message.edit(embed=new_embed)

    async def cb_no_open_modal(self, interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        await interaction.response.send_modal(ReasonModal("Reason for voting No", self.cb_no))

    async def cb_maybe(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Voted Maybe:", value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*", inline=True)
        await interaction.message.edit(embed=new_embed)

    async def cb_maybe_open_modal(self, interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message("You already voted", ephemeral=True)
                return

        await interaction.response.send_modal(ReasonModal("Reason for voting Maybe", self.cb_maybe))

    @commands.command(aliases=['rq', 'reformquery', 'reformq'])
    async def reformationquery(self, ctx, member: nextcord.Member, *, reason=""):
        """Query releasing a user from reformation centre.

        Sends query for release out of reformation centre for [member] into the information centre.
        Three 'Yes' votes will result in an automatic release.
        Permission Needed: Moderator, Trial Moderator.
        """
        if not await permcheck(ctx, is_mod):
            return

        elif reason == "":
            await ctx.send(f"{ctx.author.mention} please provide a reason.")
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

        embedVar.add_field(name="Reason", value=reason, inline=False)

        yes = Button(label="Yes", style=nextcord.ButtonStyle.green)
        yes.callback = self.cb_rq_yes_open_modal

        no = Button(label="No", style=nextcord.ButtonStyle.red)
        no.callback = self.cb_no_open_modal

        maybe = Button(label="Maybe")
        maybe.callback = self.cb_maybe_open_modal

        button_view = View(timeout=None)
        button_view.add_item(yes)
        button_view.add_item(no)
        button_view.add_item(maybe)
        button_view.interaction_check = cb_is_mod

        channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
        await channel.send(embed=embedVar, view=button_view)

    @commands.command(aliases=['rf', 'reformfailed', 'reformfail', 'reformf'])
    async def reformationfailed(self, ctx, member: nextcord.Member):
        """Query banning a user in reformation centre.

        Sends query for ban of a [member] who is currently in the reformation centre.
        Members should have been in reformation of at least 14 Days.
        Three 'Yes' votes will result in a greenlight for a ban.
        Permission Needed: Moderator, Trial Moderator.
        """
        if not await permcheck(ctx, is_mod):
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
        yes.callback = self.cb_rf_yes_open_modal

        no = Button(label="No", style=nextcord.ButtonStyle.red)
        no.callback = self.cb_no_open_modal

        maybe = Button(label="Maybe")
        maybe.callback = self.cb_maybe_open_modal

        button_view = View(timeout=None)
        button_view.add_item(yes)
        button_view.add_item(no)
        button_view.add_item(maybe)
        button_view.interaction_check = cb_is_mod

        channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
        await channel.send(embed=embedVar, view=button_view)

    @commands.command(aliases=["rcase", "reformcase"])
    async def reformationcase(self, ctx, user: nextcord.Member):
        if not await permcheck(ctx, is_custom_role(ctx.author, [get_config_int('PERMISSION ROLES', 'moderator'), get_config_int('PERMISSION ROLES', 'trial moderator'), get_config_int('PERMISSION ROLES', 'reformist')])):
            return

        elif user is None:
            await ctx.send(f"{self.sersifail} Please provide a user.")

        elif user is not None:
            with open("Files/Reformation/reformationcases.pkl", "rb") as file:
                reformation_list = pickle.load(file)
            keys = reformation_list.keys()
            if user.id in keys:
                case_embed = nextcord.Embed(
                    title=(f"Reformation Case: {reformation_list[user.id][1]}"),
                    color=nextcord.Color.from_rgb(237, 91, 6)
                )
                moderator = ctx.guild.get_member(reformation_list[user.id][2])
                channel_name = reformation_list[user.id][0]
                reform_channel = nextcord.utils.get(ctx.guild.channels, name=channel_name)
                case_embed.add_field(name="Username:", value=(f"{user.mention} ({user.id})"), inline=False)
                case_embed.add_field(name="Responsible Moderator:", value=(f"{moderator.mention} ({moderator.id}"), inline=False)
                case_embed.add_field(name="Channel:", value=(reform_channel.mention), inline=False)
                case_embed.add_field(name="Reason:", value=reformation_list[user.id][3])
                await ctx.send(embed=case_embed)
                return
        else:
            ctx.send(f"{self.sersifail} Failed to find the specified user! Perhaps they do not have a case?")

    @commands.command()
    async def refremove(self, ctx, member: nextcord.Member, *, reason):
        if not await permcheck(ctx, is_senior_mod):
            return

        civil_engineering_initiate  = ctx.guild.get_role(get_config_int('ROLES', 'civil engineering initiate'))
        await member.add_roles(civil_engineering_initiate, reason=reason)
        await member.remove_roles(ctx.guild.get_role(get_config_int('ROLES', 'reformation')), reason=reason)

        # logs
        log_embed = nextcord.Embed(
            title=f"Reformation Release: **{member.name}** ({member.id})",
            description=f"Reformation Member {member.name} was forcefully released by {ctx.author.mention} ({ctx.author.id}).",
            color=nextcord.Color.from_rgb(237, 91, 6))
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        reformation_role = member.get_role(get_config_int('ROLES', 'reformation'))

        if reformation_role is not None:

            async for ban_entry in member.guild.bans():
                if member.id == ban_entry.user.id:
                    channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
                    embed = nextcord.Embed(
                        title=f"Reformation inmate **{member}** ({member.id}) banned!",
                        colour=nextcord.Color.from_rgb(237, 91, 6))
                    embed.add_field(name="Reason:", value=ban.reason)

                    # transript
                    with open("Files/Reformation/reformationcases.pkl", "rb") as file:
                        reformation_list = pickle.load(file)
                    room_channel_name = reformation_list[member.id][0]
                    room_channel = nextcord.utils.get(member.guild.channels, name=room_channel_name)

                    transcript = await export(room_channel, military_time=True)

                    if transcript is None:
                        channel = member.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
                        await channel.send(f"{self.sersifail} Failed to Generate Transcript!")
                    else:
                        transcript_file = nextcord.File(
                            io.BytesIO(transcript.encode()),
                            filename=f"transcript-{room_channel_name}.html",
                        )

                    await room_channel.delete()
                    channel = member.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
                    await channel.send(embed=embed, file=transcript_file)

                    return

            # await member.ban(reason="Left while in reformation centre.", delete_message_days=0)
            await ban(member, "leave", reason="Left while in reformation centre.")

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
            embed = nextcord.Embed(
                title=f"User **{member}** ({member.id}) has left the server while in the reformation centre!",
                description=f"User has left the server while having the <@&{get_config_int('ROLES', 'reformation')}> role. They have been banned automatically.",
                colour=nextcord.Color.from_rgb(237, 91, 6))

            # transript
            with open("Files/Reformation/reformationcases.pkl", "rb") as file:
                reformation_list = pickle.load(file)
            room_channel_name = reformation_list[member.id][0]
            room_channel = nextcord.utils.get(member.guild.channels, name=room_channel_name)

            transcript = await export(room_channel, military_time=True)

            if transcript is None:
                channel = member.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")
            else:
                transcript_file = nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{room_channel_name}.html",
                )

            await room_channel.delete()
            channel = member.guild.get_channel(get_config_int('CHANNELS', 'teachers'))
            await channel.send(embed=embed, file=transcript_file)


class ReasonModal(nextcord.ui.Modal):
    def __init__(self, name, cb):
        super().__init__(name)
        self.field = nextcord.ui.TextInput(label="Reason", min_length=4, max_length=256, required=True, placeholder="please provide a reason")
        self.add_item(self.field)
        self.callback = cb


def setup(bot):
    bot.add_cog(Reformation(bot))
