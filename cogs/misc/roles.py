from nextcord.ext import commands
from configutils import Configuration
import datetime
import pytz


class Roles(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:  # do not apply newbie role do bots
            return

        newbie_role = member.guild.get_role(self.config.roles.newbie)
        await member.add_roles(newbie_role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # ignores message if message is by bot
            return

        if message.guild is None:  # ignores if message is a DM
            return

        newbie_role = message.guild.get_role(self.config.roles.newbie)

        if newbie_role in message.author.roles:
            now = datetime.datetime.now()
            aware_now = now.replace(tzinfo=pytz.UTC)
            time_passed = aware_now - message.author.joined_at

            if time_passed.days > 3:
                await message.author.remove_roles(newbie_role)


def setup(bot, **kwargs):
    bot.add_cog(Roles(bot, kwargs["config"]))
