import nextcord
from nextcord.ext import commands
from configutils import get_config_int
from permutils import *


class Blacklist(commands.Cog):

    def __init__(self, bot):
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.filename = "blacklist.csv"
        self.bot = bot
        self.blacklist = {}
        try:
            with open(self.filename, 'x'):  # creates CSV file if not exists
                pass
        except FileExistsError:             # ignores error if it does
            pass
        self.loadblacklist()

    def loadblacklist(self):
        with open(self.filename, "r") as file:
            for line in file:
                line = line.replace('\n', '')
                [user_id, reason] = line.split(";", maxsplit=1)
                self.blacklist[int(user_id)] = reason           # if the key is not an int, the guild.get_member() won't work

    @commands.command(aliases=['bl', 'bluser', 'addbl', 'modblacklist'])
    async def blacklistuser(self, ctx, member: nextcord.Member, *, reason):
        """sets user onto moderator blacklist"""
        if not await permcheck(ctx, is_dark_mod):
            return
        elif member.id in self.blacklist:
            await ctx.send(f"{self.sersifail} {member} already on blacklist!")
            return

        with open(self.filename, "a") as file:
            file.write(f"{member.id};{reason}\n")

        self.loadblacklist()
        await ctx.send(f"{self.sersisuccess} User added to blacklist.")

        # LOGGING

        logging = nextcord.Embed(
            title="User added to Blacklist"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="User Added:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['lbl', 'bllist', 'listbl', 'bll', 'showblacklist'])
    async def listblacklist(self, ctx):
        """lists all members currently on the blacklist"""
        if not await permcheck(ctx, is_dark_mod):
            return

        nicelist = ""
        for entry in self.blacklist:

            member = ctx.guild.get_member(entry)
            if member is None:
                nicelist = nicelist + f"**{entry}**: {self.blacklist[entry]}\n"
            else:
                nicelist = nicelist + f"**{member}** ({member.id}): {self.blacklist[entry]}\n"

        listembed = nextcord.Embed(
            title="Blacklisted Member List",
            description=nicelist
        )
        await ctx.send(embed=listembed)

    @commands.command(aliases=['rmbl', 'removeuserfromblacklist', 'blrmuser', 'blremoveuser'])
    async def removefromblacklist(self, ctx, member: nextcord.Member):
        """removes user from moderator blacklist"""
        if not await permcheck(ctx, is_dark_mod):
            return
        if member.id not in self.blacklist:
            await ctx.send(f"{self.sersifail} Member {member} not found on list!")

        self.blacklist.pop(member.id)

        with open(self.filename, "w") as file:
            for entry in self.blacklist:
                file.write(f"{entry};{self.blacklist[entry]}\n")

        await ctx.send(f"{self.sersisuccess} User has been removed from blacklist.")

        # LOGGING

        logging = nextcord.Embed(
            title="User Removed from Blacklist"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="User Removed:", value=member.mention, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=logging)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=logging)

    @commands.command(aliases=['checklb', 'ckbl'])
    async def checkblacklist(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_dark_mod):
            return
        if member.id in self.blacklist:
            await ctx.send(f"{self.sersifail} Member {member} found on blacklist!")
            return True
        else:
            await ctx.send(f"{self.sersisuccess} Member {member} not found on blacklist!")
            return False


def setup(bot):
    bot.add_cog(Blacklist(bot))
