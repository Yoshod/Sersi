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

        channel = self.bot.get_channel(getLoggingChannel(ctx.message.guild.id))
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
                channel = self.bot.get_channel(getLoggingChannel(ctx.message.guild.id))
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

    @commands.command()
    async def receivedms(self, ctx):
        if ctx.guild.id == 977377117895536640:
            if self.recdms:
                self.recdms = False
                await ctx.send("received DMs will no longer be posted to <#982057670594928660>")
            else:
                self.recdms = True
                await ctx.send("received DMs will now be posted to <#982057670594928660>")
        else:
            await ctx.send("experimental functionality is not available on ASC")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.recdms:
            return

        dm_channel = self.bot.get_channel(982057670594928660)
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
