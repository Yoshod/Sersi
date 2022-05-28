import nextcord

from nextcord.ext import commands
from baseutils import *


class Blacklist(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.blacklist = {}
        self.loadblacklist()

    def loadblacklist(self):
        with open("blacklist.txt", "r") as file:
            for line in file:
                line = line.replace('\n', '')
                [user_id, reason] = line.split(";", maxsplit=1)
                self.blacklist[int(user_id)] = reason           # if the key is not an int, the guild.get_member() won't work

    @commands.command(aliases=['bl', 'bluser', 'addbl', 'modblacklist'])
    async def blacklistuser(self, ctx, member: nextcord.Member, *reason):
        """sets user onto moderator blacklist"""
        if not isDarkMod(ctx.author.roles):
            await ctx.send(f"<:sersifail:979070135799279698> Insufficient permission!")
            return
        elif member.id in self.blacklist:
            await ctx.send(f"<:sersifail:979070135799279698> {member} already on list!")
            return

        reason_string = " ".join(reason)
        # self.blacklist[member.id] = reason

        with open("blacklist.txt", "a") as file:
            file.write(f"{member.id};{reason_string}\n")

        self.loadblacklist()
        await ctx.send("<:sersisuccess:979066662856822844> User added to blacklist.")

        # LOGGING
        channel = ctx.guild.get_channel(getLoggingChannel(ctx.guild.id))
        logging = nextcord.Embed(
            title="User added to Blacklist"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="User Added:", value=member.mention, inline=False)
        await channel.send(embed=logging)

    @commands.command(aliases=['lbl', 'bllist', 'listbl', 'bll', 'showblacklist'])
    async def listblacklist(self, ctx):
        """lists all members currently on the blacklist"""
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
        if not isDarkMod(ctx.author.roles):
            await ctx.send(f"<:sersifail:979070135799279698> Insufficient permission!")
            return
        if member.id not in self.blacklist:
            await ctx.send(f"<:sersifail:979070135799279698> Member {member} not found on list!")

        self.blacklist.pop(member.id)

        with open("blacklist.txt", "w") as file:
            for entry in self.blacklist:
                file.write(f"{entry};{self.blacklist[entry]}\n")

        await ctx.send("<:sersisuccess:979066662856822844> User has been removed from blacklist.")

        # LOGGING
        channel = ctx.guild.get_channel(getLoggingChannel(ctx.guild.id))
        logging = nextcord.Embed(
            title="User Removed from Blacklist"
        )
        logging.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        logging.add_field(name="User Removed:", value=member.mention, inline=False)
        await channel.send(embed=logging)

    @commands.command(aliases=['checklb', 'ckbl'])
    async def checkblacklist(self, ctx, member: nextcord.Member):
        if not isDarkMod(ctx.author.roles):
            await ctx.send(f"<:sersifail:979070135799279698> Insufficient permission!")
            return
        if member.id in self.blacklist:
            await ctx.send(f"<:sersifail:979070135799279698> Member {member} found on blacklist!")
            return True
        else:
            await ctx.send(f"<:sersisuccess:979066662856822844> Member {member} not found on blacklist!")
            return False


def setup(bot):
    bot.add_cog(Blacklist(bot))
