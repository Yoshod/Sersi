import nextcord

from nextcord.ext import commands
from baseutils import *


class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.recdms = False
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')

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

    @commands.Cog.listener()
    async def on_message(self, message):
        if not get_config_bool("MSG", "forward dms", False):
            return

        dm_channel = self.bot.get_channel(get_config_int("CHANNELS", "dm forward"))
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
