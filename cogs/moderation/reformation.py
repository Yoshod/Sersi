import nextcord
import pickle
import io
from nextcord.ext import commands
from nextcord.ui import Button, View
from chat_exporter import export

from utils.base import ConfirmView, SersiEmbed, ban
from utils.cases.create import create_reformation_case
from utils.config import Configuration
from utils.perms import permcheck, is_mod, cb_is_mod, is_senior_mod
from utils.roles import give_role, remove_role

class Reformation(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersifail = config.emotes.fail
        self.case_history_file = config.datafiles.casehistory
        self.case_details_file = config.datafiles.casedetails

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
    )
    async def reformation(self, interaction: nextcord.Interaction):
        pass

    @reformation.subcommand(
        name="add", description="Send a user to reformation centre."
    )
    async def reformation_needed(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to send to reformation", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for sending to reformation",
            required=True,
            min_length=8,
            max_length=1024,
        ),
    ):
        """Send a user to reformation centre.

        Sends a [member] to reformation centre for reform by giving said [member] the @Reformation role.
        Removes @Civil Engineering Initiate and all Opt-In-Roles.
        Permission Needed: Moderator, Trial Moderator.
        """

        if not await permcheck(interaction, is_mod):
            return

        reformation_role = interaction.guild.get_role(self.config.roles.reformation)

        if reformation_role in member.roles:
            await interaction.send(
                f"{self.sersifail} member is already in reformation", ephemeral=True
            )
            return

        await interaction.response.defer()

        @ConfirmView.query(
            title="Reformation Needed",
            prompt="Following member will be sent to reformation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            },
        )
        async def execute(*args, **kwargs):
            # ------------------------------- ROLES
            # give reformation role
            await member.add_roles(reformation_role, reason=reason, atomic=True)

            # remove civil engineering initiate
            await remove_role(
                member,
                self.config.roles.civil_engineering_initiate, 
                interaction.guild,
                reason,
            )

            # remove opt-ins
            for role in vars(self.config.opt_in_roles):
                await remove_role(
                    member, 
                    
                    vars(self.config.opt_in_roles)[role]
                ,
                    interaction.guild,
                    reason,
                )

            # ------------------------------- CREATING THE CASE CHANNEL
            # updating the case number in the iter file
            with open(self.config.datafiles.reform_iter, "r") as file:
                case_num = file.readline()
                case_num = int(case_num) + 1

            with open(self.config.datafiles.reform_iter, "w") as file:
                file.write(str(case_num))

            case_name = f"reformation-case-{str(case_num).zfill(4)}"
            overwrites = {
                interaction.guild.default_role: nextcord.PermissionOverwrite(
                    read_messages=False
                ),
                interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True),
                interaction.guild.get_role(
                    self.config.permission_roles.reformist
                ): nextcord.PermissionOverwrite(read_messages=True),
                interaction.guild.get_role(
                    self.config.permission_roles.moderator
                ): nextcord.PermissionOverwrite(read_messages=True),
                member: nextcord.PermissionOverwrite(
                    read_messages=True,
                    create_public_threads=False,
                    create_private_threads=False,
                    external_stickers=False,
                    embed_links=False,
                    attach_files=False,
                    use_external_emojis=False,
                ),
            }
            category = nextcord.utils.get(
                interaction.guild.categories, name="REFORMATION ROOMS"
            )

            case_channel = await interaction.guild.create_text_channel(
                case_name, overwrites=overwrites, category=category
            )

            # ------------------------------- CREATING THE CASEFILE ENTRY

            create_reformation_case(
                self.config,
                case_num,
                member,
                interaction.user,
                case_channel.name,
                reason,
            )

            # ------------------------------- LOGGING

            # Giving a welcome to the person sent to reformation
            welcome_embed = SersiEmbed(
                title="Welcome to Reformation",
                description=f"Hello {member.mention}, you have been sent to reformation by {interaction.user.mention}. "
                f"The reason given for this is `{reason}`. \n\nFor more information on reformation "
                f"check out <#{self.config.channels.reformation_info}> or talk to a <@&"
                f"{self.config.permission_roles.reformist}>.",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )

            await case_channel.send(embed=welcome_embed)

            embed = SersiEmbed(
                title="User Has Been Sent to Reformation",
                description=f"Moderator {interaction.user.mention} ({interaction.user.id}) has sent user {member.mention}"
                f" ({member.id}) to reformation.\n\n" + f"**__Reason:__**\n{reason}",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )

            channel = interaction.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(
                self.config.channels.reform_public_log
            )
            await channel.send(embed=embed)

        await execute(self.bot, self.config, interaction)

    async def cb_rq_yes(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Voted Yes:",
            value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*",
            inline=True,
        )

        # retrieve current amount of votes and iterate by 1
        yes_votes = new_embed.description[-1]
        yes_votes = int(yes_votes) + 1

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)
        await interaction.response.defer()

        # automatically releases inmate at 3 yes votes
        if yes_votes >= 3:
            await interaction.message.edit(view=None)

            # get member object of member to be released
            member_string = new_embed.footer.text
            member_id = int(member_string)
            member = interaction.guild.get_member(member_id)

            # fetch yes voters
            yes_men = []
            for field in new_embed.fields:
                if field.name == "Voted Yes:":
                    yes_men.append(field.value)

            # roles
            try:
                civil_engineering_initiate = interaction.guild.get_role(
                    self.config.roles.civil_engineering_initiate
                )
                reformed = interaction.guild.get_role(self.config.roles.reformed)

                await member.add_roles(
                    civil_engineering_initiate,
                    reformed,
                    reason="Released out of the Reformation Centre",
                    atomic=True,
                )
            except AttributeError:
                await interaction.send("Could not assign roles.")
            await member.remove_roles(
                interaction.guild.get_role(self.config.roles.reformation),
                reason="Released out of the Reformation Centre",
                atomic=True,
            )

            # logs
            yes_list = "\n• ".join(yes_men)

            log_embed = nextcord.Embed(
                title=f"Successful Reformation: **{member.name}** ({member.id})",
                description=f"Reformation Member {member.name} was deemed well enough to be considered "
                f"reformed.\nThis has been approved by:\n• {yes_list}.",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )
            channel = interaction.guild.get_channel(self.config.channels.alert)
            await channel.send(embed=log_embed)

            channel = interaction.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=log_embed)

            channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await channel.send(embed=log_embed)

            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            await channel.send(embed=log_embed)

            # await interaction.send(f"**{member.name}** ({member.id}) will now be considered reformed.")

            # updates embed and removed buttons
            await interaction.message.edit(embed=new_embed, view=None)

            # close case
            with open(self.config.datafiles.reformation_cases, "rb") as file:
                reformation_list = pickle.load(file)

            channel_name = reformation_list[member.id][0]
            channel = nextcord.utils.get(interaction.guild.channels, name=channel_name)

            transcript = await export(channel, military_time=True)

            if transcript is None:
                await channel.delete()
                channel = interaction.guild.get_channel(
                    self.config.channels.teachers_lounge
                )
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")

            else:
                transcript_file = nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{channel_name}.html",
                )

            await channel.delete()
            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            await channel.send(embed=log_embed, file=transcript_file)

    async def cb_rq_yes_open_modal(self, interaction: nextcord.Interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message(
                    "You already voted", ephemeral=True
                )
                return

        await interaction.response.send_modal(
            ReasonModal("Reason for voting Yes", self.cb_rq_yes)
        )

    async def cb_rf_yes(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Voted Yes:",
            value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*",
            inline=True,
        )
        # retrieve current amount of votes and iterate by 1
        yes_votes = new_embed.description[-1]
        yes_votes = int(yes_votes) + 1

        new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
        await interaction.message.edit(embed=new_embed)
        await interaction.response.defer()

        # automatically releases inmate at 3 yes votes
        if yes_votes >= 3:
            await interaction.message.edit(view=None)

            member_string = new_embed.footer.text
            member_id = int(member_string)
            member = interaction.guild.get_member(member_id)

            yes_men = []
            for field in new_embed.fields:
                if field.name == "Voted Yes:":
                    yes_men.append(field.value)

            # get person cases
            case_history = {}
            with open(self.case_history_file, "rb") as file:
                case_history = pickle.load(file)

            user_history = case_history[member_id][
                ::-1
            ]  # filter for member_id, most recent first

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
            await ban(self.config, member, "rf", reason=f"Reformation Failed: {reason}")

            # transript
            with open(self.config.datafiles.reformation_cases, "rb") as file:
                reformation_list = pickle.load(file)
            room_channel_name = reformation_list[member.id][0]
            room_channel = nextcord.utils.get(
                interaction.guild.channels, name=room_channel_name
            )

            transcript = await export(room_channel, military_time=True)
            await room_channel.delete()

            yes_list = "\n• ".join(yes_men)

            embed = nextcord.Embed(
                title="Reformation Failed",
                description=f"Reformation Inmate {member.name} has been deemed unreformable by\n•{yes_list}\n"
                f"\nInitial reason for Reformation was: `{reason}`. They have been banned automatically.",
                color=nextcord.Color.from_rgb(0, 0, 0),
            )

            if transcript is None:
                channel = interaction.guild.get_channel(
                    self.config.channels.teachers_lounge
                )
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")
            else:
                transcript_file = nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{room_channel_name}.html",
                )

            channel = self.bot.get_channel(self.config.channels.alert)
            await channel.send(embed=embed)

            channel = self.bot.get_channel(self.config.channels.logging)
            await channel.send(embed=embed)

            channel = self.bot.get_channel(self.config.channels.mod_logs)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(
                self.config.channels.teachers_lounge
            )
            await channel.send(embed=embed, file=transcript_file)

    async def cb_rf_yes_open_modal(self, interaction: nextcord.Interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message(
                    "You already voted", ephemeral=True
                )
                return

        await interaction.response.send_modal(
            ReasonModal("Reason for voting Yes", self.cb_rf_yes)
        )

    async def cb_no(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Voted No:",
            value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*",
            inline=True,
        )
        await interaction.message.edit(embed=new_embed)

    async def cb_no_open_modal(self, interaction: nextcord.Interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message(
                    "You already voted", ephemeral=True
                )
                return

        await interaction.response.send_modal(
            ReasonModal("Reason for voting No", self.cb_no)
        )

    async def cb_maybe(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Voted Maybe:",
            value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*",
            inline=True,
        )
        await interaction.message.edit(embed=new_embed)

    async def cb_maybe_open_modal(self, interaction: nextcord.Interaction):
        # check if user has already voted
        for field in interaction.message.embeds[0].fields:
            if field.value.splitlines()[0] == interaction.user.mention:
                await interaction.response.send_message(
                    "You already voted", ephemeral=True
                )
                return

        await interaction.response.send_modal(
            ReasonModal("Reason for voting Maybe", self.cb_maybe)
        )

    @reformation.subcommand(
        name="query_release",
        description="Query releasing a user from reformation centre.",
    )
    async def reformation_query(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to send to reformation", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for sending to reformation",
            required=True,
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == self.config.roles.reformation:
                is_in_reformation = True
        if not is_in_reformation:
            await interaction.send("Member is not in reformation.")
            return

        await interaction.response.defer()

        embedVar = SersiEmbed(
            title=f"Reformation Query: **{member.name}** ({member.id})",
            description=f"Reformation Inmate {member.name} was deemed well enough to start a query about their "
            f"release\nQuery started by {interaction.user.mention} ({interaction.user.id})\n\nYes Votes: 0",
            color=nextcord.Color.from_rgb(237, 91, 6),
            footer=f"{member.id}",
            fields={
                "Reason": reason,
            },
        )

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

        channel = self.bot.get_channel(self.config.channels.alert)
        await channel.send(embed=embedVar, view=button_view)

    @reformation.subcommand(
        name="query_failed", description="Query a ban of failed reformation inmate."
    )
    async def reformation_failed(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to ban", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for banning member",
            required=False,
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == self.config.roles.reformation:
                is_in_reformation = True
        if not is_in_reformation:
            await interaction.send("Member is not in reformation.")
            return

        await interaction.response.defer()

        embedVar = SersiEmbed(
            title=f"Reformation Failed Query: **{member.name}** ({member.id})",
            description=f"Reformation Inmate {member.name} seems to not be able to be reformed. Should the "
            f"reformation process therefore be given up and the user be banned?\nQuery"
            f" started by {interaction.user.mention} ({interaction.user.id})\n\nYes Votes: 0",
            color=nextcord.Color.from_rgb(237, 91, 6),
            footer=f"{member.id}",
            fields={
                "Reason": reason,
            },
        )

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

        channel = self.bot.get_channel(self.config.channels.alert)
        await channel.send(embed=embedVar, view=button_view)

    @reformation.subcommand(name="release", description="Release a user from reformation centre.")
    async def reformation_release(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            description="Member to release", required=True
        ),
        reason: str = nextcord.SlashOption(
            description="Reason for releasing member",
            required=True,
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_senior_mod):
            return
        
        # member have reformation role check
        is_in_reformation = False
        for role in member.roles:
            if role.id == self.config.roles.reformation:
                is_in_reformation = True
        if not is_in_reformation:
            await interaction.send("Member is not in reformation.")
            return
        
        await interaction.response.defer()

        @ConfirmView.query(
            title="Release Member from reformation",
            prompt="Following member will be released from reformation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            },
        )
        async def execute(*args, **kwargs):
            # remove reformation role
            await remove_role(
                member,
                self.config.roles.reformation,
                interaction.guild,
                reason
            )

            # add civil engineering initiate role
            await give_role(
                member,
                self.config.roles.civil_engineering_initiate,
                interaction.guild,
                reason
            )

            # logging

            embed = SersiEmbed(
                title="User Has Been Released from Reformation",
                description=f"Senior Moderator {interaction.user.mention} ({interaction.user.id}) has released user {member.mention}"
                f" ({member.id}) from reformation.\n\n" + f"**__Reason:__**\n{reason}",
                color=nextcord.Color.from_rgb(237, 91, 6),
            )

            channel = interaction.guild.get_channel(self.config.channels.logging)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(self.config.channels.teachers_lounge)
            await channel.send(embed=embed)

            channel = interaction.guild.get_channel(self.config.channels.reform_public_log)
            await channel.send(embed=embed)

            await interaction.send(f"**{member.name}** ({member.id}) has been released from reformation.")
        
        await execute(self.bot, self.config, interaction)

    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        reformation_role = member.get_role(self.config.roles.reformation)

        if reformation_role is not None:
            async for ban_entry in member.guild.bans():
                if member.id == ban_entry.user.id:
                    ban_embed = nextcord.Embed(
                        title=f"Reformation inmate **{member}** ({member.id}) banned!",
                        colour=nextcord.Color.from_rgb(237, 91, 6),
                    )
                    ban_embed.add_field(name="Reason:", value=ban_entry.reason)
                    channel = self.bot.get_channel(self.config.channels.mod_logs)
                    await channel.send(embed=ban_embed)

                    # transript
                    with open(self.config.datafiles.reformation_cases, "rb") as file:
                        reformation_list = pickle.load(file)
                    room_channel_name = reformation_list[member.id][0]
                    room_channel = nextcord.utils.get(
                        member.guild.channels, name=room_channel_name
                    )

                    transcript = await export(room_channel, military_time=True)

                    if transcript is None:
                        channel = member.guild.get_channel(
                            self.config.channels.teachers_lounge
                        )
                        await channel.send(
                            f"{self.sersifail} Failed to Generate Transcript!"
                        )
                    else:
                        transcript_file = nextcord.File(
                            io.BytesIO(transcript.encode()),
                            filename=f"transcript-{room_channel_name}.html",
                        )

                    await room_channel.delete()
                    channel = member.guild.get_channel(
                        self.config.channels.teachers_lounge
                    )
                    await channel.send(embed=ban_embed, file=transcript_file)

                    return

            # member not yet banned, proceed to ban
            # await member.ban(reason="Left while in reformation centre.", delete_message_days=0)
            await ban(
                self.config, member, "leave", reason="Left while in reformation centre."
            )

            channel = self.bot.get_channel(self.config.channels.alert)
            embed = nextcord.Embed(
                title=f"User **{member}** ({member.id}) has left the server while in the reformation centre!",
                description=f"User has left the server while having the <@&{self.config.roles.reformation}> role. "
                f"They have been banned automatically.",
                colour=nextcord.Color.from_rgb(237, 91, 6),
            )

            # transript
            with open(self.config.datafiles.reformation_cases, "rb") as file:
                reformation_list = pickle.load(file)
            room_channel_name = reformation_list[member.id][0]
            room_channel = nextcord.utils.get(
                member.guild.channels, name=room_channel_name
            )

            transcript = await export(room_channel, military_time=True)

            if transcript is None:
                channel = member.guild.get_channel(self.config.channels.teachers_lounge)
                await channel.send(f"{self.sersifail} Failed to Generate Transcript!")
            else:
                transcript_file = nextcord.File(
                    io.BytesIO(transcript.encode()),
                    filename=f"transcript-{room_channel_name}.html",
                )

            await room_channel.delete()
            channel = member.guild.get_channel(self.config.channels.teachers_lounge)
            await channel.send(embed=embed, file=transcript_file)


class ReasonModal(nextcord.ui.Modal):
    def __init__(self, name: str, cb: callable):
        super().__init__(name)
        self.field = nextcord.ui.TextInput(
            label="Reason",
            min_length=4,
            max_length=256,
            required=True,
            placeholder="please provide a reason",
        )
        self.add_item(self.field)
        self.callback = cb


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Reformation(bot, kwargs["config"]))
