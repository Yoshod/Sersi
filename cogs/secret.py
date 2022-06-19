import nextcord
import uuid
import pickle

from nextcord.ext import commands
from baseutils import *


class Secret(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.active_secret_dms = []
        self.filename = "secret_dms.pkl"
        try:
            with open(self.filename, 'x'):  # creates file if not exists
                pass
        except FileExistsError:             # ignores error if it does
            pass

    @commands.command(aliases=['da', 'deanonymize'])
    async def deanonymise(self, ctx, id_num, *, reason=""):
        if not await permcheck(ctx, is_dark_mod):
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

        member = ctx.guild.get_member(int(member_snowflake))

        if member is not None:
            await ctx.send(f"Message with ID `{id_num}` was sent by {member.mention} ({member.id})")
        else:
            await ctx.send(f"Message with ID `{id_num}` was sent by `{member_snowflake}`, who is not found on this server")

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

                secretlist[ID] = message.author.id
                print(f"Current secret dict: {secretlist}")

                with open(self.filename, 'wb') as file:
                    pickle.dump(secretlist, file)

                dm_channel = self.bot.get_channel(get_config_int("CHANNELS", "dm forward"))
                channel_webhooks = await dm_channel.webhooks()

                for webhook in channel_webhooks:                  # tries to find existing webhook
                    if webhook.name == "dm webhook by sersi":
                        await webhook.send(embed=secret, username="Anonymous User")
                        msg_sent = True

                if not msg_sent:                          # creates webhook if none found
                    webhook = await dm_channel.create_webhook(name="dm webhook by sersi")
                    await webhook.send(embed=secret, username="Anonymous User")
                    msg_sent = True


def setup(bot):
    bot.add_cog(Secret(bot))
