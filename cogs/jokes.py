import nextcord
import random
from nextcord.ext import commands
from baseutils import *


class Jokes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def nevermod(self, ctx, member: nextcord.Member):
        if not is_mod(ctx.author):
            await ctx.send(f"You're not a mod, you should not run this, right? ;)\n\nAnyways let's nevermod **you** instead as a twist.")
            member = ctx.author

        nevermod_role = ctx.guild.get_role(get_config_int('ROLES', 'nevermod'))

        await member.add_roles(nevermod_role, reason="nevermod command", atomic=True)
        nevermod_embed = nextcord.Embed(
            title="Never Getting Mod",
            description=f"Oh no! {member.mention} asked for mod in a public channel instead of applying through our application form! Now you’re never going to get mod… In fact, we even gave you a nice shiny new role just to make sure you know that you {nevermod_role.mention}.",
            colour=nextcord.Color.from_rgb(237, 91, 6))
        await ctx.send(embed=nevermod_embed)

    # events
    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:  # ignores message if message is by bot
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
