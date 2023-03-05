import nextcord
from nextcord.ext import commands

from configutils import Configuration
from permutils import permcheck, is_staff


class Messages(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    @commands.command()
    async def dm(self, ctx: commands.Context, recipient: nextcord.Member, *, message):
        if not await permcheck(ctx, is_staff):
            return

        if message == "":
            await ctx.send(f"{self.sersifail} no message provided.")
            return

        await recipient.send(message)
        await ctx.send(f"{self.sersisuccess} Direkt Message sent to {recipient}!")

        channel = self.bot.get_channel(self.config.channels.logging)
        logging = nextcord.Embed(
            title="DM Sent",
            description="A DM has been sent.",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        logging.add_field(name="Sender:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Recipient:", value=recipient.mention, inline=False)
        logging.add_field(name="Message Content:", value=message, inline=False)
        await channel.send(embed=logging)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Messages(bot, kwargs["config"]))
