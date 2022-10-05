import nextcord
from nextcord.ext import commands

from baseutils import ConfirmView
from configutils import Configuration
from permutils import permcheck, is_slt


class Blacklist(commands.Cog):

    def __init__(self, bot, config: Configuration):
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail
        self.filename = config.datafiles.blacklist
        self.bot = bot
        self.config = config
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

    async def cb_bluser_proceed(self, interaction):
        member_id, reason = 0, ""
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
            if field.name == "Reason":
                reason = field.value

        member = interaction.guild.get_member(member_id)

        with open(self.filename, "a") as file:
            file.write(f"{member.id};{reason}\n")

        self.loadblacklist()
        await interaction.message.edit(f"{self.sersisuccess} User added to blacklist.", embed=None, view=None)

        # LOGGING

        logging = nextcord.Embed(
            title="User added to Blacklist"
        )
        logging.add_field(name="Moderator:", value=interaction.user.mention, inline=False)
        logging.add_field(name="User Added:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=logging)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
        await channel.send(embed=logging)

    @commands.command(aliases=['bl', 'bluser', 'addbl', 'modblacklist'])
    async def blacklistuser(self, ctx, member: nextcord.Member, *, reason=""):
        """Put user onto moderator blacklist."""
        # in case of invocation from s!removemoderator
        if ctx.author == self.bot.user:
            with open(self.filename, "a") as file:
                file.write(f"{member.id};{reason}\n")

            self.loadblacklist()
            return

        if not await permcheck(ctx, is_slt):
            return
        elif member.id in self.blacklist:
            await ctx.reply(f"{self.sersifail} {member} already on blacklist!")
            return
        elif reason == "":
            await ctx.reply(f"{self.sersifail} please provede a reason!")
            return

        dialog_embed = nextcord.Embed(
            title="Add Member to Moderator blacklist",
            description="Following member will be blacklisted from becoming a staff member:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)
        dialog_embed.add_field(name="Reason", value=reason, inline=False)

        await ConfirmView(self.cb_bluser_proceed).send_as_reply(ctx, embed=dialog_embed)

    @commands.command(aliases=['lbl', 'bllist', 'listbl', 'bll', 'showblacklist'])
    async def listblacklist(self, ctx):
        """List all members currently on the blacklist."""
        if not await permcheck(ctx, is_slt):
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

    async def cb_blrmuser_proceed(self, interaction):
        member_id = 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "User ID":
                member_id = int(field.value)
        member = interaction.guild.get_member(member_id)

        self.blacklist.pop(member.id)

        with open(self.filename, "w") as file:
            for entry in self.blacklist:
                file.write(f"{entry};{self.blacklist[entry]}\n")

        await interaction.message.edit(f"{self.sersisuccess} User has been removed from blacklist.", embed=None, view=None)

        # LOGGING

        logging = nextcord.Embed(
            title="User Removed from Blacklist"
        )
        logging.add_field(name="Moderator:", value=interaction.user.mention, inline=False)
        logging.add_field(name="User Removed:", value=member.mention, inline=False)

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=logging)

        channel = interaction.guild.get_channel(self.config.channels.modlogs)
        await channel.send(embed=logging)

    @commands.command(aliases=['rmbl', 'removeuserfromblacklist', 'blrmuser', 'blremoveuser'])
    async def removefromblacklist(self, ctx, member: nextcord.Member):
        """Remove user from moderator blacklist."""
        if not await permcheck(ctx, is_slt):
            return
        if member.id not in self.blacklist:
            await ctx.send(f"{self.sersifail} Member {member} not found on list!")

        dialog_embed = nextcord.Embed(
            title="Remove Member from Moderator blacklist",
            description="Following member will be removed from the blacklist:",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name="User", value=member.mention)
        dialog_embed.add_field(name="User ID", value=member.id)

        await ConfirmView(self.cb_blrmuser_proceed).send_as_reply(ctx, embed=dialog_embed)

    @commands.command(aliases=['checklb', 'ckbl'])
    async def checkblacklist(self, ctx, member: nextcord.Member):
        if not await permcheck(ctx, is_slt):
            return
        if member.id in self.blacklist:
            await ctx.send(f"{self.sersifail} Member {member} found on blacklist!")
            return True
        else:
            await ctx.send(f"{self.sersisuccess} Member {member} not found on blacklist!")
            return False


def setup(bot, **kwargs):
    bot.add_cog(Blacklist(bot, kwargs["config"]))
