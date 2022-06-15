import nextcord
from nextcord.ext import commands
from baseutils import *


class Watchlist(commands.Cog):

    def __init__(self, bot):
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.filename = "watchlist.csv"
        self.bot = bot
        self.watchlist = {}
        try:
            with open(self.filename, 'x'):  # creates CSV file if not exists
                pass
        except FileExistsError:             # ignores error if it does
            pass
        self.loadwatchlist()

    def loadwatchlist(self):
        with open(self.filename, "r") as file:
            for line in file:
                line = line.replace('\n', '')
                [user_id, reason] = line.split(";", maxsplit=1)
                self.watchlist[int(user_id)] = reason           # if the key is not an int, the guild.get_member() won't work

    @commands.command(aliases=['wl', 'wluser', 'addwl', 'watchlist'])
    async def watchlistuser(self, ctx, member: nextcord.Member, **reason):
        """sets user onto moderator watchlist"""
        if not is_dark_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission!")
            return
        elif member.id in self.watchlist:
            await ctx.send(f"{self.sersifail} {member} already on watchlist!")
            return

        reason_string = " ".join(reason)

        with open(self.filename, "a") as file:
            file.write(f"{member.id};{reason_string}\n")

        self.loadwatchlist()
        await ctx.send(f"{self.sersisuccess} User added to watchlist.")

        # LOGGING

        logging = nextcord.Embed(
            title="User added to Watchlist"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="User Added:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['lwl', 'wllist', 'listwl', 'wll', 'showwatchlist'])
    async def listwatchlist(self, ctx):
        """lists all members currently on the watchlist"""
        if not is_dark_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission!")
            return

        nicelist = ""
        for entry in self.watchlist:

            member = ctx.guild.get_member(entry)
            if member is None:
                nicelist = nicelist + f"**{entry}**: {self.watchlist[entry]}\n"
            else:
                nicelist = nicelist + f"**{member}** ({member.id}): {self.watchlist[entry]}\n"

        listembed = nextcord.Embed(
            title="Watchlisted Member List",
            description=nicelist
        )
        await ctx.send(embed=listembed)

    @commands.command(aliases=['rmwl', 'removeuserfromwatchlist', 'wlrmuser', 'wlremoveuser'])
    async def removefromwatchlist(self, ctx, member: nextcord.Member):
        """removes user from moderator watchlist"""
        if not is_dark_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission!")
            return
        if member.id not in self.watchlist:
            await ctx.send(f"{self.sersifail} Member {member} not found on list!")

        self.watchlist.pop(member.id)

        with open(self.filename, "w") as file:
            for entry in self.watchlist:
                file.write(f"{entry};{self.watchlist[entry]}\n")

        await ctx.send(f"{self.sersisuccess} User has been removed from watchlist.")

        # LOGGING

        logging = nextcord.Embed(
            title="User Removed from Watchlist"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="User Removed:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['checkwl', 'ckwl'])
    async def checkwatchlist(self, ctx, member: nextcord.Member):
        if not is_dark_mod(ctx.author):
            await ctx.send(f"{self.sersifail} Insufficient permission!")
            return
        if member.id in self.watchlist:
            await ctx.send(f"{self.sersifail} Member {member} found on watchlist!")
            return True
        else:
            await ctx.send(f"{self.sersisuccess} Member {member} not found on watchlist!")
            return False


def setup(bot):
    bot.add_cog(Watchlist(bot))
