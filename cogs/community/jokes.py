import nextcord
import random
from nextcord.ext import commands

from configutils import Configuration
from permutils import is_mod
from webhookutils import send_webhook_message


def generate_uwu(input_text: str) -> str:
    """Shamelessly stolen from https://www.geeksforgeeks.org/uwu-text-convertor-in-python/.
    well, I modified it.
    """

    output_text = ""
    previous_char = "\0"
    # check the cases for every individual character
    for current_char in input_text:
        # change 'L' and 'R' to 'W'
        if current_char in ["L", "R"]:
            output_text += "W"

        # change 'l' and 'r' to 'w'
        elif current_char in ["l", "r"]:
            output_text += "w"

        # if the current character is 'o' or 'O' and the previous one is 'N', 'n', 'M' or 'm'
        elif current_char in ["O", "o"]:
            if previous_char in ["N", "n", "M", "m"]:
                output_text += "yo"
            else:
                output_text += current_char

        # if the current character is 'a' or 'A' and the previous one is 'N', 'n', 'M' or 'm'
        elif current_char in ["A", "a"]:
            if previous_char in ["N", "n", "M", "m"]:
                output_text += "ya"
            else:
                output_text += current_char

        # if no case match, write it as it is
        else:
            output_text += current_char

        previous_char = current_char

    return output_text


class Jokes(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def nevermod(self, ctx: commands.Context, member: nextcord.Member):
        if not is_mod(ctx.author):  # don't replace, it is funny
            await ctx.send(
                "You're not a mod, you should not run this, right? ;)\n\nAnyways let's nevermod **you** instead as a "
                "twist."
            )
            member = ctx.author

        nevermod_role = ctx.guild.get_role(self.config.roles.never_mod)

        await member.add_roles(nevermod_role, reason="nevermod command", atomic=True)
        nevermod_embed = nextcord.Embed(
            title="Never Getting Mod",
            description=f"Oh no! {member.mention} asked for mod in a public channel instead of applying through our "
            f"application form! Now you’re never going to get mod… In fact, we even gave you a nice shiny "
            f"new role just to make sure you know that you {nevermod_role.mention}.",
            colour=nextcord.Color.from_rgb(237, 91, 6),
        )
        await ctx.send(embed=nevermod_embed)

    @commands.command()
    async def uwu(self, ctx: commands.Context, *, message: str = ""):
        """OwO *nuzzles the command*.

        Takes message and uwuifies it.
        """
        if message == "":
            await ctx.send(f"{ctx.author.mention} pwease pwovide a message to uwuify.")
            return

        await ctx.message.delete(delay=None)

        await send_webhook_message(
            channel=ctx.channel,
            content=generate_uwu(message),
            username=generate_uwu(ctx.author.display_name),
            avatar_url=ctx.author.display_avatar.url,
        )

    @commands.command(aliases=["coin", "coinflip"])
    async def flip(self, ctx: commands.Context):
        flip_result = random.randint(1, 2)
        if flip_result == 2:
            await ctx.reply(
                "https://tenor.com/view/heads-coinflip-flip-a-coin-coin-coins-gif-21479854"
            )
        elif flip_result == 1:
            await ctx.reply(
                "https://tenor.com/view/coins-tails-coin-flip-a-coin-coinflip-gif-21479856"
            )

    # events
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:  # ignores message if message is by bot
            return

        if message.guild is None:
            return

        if "admin furry stash" in message.content.lower():
            randomValue = random.randint(1, 10)
            if randomValue == 10:
                embed = nextcord.Embed(
                    title="Admin Furry Stash Rumour",
                    description='The so called "Admin Furry Stash" channel does not exist. It has never existed, '
                    "and never will exist, as there are no furry admins on this server. Please remain "
                    "calm as our specialist anti-disinformation team arrives at your address in order to "
                    "further educate you on this matter.",
                    colour=nextcord.Colour.from_rgb(138, 43, 226),
                )
                await message.channel.send(embed=embed)
                return

        if "literally 1984" in message.content.lower():
            randomValue = random.randint(1, 4)
            if randomValue == 1:
                years = [1419, 1483, 1618, 1812, 1848, 1894, 1942, 1948, 1968, 1989]
                await message.channel.send(
                    f"Oh my god, so true. It literally is like George Orlando's {random.choice(years)}"
                )
                return

        if message.content.lower() == "nya":
            randomValue = random.randint(1, 10)
            if randomValue == 1:
                await message.channel.send(
                    f"Nya... nya? What are you, a fucking weeb {message.author.mention}?"
                )
                return

        if message.content.lower() == "meow":
            randomValue = random.randint(1, 10)
            if randomValue == 1:
                await message.channel.send(
                    f"Meow meow meow, we get it you have a prissy attitude {message.author.mention}, we already noticed."
                )
                return

        if (
            message.type == nextcord.MessageType.reply
            and "is this" in message.content.lower()
            and len(message.mentions) == 1
        ):
            randomValue = random.randint(1, 100)
            if randomValue == 1:
                await message.reply(
                    f"No, this is {message.mentions[0].nick or message.mentions[0].name}."
                )
                return

        if message.author.is_on_mobile():
            randomValue = random.randint(1, 100000)
            if randomValue == 1:
                # let's have it simple _and_ gender neutral. okay?
                await message.reply(
                    "Discord mobile was the greatest mistake in the history of humankind"
                )
            elif randomValue < 4:
                await message.reply("Phone user detected, opinion rejected")


def setup(bot, **kwargs):
    bot.add_cog(Jokes(bot, kwargs["config"]))
