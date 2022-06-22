import nextcord
from nextcord.ext import commands
from configutils import get_config_int
import datetime
import pytz


class Roles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:  # do not apply newbie role do bots
            return

        newbie_role = member.guild.get_role(get_config_int('ROLES', 'newbie'))
        await member.add_roles(newbie_role)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # ignores message if message is by bot
            return

        if message.guild is None:
            return

        newbie_role = message.guild.get_role(get_config_int('ROLES', 'newbie'))

        if newbie_role in message.author.roles:

            now = datetime.datetime.now()
            aware_now = now.replace(tzinfo=pytz.UTC)
            time_passed = aware_now - message.author.joined_at

            if time_passed.days > 3:
                await message.author.remove_roles(newbie_role)


def setup(bot):
    bot.add_cog(Roles(bot))
