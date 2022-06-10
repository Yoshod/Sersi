import nextcord

from nextcord.ext import commands
from baseutils import *


class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.recdms = False

    @commands.command()
    async def dm(self, ctx, recipient: nextcord.Member, *message):
        msg = " ".join(message)
        if msg == "":
            return
        elif not isMod(ctx.author.roles):
            await ctx.send("<:sersifail:979070135799279698> Only moderators can use this command.")
            return

        await recipient.send(msg)
        await ctx.send(f"<:sersisuccess:979066662856822844> Direkt Message sent to {recipient}!")

        channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
        logging = nextcord.Embed(
            title="DM Sent",
            description="A DM has been sent.",
            color=nextcord.Color.from_rgb(237, 91, 6))
        logging.add_field(name="Sender:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Recipient:", value=recipient.mention, inline=False)
        logging.add_field(name="Message Content:", value=msg, inline=False)
        await channel.send(embed=logging)

    @commands.command()
    async def dmTest(self, ctx, userId=None, *, args=None):
        if isMod(ctx.author.roles):
            if userId is not None and args is not None:
                target = userId
                targetId = "Null"
                for i in range(len(target)):
                    currentChar = target[i]
                    charTest = currentChar.isdigit()
                    print(charTest)
                    if charTest is True and targetId != "Null":
                        targetId = str(targetId) + str(target[i])
                        print("Character is number")
                    elif charTest is True and targetId == "Null":
                        targetId = str(target[i])
                targetId = int(targetId)
                user = bot.get_user(targetId)
                try:
                    await user.send(args)

                except:
                    await ctx.send("The message failed to send. Reason: Could not DM user.")

                # Logging
                channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
                embedVar = nextcord.Embed(
                    title="DM Sent",
                    description=f"A DM has been sent.\n\n__Sender:__\n{ctx.author.mention}\n\n__Recipient:__\n{userId}\n\n__Message Content:__\n{args}",
                    color=nextcord.Color.from_rgb(237, 91, 6))
                await channel.send(embed=embedVar)

            elif userId is None and args is not None:
                await ctx.send("No user was specified.")

            elif userId is not None and args is None:
                await ctx.send("No message was specified.")
            else:
                await ctx.send("How the fuck did this error appear?")
        else:
            await ctx.send("<:sersifail:979070135799279698> Only moderators can use this command.")


    @commands.Cog.listener()
    async def on_message(self, message):
        if not get_config("MSG", "forward dms", "false").lower() == "true":
            return

        dm_channel = self.bot.get_channel(get_config_int("CHANNELS", "dm forward"))   # please name and config
        if message.guild is None and message.author != self.bot.user:
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
