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
        role_obj = member.guild.get_role(get_config_int('ROLES', 'newbie'))
        await member.add_roles(role_obj)

    @commands.Cog.listener()
    async def on_message(self, message):
        print("e")
        print(message)
        role_obj = message.guild.get_role(get_config_int('ROLES', 'newbie'))
        print(message.author.roles)
        if role_obj in message.author.roles:
            print(f"{role_obj}")

            now = datetime.datetime.now()
            aware_now = now.replace(tzinfo=pytz.UTC)
            time_passed = aware_now - message.author.joined_at
            print(time_passed)

            if time_passed.days > 3:
                await message.author.remove_roles(role_obj)


def setup(bot):
    bot.add_cog(Roles(bot))
