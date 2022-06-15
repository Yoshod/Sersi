import nextcord
import asyncio
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
    async def clear(self, ctx, amount, member: nextcord.Member = None):
        deleted_msgs = []
        try:
            amount = int(amount)

        except ValueError:
            await ctx.send(f"{self.sersifail} Amount \"{amount}\" is not an integer. ")
            return

        if not await permcheck(ctx, is_mod):
            return

        elif amount is None:
            await ctx.send(f"{self.sersifail} You must specify how many messages you wish to purge.")
            return

        elif amount < 1:
            await ctx.send(f"{self.sersifail} You must delete at least one message.")
            return

        elif amount > self.MAXMESSAGES:
            await ctx.send(f"{self.sersifail} You cannot delete more than 100 messages.")
            return

        elif member is None:
            deleted_msgs = await ctx.channel.purge(limit=amount + 1)

        elif member is not None:
            deleted_msgs = await ctx.channel.purge(limit=amount + 1, check=lambda x: True if (msg.author.id == member.id) else False)

        # LOGGING
        # await asyncio.sleep(2)
        # async for entry in ctx.guild.audit_logs(limit=1, action=nextcord.AuditLogAction.message_bulk_delete):
        #     deletion_count = entry.extra['count']
        deletion_count = len(deleted_msgs) - 1

        logging = nextcord.Embed(
            title="Messages Purged",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Messages Requested:", value=amount, inline=False)
        logging.add_field(name="Messages Purged:", value=deletion_count, inline=False)
        logging.add_field(name="Channel Purged:", value=ctx.channel.mention, inline=False)
        if member is not None:
            logging.add_field(name="User Targeted:", value=f"{member.mention} ({member.id})")

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['tp', 'timedpurge'])
    @commands.cooldown(1, 900, commands.BucketType.user)
    async def timed_purge(self, ctx, time=None, target: nextcord.Member = None):
        deleted_msgs = []
        try:
            time = re.sub(r"[^0-9]", "", time)
            time = int(time)

        except ValueError:
            await ctx.send(f"{self.sersifail} `{time}` is not a valid time.")
            return

        if not await permcheck(ctx, is_senior_mod):
            await ctx.send(f"{self.sersifail} Only Senior Moderators or higher can use this command!")
            return

        elif time < 1:
            await ctx.send(f"{self.sersifail} The minimum time is one minute.")
            return

        elif time is None:
            await ctx.send(f"{self.sersifail} You must specify a length of time.")
            return

        elif time > self.MAXTIME:
            await ctx.send(f"{self.sersifail} The length of time specified is greater than the maximum value.")
            return

        elif target is None:
            after = ctx.message.created_at - timedelta(minutes=time)
            deleted_msgs = await ctx.channel.purge(limit=10 * time, after=after)

        elif target is not None:
            after = ctx.message.created_at - timedelta(minutes=time)
            deleted_msgs = await ctx.channel.purge(limit=10 * time, check=lambda x: True if (message.author.id == target.id) else False, after=after)

        # LOGGING
        # await asyncio.sleep(2)
        # async for entry in ctx.guild.audit_logs(limit=1, action=nextcord.AuditLogAction.message_bulk_delete):
        #     deletion_count = entry.extra['count']
        deletion_count = len(deleted_msgs) - 1

        logging = nextcord.Embed(
            title="Messages Purged",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Time Specified:", value=f"{time} minutes", inline=False)
        logging.add_field(name="Messages Purged:", value=deletion_count, inline=False)
        logging.add_field(name="Channel Purged:", value=ctx.channel.mention, inline=False)
        if target is not None:
            logging.add_field(name="User Targeted:", value=f"{member.mention} ({member.id})")

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['pu', 'purgeuntil'])
    async def purge_until(self, ctx, message_id=None):
        channel = ctx.message.channel
        try:
            message = await channel.fetch_message(int(message_id))
        except nextcord.errors.NotFound:
            await ctx.send(f"{self.sersifail} The message specified has not been found.")
            return

        await ctx.message.delete()
        await channel.purge(after=message)

        # LOGGING
        await asyncio.sleep(2)
        async for entry in ctx.guild.audit_logs(limit=1, action=nextcord.AuditLogAction.message_bulk_delete):
            deletion_count = entry.extra['count']

        logging = nextcord.Embed(
            title="Messages Purged",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="Message Specified:", value=message.jump_url, inline=False)
        logging.add_field(name="Messages Purged:", value=(f"{int(deletion_count) - 1}"), inline=False)
        logging.add_field(name="Channel Purged:", value=ctx.channel.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)


def setup(bot):
    bot.add_cog(Purge(bot))
