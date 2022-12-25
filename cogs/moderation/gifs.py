from nextcord.ext import commands

from configutils import Configuration
from permutils import permcheck, is_mod
from baseutils import SersiEmbed


class Gif(commands.Cog):
    """Autodeleteing blacklisted GIF."""

    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.filename = config.datafiles.gifblacklist
        try:
            with open(self.filename, "x"):  # creates file if not exists
                pass
        except FileExistsError:  # ignores error if it does
            pass
        self.list = self.loadlist()
        self.sersisuccess = config.emotes.success

    def loadlist(self):
        giflist = []
        with open(self.filename, "r") as file:
            for line in file:
                line = line.replace("\n", "")
                giflist.append(line)
        return giflist

    @commands.command()
    async def addgif(self, ctx, url):
        """Add a GIF to the blacklist.

        URL must be provided.
        """
        await ctx.message.delete()
        if not await permcheck(ctx, is_mod):
            return

        with open(self.filename, "a") as file:
            file.write(f"{url}\n")
        self.list = self.loadlist()

        await ctx.send(f"{self.sersisuccess} GIF URL `{url}` added to blacklist.")

        # logging
        embed = SersiEmbed(
            title="GIF added to blacklist",
            fields={"Moderator:": ctx.author.mention, "GIF URL:": url},
            footer="GIF Blacklist",
        )

        channel = ctx.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

    @commands.command()
    async def removegif(self, ctx, url):
        """Remove GIF from blacklist.

        URL must be provided.
        """
        if not await permcheck(ctx, is_mod):
            return

        if url in self.list:
            self.list.remove(url)

        with open(self.filename, "w") as file:
            for gif in self.list:
                file.write(f"{gif}\n")

        await ctx.send(f"{self.sersisuccess} GIF URL `{url}` removed from blacklist.")

        # logging
        embed = SersiEmbed(
            title="GIF removed from blacklist",
            fields={"Moderator:": ctx.author.mention, "GIF URL:": url},
            footer="GIF Blacklist",
        )

        channel = ctx.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

    @commands.command()
    async def listgifs(self, ctx):
        """List GIFs currently blacklisted."""
        if not await permcheck(ctx, is_mod):
            return

        embed = SersiEmbed(
            title="List of GIFs currently being blacklisted",
            description="\n".join(self.list),
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content in self.list:
            await message.delete()

            # logging
            embed = SersiEmbed(
                title="Blacklisted GIF deleted",
                fields={
                    "Message Author:": message.author.mention,
                    "Channel:": message.channel.mention,
                    "Message:": message.content,
                },
            )

            channel = self.bot.get_channel(self.config.channels.logging)
            await channel.send(embed=embed)


def setup(bot, **kwargs):
    bot.add_cog(Gif(bot, kwargs["config"]))
