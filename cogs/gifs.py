import nextcord
from nextcord.ext import commands
from baseutils import *


class Gif(commands.Cog):
    """Autodeleteing blacklisted GIFs"""
    def __init__(self, bot):
        self.bot = bot
        self.filename = "gifblacklist.txt"
        try:
            with open(self.filename, 'x'):  # creates file if not exists
                pass
        except FileExistsError:             # ignores error if it does
            pass
        self.list = self.loadlist()

    def loadlist(self):
        giflist = []
        with open(self.filename, 'r') as file:
            for line in file:
                line = line.replace('\n', '')
                giflist.append(line)
        return giflist

    @commands.command()
    async def addgif(self, ctx, url):
        """Adds a GIF to the blacklist

        URL must be provided"""
        if not await permcheck(ctx, is_mod):
            return

        await ctx.message.delete()
        if not await permcheck(ctx, is_mod):
            return

        with open(self.filename, "a") as file:
            file.write(f"{url}\n")
        self.list = self.loadlist()

        # logging
        embed = nextcord.Embed(
            title="GIF added to blacklist",
            color=nextcord.Colour.from_rgb(237, 91, 6))
        embed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        embed.add_field(name="GIF URL:", value=url, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=embed)

    @commands.command()
    async def removegif(self, ctx, url):
        """Removes GIF from blacklist

        URL must be provided"""
        if not await permcheck(ctx, is_mod):
            return

        if url in self.list:
            self.list.remove(url)

        print(f"list before file write {self.list}")

        with open(self.filename, "w") as file:
            for gif in self.list:
                print(f"current GIF {gif}")
                file.write(f"{gif}\n")

        # logging
        embed = nextcord.Embed(
            title="GIF removed from blacklist",
            color=nextcord.Colour.from_rgb(237, 91, 6))
        embed.add_field(name="Moderator:", value=ctx.author.mention, inline=False)
        embed.add_field(name="GIF URL:", value=url, inline=False)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=embed)

    @commands.command()
    async def listgifs(self, ctx):
        """Lists GIFs currently blacklisted"""
        if not await permcheck(ctx, is_mod):
            return

        embed = nextcord.Embed(
            title="List of GIFs currently being blacklisted",
            description="\n".join(self.list),
            colour=nextcord.Color.from_rgb(237, 91, 6))
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content in self.list:
            await message.delete()

            # logging
            embed = nextcord.Embed(
                title="Blacklisted GIF deleted",
                color=nextcord.Colour.from_rgb(237, 91, 6))
            embed.add_field(name="Message Author:", value=message.author.mention, inline=False)
            embed.add_field(name="Channel:", value=message.channel.mention, inline=False)
            embed.add_field(name="Message:", value=message.content, inline=False)

            channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
            await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Gif(bot))
