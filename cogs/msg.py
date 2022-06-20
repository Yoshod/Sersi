import nextcord
import uuid
import pickle
from nextcord.ext import commands
from nextcord.ui import Button, View

from configutils import get_config, get_config_int, get_config_bool
from permutils import permcheck, is_mod, is_senior_mod, cb_is_mod
from encryptionutils import *
from slurdetector import detectSlur


class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.recdms = False
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.active_secret_dms = []
        self.filename = ("secret_dms.pkl")

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

    @commands.command(aliases=['da', 'deanonymize'])
    async def deanonymise(self, ctx, id_num, *, reason=""):
        if not await permcheck(ctx, is_senior_mod):
            return
        elif reason == "":
            await ctx.send(f"{self.sersifail} Please provide a reason!")
            return

        secretlist = {}
        with open(self.filename, 'rb') as f:
            try:
                secretlist = pickle.load(f)
            except EOFError:
                pass

        try:
            member_snowflake = secretlist[id_num]
        except KeyError:
            await ctx.send(f"{self.sersifail} No entry found with ID {id_num}")
            return

        member_id = unencrypt_data(member_snowflake)
        member = ctx.guild.get_member(int(member_id))

        if member is not None:
            await ctx.send(f"Message with ID `{id_num}` was sent by {member.mention} ({member.id})")
            channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
            logging = nextcord.Embed(
                title="User Deanonymised",
                description="An anonymous message has had their user revealed.",
                color=nextcord.Color.from_rgb(237, 91, 6))
            logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
            logging.add_field(name="Message Revealed:", value=id_num, inline=False)
            logging.add_field(name="Reason:", value=reason, inline=False)
            await channel.send(embed=logging)
            channel = self.bot.get_channel(get_config_int('CHANNELS', 'modlogs'))
            await channel.send(embed=logging)
        else:
            await ctx.send(f"Message with ID `{id_num}` was sent by `{member_id}`, who is not found on this server")

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.guild is None and message.author != self.bot.user:

            if message.content.lower() == "secret":
                self.active_secret_dms.append(message.author.id)
                await message.author.send("The next DM will be secret! This is not an invitation to break the rules.")
                return

            elif message.author.id in self.active_secret_dms:
                self.active_secret_dms.remove(message.author.id)
                ID = str(uuid.uuid4())

                secret = nextcord.Embed(
                    title="Secret Message",
                    description=message.content,
                    colour=nextcord.Colour.blurple())
                secret.set_footer(text=ID)

                secretlist = {}
                with open(self.filename, 'rb') as f:
                    try:
                        secretlist = pickle.load(f)
                    except EOFError:
                        pass

                # encrypt author id
                secure_author = encrypt_data(str(message.author.id))
                secretlist[ID] = secure_author
                print(f"Current secret dict: {secretlist}")

                with open(self.filename, 'wb') as file:
                    pickle.dump(secretlist, file)

                dm_channel = self.bot.get_channel(get_config_int("CHANNELS", "secret"))
                channel_webhooks = await dm_channel.webhooks()

                for webhook in channel_webhooks:                  # tries to find existing webhook
                    if webhook.name == "dm webhook by sersi":
                        await webhook.send(embed=secret, username="Anonymous User")
                        msg_sent = True

                detected_slurs = detectSlur(message.content)
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

            else:
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
