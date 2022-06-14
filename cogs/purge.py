import nextcord
from nextcord.ext import commands
from baseutils import *
from datetime import timedelta


class Purge(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.MAXMESSAGES = 100
        self.MAXTIME = 15

    @commands.command(aliases=['p', 'massdelete', 'delete', 'del', 'purge'])
    async def clear(self, ctx, amount=None, target=None):
        if not is_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Only Moderators can use this command!")
            return

        elif amount is None:
            await ctx.send(f"{self.sersifail} You must specify how many messages you wish to purge.")
            return

        elif amount > self.MAXMESSAGES:
            await ctx.send(f"{self.sersifail} You cannot delete more than 100 messages.")
            return

        elif target is None:
            await ctx.channel.purge(limit=amount + 1)

        elif target is not None:
            await ctx.channel.parge(limit=amount + 1, check=lambda x: True if (message.author.id == target.id) else False)

        # LOGGING

        logging = nextcord.Embed(
            title="Messages Purged"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Messages Purged:", value=amount, inline=False)
        logging.add_field(name="Channel Purged:", value=ctx.channel.mention, inline=False)
        if target is not None:
            logging.add_field(name="User Targeted:", value=target)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['tp', 'timed purge'])
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def timed_purge(self, ctx, time=None, target=None):
        if not is_senior_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Only Senior Moderators or higher can use this command!")
            return

        elif time is None:
            await ctx.send(f"{self.sersifail} You must specify a length of time.")
            return

        elif time > self.MAXTIME:
            await ctx.send(f"{self.sersifail} The length of time specified is greater than the maximum value.")
            return

        elif target is None:
            after = ctx.message.created_at - timedelta(minutes=time)
            await channel.purge(limit=10 * time, after=after)

        elif target is not None:
            after = ctx.message.created_at - timedelta(minutes=time)
            await channel.purge(limit=10 * time, check=lambda x: True if (message.author.id == target.id) else False, after=after)

        # LOGGING

        logging = nextcord.Embed(
            title="Messages Purged"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Time Specified:", value=(f"{time} minutes"), inline=False)
        logging.add_field(name="Channel Purged:", value=ctx.channel.mention, inline=False)
        if target is not None:
            logging.add_field(name="User Targeted:", value=target)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)


def setup(bot):
    bot.add_cog(Purge(bot))
