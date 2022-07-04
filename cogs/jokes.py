import nextcord
import random
from nextcord.ext import commands

from configutils import get_config_int
from permutils import is_mod
from webhookutils import send_webhook_message


class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def generate_uwu(input_text: str) -> str:
        """Shamelessly stolen from https://www.geeksforgeeks.org/uwu-text-convertor-in-python/
        well, i modified it"""

        output_text = ''
        previous_char = '\0'
        # check the cases for every individual character
        for current_char in input_text:

            # change 'L' and 'R' to 'W'
            if current_char in ['L', 'R']:
                output_text += 'W'

            # change 'l' and 'r' to 'w'
            elif current_char in ['l', 'r']:
                output_text += 'w'

            # if the current character is 'o' or 'O'and the previous one is 'N', 'n', 'M' or 'm'
            elif current_char in ['O', 'o']:
                if previous_char in ['N', 'n', 'M', 'm']:
                    output_text += 'yo'
                else:
                    output_text += current_char

            # if the current character is 'a' or 'A'and the previous one is 'N', 'n', 'M' or 'm'
            elif current_char in ['A', 'a']:
                if previous_char in ['N', 'n', 'M', 'm']:
                    output_text += 'ya'
                else:
                    output_text += current_char

            # if no case match, write it as it is
            else:
                output_text += current_char

            previous_char = current_char

        return output_text

    @commands.command()
    async def nevermod(self, ctx, member: nextcord.Member):
        if not is_mod(ctx.author):      # don't replace, it is funny
            await ctx.send(f"You're not a mod, you should not run this, right? ;)\n\nAnyways let's nevermod **you** instead as a twist.")
            member = ctx.author

        nevermod_role = ctx.guild.get_role(get_config_int('ROLES', 'nevermod'))

        await member.add_roles(nevermod_role, reason="nevermod command", atomic=True)
        nevermod_embed = nextcord.Embed(
            title="Never Getting Mod",
            description=f"Oh no! {member.mention} asked for mod in a public channel instead of applying through our application form! Now you’re never going to get mod… In fact, we even gave you a nice shiny new role just to make sure you know that you {nevermod_role.mention}.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        await ctx.send(embed=nevermod_embed)

    @commands.command()
    async def uwu(self, ctx, *, message=""):
        """OwO *nuzzles the command*

        Takes message and uwuifies it."""
        if message == "":
            await ctx.send(f"{ctx.author.mention} pwease pwovide a message to uwuify.")
            return

        await ctx.message.delete(delay=None)

        await send_webhook_message(ctx.channel, content=self.generate_uwu(message), username=self.generate_uwu(ctx.author.display_name), avatar_url=ctx.author.display_avatar.url)

    @commands.command(aliases=["coin", "coinflip"])
    async def flip(self, ctx):
        flip_result = random.randint(1, 2)
        if flip_result == 2:
            await ctx.reply("https://tenor.com/view/heads-coinflip-flip-a-coin-coin-coins-gif-21479854")
        elif flip_result == 1:
            await ctx.reply("https://tenor.com/view/coins-tails-coin-flip-a-coin-coinflip-gif-21479856")

    # events
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:  # ignores message if message is by bot
            return

        if message.guild is None:
            return

        elif "pythonic" in message.content.lower():
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                await message.channel.send("Is your code even pep8 compliant bro?\nNo? It's not?\nAnd you have the gall to call yourself a programmer. Go read the contents of the pep8 style guide cover to cover you heathen.")
            else:
                return

        elif "admin furry stash" in message.content.lower():
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                embed = nextcord.Embed(
                    title="Admin Furry Stash Rumour",
                    description="The so called \"Admin Furry Stash\" channel does not exist. It has never existed, and never will exist, as there are no furry admins on this server. Please remain calm as our specialist anti-disinformation team arrives at your address in order to further educate you on this matter.",
                    colour=nextcord.Colour.from_rgb(138, 43, 226)
                )
                await message.channel.send(embed=embed)
            else:
                return

        elif "question of life the universe and everything" in message.content.lower().replace(",", "") or "ultimate question" in message.content.lower():
            randomValue = random.randint(1, 5)
            if randomValue == 1:
                await message.channel.send("The answer is ||42||")
            else:
                return

        elif message.content.lower() == "literally 1984":
            randomValue = random.randint(1, 10)
            if randomValue >= 9:
                await message.channel.send("Oh my god, so true. It literally is like George Orlando's 1812")
            else:
                return

        elif message.content.lower() == "nya":
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                await message.channel.send(f"Nya... nya? What are you, a fucking weeb {message.author.mention}?")
            else:
                return

        elif message.content.lower() == "meow":
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                await message.channel.send(f"Meow meow meow, we get it you have a prissy attitude {message.author.mention}, we already noticed.")
            else:
                return

        elif ("it's coming home" in message.content.lower() or "it will come home" in message.content.lower()) and message.author.id == 362340623992356864:
            await message.reply("No it won't be coming home Solar, and it likely never will in the future.")

        elif message.author.is_on_mobile():
            randomValue = random.randint(1, 100000)
            if randomValue == 1:
                await message.reply("Discord mobile was the greatest mistake in the history of mankind")
            elif randomValue in [2, 3, 4, 5]:
                await message.reply("Phone user detected, opinion rejected")


def setup(bot):
    bot.add_cog(Jokes(bot))
