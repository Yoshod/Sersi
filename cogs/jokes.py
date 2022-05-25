import nextcord
import random
from nextcord.ext import commands


class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # events
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author == self.bot.user:  # ignores message if message is by bot
            return

        elif "pythonic" in str(message.content):
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                await message.channel.send("Is your code even pep8 compliant bro?\nNo? It's not?\nAnd you have the gall to call yourself a programmer. Go read the contents of the pep8 style guide cover to cover you heathen.")
            else:
                return

        elif str(message.content) == "literally 1984" or str(message.content) == "Literally 1984":
            randomValue = random.randint(1, 10)
            if randomValue >= 9:
                await message.channel.send("Oh my god, so true. It literally is like George Orlando's 1812")
            else:
                return

        elif str(message.content) == "nya" or str(message.content) == "Nya":
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                await message.channel.send(f"Nyah... nyah? What are you, a fucking weeb {message.author.mention}?")
            else:
                return

        elif str(message.content) == "meow" or str(message.content) == "Meow":
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                await message.channel.send(f"Meow meow meow, we get it you have a prissy attitude {message.author.mention}, we already noticed.")
            else:
                return


def setup(bot):
    bot.add_cog(Jokes(bot))
