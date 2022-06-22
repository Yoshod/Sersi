import nextcord
import uuid
import pickle
from nextcord.ext import commands
from nextcord.ui import Button, View

from baseutils import ConfirmView, DualCustodyView
from configutils import get_config, get_config_int, get_config_bool
from permutils import permcheck, is_dark_mod, is_full_mod, is_mod, cb_is_mod
from encryptionutils import encrypt_data, unencrypt_data
from slurdetector import detect_slur


class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.recdms = False
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.active_secret_dms = []
        self.filename = ("Files/AnonMessages/secret_dms.pkl")
        self.banned_filename = "Files/AnonMessages/banned.csv"
        self.banlist = {}

        try:
            with open(self.banned_filename, 'x'):  # creates CSV file if not exists
                pass
        except FileExistsError:             # ignores error if it does
            pass
        self.loadbanlist()

    def loadbanlist(self):
        with open(self.banned_filename, "r") as file:
            for line in file:
                line = line.replace('\n', '')
                [user_id, reason] = line.split(";", maxsplit=1)
                self.banlist[int(user_id)] = reason           # if the key is not an int, the guild.get_member() won't work

    async def cb_action_taken(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Action Taken By", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        embedLogVar = nextcord.Embed(
            title="Action Taken Pressed",
            description="Action has been taken by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_acceptable_use(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Usage Deemed Acceptable By", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.light_grey()
        await interaction.message.edit(embed=new_embed, view=None)

        # Logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        embedLogVar = nextcord.Embed(
            title="Acceptable Use Pressed",
            description="Usage of a slur has been deemed acceptable by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_false_positive(self, interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(name="Deemed As False Positive By:", value=interaction.user.mention, inline=False)
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'false positives'))

        embedVar = nextcord.Embed(
            title="Marked as false positive",
            color=nextcord.Color.from_rgb(237, 91, 6))

        for field in new_embed.fields:
            if field.name in ["Context:", "Slurs Found:"]:
                embedVar.add_field(name=field.name, value=field.value, inline=False)

        embedVar.add_field(name="Report URL:", value=interaction.message.jump_url, inline=False)
        await channel.send(embed=embedVar)

        # Logging
        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        embedLogVar = nextcord.Embed(
            title="False Positive Pressed",
            description="Detected slur has been deemed a false positive by a moderator in response to a report.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embedLogVar.add_field(name="Report:", value=interaction.message.jump_url, inline=False)
        embedLogVar.add_field(name="Moderator:", value=f"{interaction.user.mention} ({interaction.user.id})", inline=False)
        await channel.send(embed=embedLogVar)

    async def cb_anonmute_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            if field.name == "Reason":
                reason = field.value
        member = interaction.guild.get_member(member_id)

        with open(self.banned_filename, "a") as file:
            file.write(f"{member.id};{reason}\n")

        self.loadbanlist()
        await interaction.message.edit(f"{self.sersisuccess} User muted in anonymous messages.", embed=None, view=None)

        # LOGGING

        logging = nextcord.Embed(
            title="User Muted (Anonymous Messages)",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        logging.add_field(name="Moderator:", value=interaction.user.mention, inline=False)
        logging.add_field(name="User Added:", value=member.mention, inline=False)
        logging.add_field(name="Reason:", value=reason, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['anonban', 'anonmute'])
    async def anonymousmute(self, ctx, member: nextcord.Member, *, reason):
        if not await permcheck(ctx, is_mod):
            return
        elif member.id in self.banlist:
            await ctx.send(f"{self.sersifail} {member} is already banned from participating in anonymous messages.!")
            return
        
        dialog_embed = nextcord.Embed(
           title="Secret Messages Mute",
           description="Following member will be forbidden from sending secret messages:",
           color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)

        await ConfirmView(self.cb_anonmute_proceed).send_as_reply(ctx, embed=dialog_embed)

    @commands.command(aliases=['lam', 'am', 'listam', 'lab', 'ab', 'listab'])
    async def listanonymousmutes(self, ctx):
        """lists all members currently muted in anonymous messages"""
        if not await permcheck(ctx, is_mod):
            return

        nicelist = ""
        for entry in self.banlist:

            member = ctx.guild.get_member(entry)
            if member is None:
                nicelist = nicelist + f"**{entry}**: {self.banlist[entry]}\n"
            else:
                nicelist = nicelist + f"**{member}** ({member.id}): {self.banlist[entry]}\n"

        listembed = nextcord.Embed(
            title="Anonymous Messages Muted Member List",
            description=nicelist,
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        await ctx.send(embed=listembed)

    async def cb_anonunmute_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        self.banlist.pop(member.id)
        print(self.banlist)

        with open(self.banned_filename, "w") as file:
            for entry in self.banlist:
                file.write(f"{entry};{self.banlist[entry]}\n")

        await interaction.message.edit(f"{self.sersisuccess} User has been unmuted in anonymous messages.", embed=None, view=None)

        # LOGGING

        logging = nextcord.Embed(
            title="User Unmuted (Anonymous Messages)",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        logging.add_field(name="Moderator:", value=interaction.user.mention, inline=False)
        logging.add_field(name="User Unmuted:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['anonunmute', 'unmuteanon', 'umanon', 'anonum'])
    async def anonymousunmute(self, ctx, member: nextcord.Member):
        """removes user from anonymous messages mute"""
        if not await permcheck(ctx, is_mod):
            return
        if member.id not in self.banlist:
            await ctx.send(f"{self.sersifail} Member {member} not found on list!")

        dialog_embed = nextcord.Embed(
           title="Secret Messages Unute",
           description="Following member will no longer be forbidden from sending secret messages:",
           color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_anonunmute_proceed).send_as_reply(ctx, embed=dialog_embed)

    @commands.command(aliases=['checkmuted', 'checkmute'])
    async def checkanonmutes(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_mod):
            return

        if member.id in self.banlist:
            await ctx.send(f"{self.sersifail} Member {member} is muted in anonymous messages!")
            return True
        else:
            await ctx.send(f"{self.sersisuccess} Member {member} is not muted in anonymous messages!")
            return False

    @commands.command()
    async def dm(self, ctx, recipient: nextcord.Member, *, message):
        if not await permcheck(ctx, is_mod):
            return

        if message == "":
            ctx.send(f"{self.sersifail} no message provided.")
            return

        await recipient.send(message)
        await ctx.send(f"{self.sersisuccess} Direkt Message sent to {recipient}!")

        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        logging = nextcord.Embed(
            title="DM Sent",
            description="A DM has been sent.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        logging.add_field(name="Sender:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Recipient:", value=recipient.mention, inline=False)
        logging.add_field(name="Message Content:", value=message, inline=False)
        await channel.send(embed=logging)

    async def cb_da_confirm(self, interaction):
        mod_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "Anonymous Message ID":
                secret_id = field.value
            if field.name == "Moderator ID":
                mod_id = int(field.value)
            if field.name == "Reason":
                reason = field.value

        secretlist = {}
        with open(self.filename, 'rb') as file:
            try:
                secretlist = pickle.load(file)
            except EOFError:
                pass

        member_snowflake, nonce_snowflake, tag_snowflake = secretlist[secret_id]

        member_id = unencrypt_data(member_snowflake, nonce_snowflake, tag_snowflake)
        member = interaction.guild.get_member(int(member_id))

        if member is not None:
            da_embed = nextcord.Embed(
                title="User Deanonymised",
                description=(f"The user behind message ```{secret_id}``` is {member.mention} ({member.id})"),
                color=nextcord.Color.from_rgb(237, 91, 6))
            await interaction.message.edit(embed=da_embed, view=None)

            logging = nextcord.Embed(
                title="User Deanonymised",
                description="An anonymous message has had their user revealed.",
                color=nextcord.Color.from_rgb(237, 91, 6))

            if mod_id == 0:
                logging.add_field(name="Moderator:", value=interaction.user.mention, inline=False)
            else:
                logging.add_field(name="Moderator:", value=interaction.guild.get_member(mod_id).mention, inline=False)
                logging.add_field(name="Confirming Moderator:", value=interaction.user.mention, inline=False)

            logging.add_field(name="Message Revealed:", value=secret_id, inline=False)
            logging.add_field(name="Reason:", value=reason, inline=False)

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
            await channel.send(embed=logging)
            channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
            await channel.send(embed=logging)
        else:
            await interaction.message.edit(f"Message with ID `{secret_id}` was sent by `{member_id}`, who is not found on this server", embed=None, view=None)

    async def cb_da_proceed(self, interaction):
        for field in interaction.message.embeds[0].fields:
            if field.name == "Anonymous Message ID":
                secret_id = field.value
            if field.name == "Reason":
                reason = field.value

        dialog_embed = nextcord.Embed(
            title="Deanonymise message",
            description="Following message will be deanonymised:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="Anonymous Message ID", value=secret_id)
        dialog_embed.add_field(name="Moderator", value=interaction.user.mention)
        dialog_embed.add_field(name="Moderator ID", value=interaction.user.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'alert'))
        view = DualCustodyView(self.cb_da_confirm, interaction.user, is_full_mod)
        await view.send_dialogue(channel, embed=dialog_embed)

        await interaction.message.edit(f"Deanonymisation of Message with ID `{secret_id}` was sent for approval by another moderator", embed=None, view=None)

    @commands.command(aliases=['da', 'deanonymize'])
    async def deanonymise(self, ctx, id_num, *, reason=""):
        if not await permcheck(ctx, is_mod):
            return
        elif reason == "":
            await ctx.send(f"{self.sersifail} Please provide a reason!")
            return

        secretlist = {}
        with open(self.filename, 'rb') as file:
            try:
                secretlist = pickle.load(file)
            except EOFError:
                pass

        if id_num not in secretlist.keys():
            await ctx.send(f"{self.sersifail} No entry found with ID {id_num}")
            return

        dialog_embed = nextcord.Embed(
            title="Deanonymise message",
            description="Following message will be deanonymised:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="Anonymous Message ID", value=id_num)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)

        if is_dark_mod(ctx.author):
            await ConfirmView(self.cb_da_confirm).send_as_reply(ctx, embed=dialog_embed)
        else:
            await ConfirmView(self.cb_da_proceed).send_as_reply(ctx, embed=dialog_embed)

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild is None and message.author != self.bot.user:

            if message.content.lower() == "secret" and message.author.id not in self.banlist:
                self.active_secret_dms.append(message.author.id)
                await message.author.send("The next DM will be secret! Do not share personal private information or impersonate other users on the server. Rule breakers will be deanonymised and punished.")
                return

            elif message.author.id in self.active_secret_dms and message.author.id not in self.banlist:
                self.active_secret_dms.remove(message.author.id)
                ID = str(uuid.uuid4())

                desc = ""
                if len(message.content) < 1:
                    desc = "This message has no content, likely an image or file."
                else:
                    desc = message.content

                secret = nextcord.Embed(
                    title="Secret Message",
                    description=desc,
                    colour=nextcord.Colour.blurple())
                secret.set_footer(text=ID)

                for attachment in message.attachments:
                    if "image" in attachment.content_type:      # like image/jpeg, image/png
                        secret.set_image(url=attachment.url)
                        break

                secretlist = {}
                with open(self.filename, 'rb') as file:
                    try:
                        secretlist = pickle.load(file)
                    except EOFError:    # file is empty
                        pass

                # encrypt author id
                secure_author, nonce, tag = encrypt_data(str(message.author.id))
                secretlist[ID] = (secure_author, nonce, tag)

                with open(self.filename, 'wb') as file:
                    pickle.dump(secretlist, file)

                dm_channel = self.bot.get_channel(get_config_int("CHANNELS", "secret"))
                channel_webhooks = await dm_channel.webhooks()

                for webhook in channel_webhooks:                  # tries to find existing webhook
                    if webhook.name == "dm webhook by sersi":
                        await webhook.send(embed=secret, username="Anonymous User")
                        msg_sent = True

                detected_slurs = detect_slur(message.content)

                if len(detected_slurs) > 0:  # checks slur heat
                    channel = self.bot.get_channel(get_config_int('CHANNELS', 'alert'))
                    slurembed = nextcord.Embed(
                        title="Slur(s) Detected",
                        description="A slur has been detected in an anonymous message. If moderator action is required you should deanonymise the message.",
                        color=nextcord.Color.from_rgb(237, 91, 6)
                    )
                    slurembed.add_field(name="Message ID:", value=ID, inline=False)

                    if len(message.content) < 1024:
                        slurembed.add_field(name="Context:", value=message.content, inline=False)
                    else:
                        slurembed.add_field(name="Context:", value="`MESSAGE TOO LONG`", inline=False)

                    slurembed.add_field(name="Slurs Found:", value=", ".join(set(detected_slurs)), inline=False)
                    slurembed.set_footer(text="Sersi Slur Detection Alert")

                    action_taken = Button(label="Action Taken")
                    action_taken.callback = self.cb_action_taken

                    acceptable_use = Button(label="Acceptable Use")
                    acceptable_use.callback = self.cb_acceptable_use

                    false_positive = Button(label="False Positive")
                    false_positive.callback = self.cb_false_positive

                    button_view = View(timeout=None)
                    button_view.add_item(action_taken)
                    button_view.add_item(acceptable_use)
                    button_view.add_item(false_positive)
                    button_view.interaction_check = cb_is_mod

                    await channel.send(embed=slurembed, view=button_view)

                if not msg_sent:                          # creates webhook if none found
                    webhook = await dm_channel.create_webhook(name="dm webhook by sersi")
                    await webhook.send(embed=secret, username="Anonymous User")
                    msg_sent = True

            elif message.author.id in self.banlist and message.content.lower() == "secret":
                await message.author.send(f"{self.sersifail} You cannot send anonymous messages.")

            elif message.author.id in self.active_secret_dms and message.author.id in self.banlist:
                await message.author.send(f"{self.sersifail} You cannot send anonymous messages.")

            else:
                return
                if not get_config_bool("MSG", "forward dms", False):
                    return

                dm_channel = self.bot.get_channel(get_config_int("CHANNELS", "dm forward"))   # please name and config
                channel_webhooks = await dm_channel.webhooks()
                msg_sent = False

                for webhook in channel_webhooks:                  # tries to find existing webhook
                    if webhook.name == "dm webhook by sersi":
                        await webhook.send(message.content, username=message.author.display_name, avatar_url=message.author.display_avatar.url)
                        msg_sent = True

                if not msg_sent:                          # creates webhook if none found
                    webhook = await dm_channel.create_webhook(name="dm webhook by sersi")
                    await webhook.send(message.content, username=message.author.display_name, avatar_url=message.author.display_avatar.url)
                    msg_sent = True


def setup(bot):
    bot.add_cog(Messages(bot))
