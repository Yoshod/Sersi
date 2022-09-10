from configutils import get_config_int
from nextcord.ext import commands


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(get_config_int("GUILDS", "current"))

    @commands.Cog.listener()
    async def on_raw_message_delete(self, RawMessageDeleteEvent):
        channel = self.guild.get_channel(get_config_int("LOGGING", "deleted_messages"))
        await channel.send(RawMessageDeleteEvent.cached_message.content)


def setup(bot):
    bot.add_cog(Logging(bot))
