import nextcord

from nextcord.ext import commands
from baseutils import *


class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

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
                    description="A DM has been sent.\n\n__Sender:__\n{ctx.author.mention}\n\n__Recipient:__\n{userId}\n\n__Message Content:__\n{args}",
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


def setup(bot):
    bot.add_cog(Messages(bot))
