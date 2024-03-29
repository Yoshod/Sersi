import random
import re
from dataclasses import dataclass

import nextcord
from nextcord.ext import commands

from utils.base import ignored_message
from utils.config import Configuration
from utils.perms import is_mod
from utils.sersi_embed import SersiEmbed
from utils.webhooks import send_webhook_message


@dataclass
class match_regex:
    string: str

    def __eq__(self, other: str | re.Pattern):
        if isinstance(other, str):
            other = re.compile(other)
        assert isinstance(other, re.Pattern)
        return other.fullmatch(self.string) is not None


def chance(success_percentage: int) -> bool:
    """returns true at a success_percentage% chance"""
    percentage: int = random.randint(1, 100)
    return percentage <= success_percentage


def clamp(n: int, min_value: int, max_value: int) -> int:
    """clamps n between min_value and max_value"""
    return max(min(n, max_value), min_value)


def generate_uwu(input_text: str) -> str:
    """Will convert input text into uwuified text.

    Replaces specific characters with their uwu equivalents,
    and inserts "yo" or "ya" after "o" or "a" if the previous
    character is "n", "m", "N", or "M". Returns the uwuified text.

    Shamelessly stolen from https://www.geeksforgeeks.org/uwu-text-convertor-in-python/.
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
        elif current_char in ["O", "o"] and previous_char in ["N", "n", "M", "m"]:
            output_text += "yo"

        # if the current character is 'a' or 'A' and the previous one is 'N', 'n', 'M' or 'm'
        elif current_char in ["A", "a"] and previous_char in ["N", "n", "M", "m"]:
            output_text += "ya"

        # if no case match, write it as it is
        else:
            output_text += current_char

        previous_char = current_char

    return output_text


class Jokes(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        """Cog that provides fun commands and events.

        Args:
            bot (commands.Bot): The bot instance.
            config (Configuration): The bot configuration object.

        """

        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def fun(self, interaction: nextcord.Interaction):
        pass

    @fun.subcommand(
        description="Makes absolutely 100% sure that the member will not become mod anytime in the future."
    )
    async def nevermod(
        self, interaction: nextcord.Interaction, member: nextcord.Member
    ):
        if not is_mod(interaction.user):
            self_nevermod = True
        else:
            self_nevermod = False

        await interaction.response.defer(ephemeral=False)

        nevermod_role = interaction.guild.get_role(self.config.roles.never_mod)

        if self_nevermod:
            await interaction.user.add_roles(
                nevermod_role, reason="nevermod command", atomic=True
            )
            nevermod_embed = SersiEmbed(
                title="Self Nevermodded!",
                description=f"Member {interaction.user.mention} ({interaction.user.id})"
                " thought they were being funny by running the nevermod command!"
                "Now they themselves have been nevermodded for their sins.",
                footer="Nevermod",
            )

        else:
            await member.add_roles(
                nevermod_role, reason="nevermod command", atomic=True
            )
            nevermod_embed = SersiEmbed(
                title="Never Getting Mod",
                description=f"Oh no! {member.mention} asked for mod in a public channel instead of applying through our "
                "application form! Now you’re never going to get mod… In fact, we even gave you a nice shiny "
                f"new role just to make sure you know that you {nevermod_role.mention}.",
                footer="Nevermod",
            )
        await interaction.followup.send(embed=nevermod_embed)

    @fun.subcommand(description="UwUifies the message.")
    async def uwuify(
        self,
        interaction: nextcord.Interaction,
        message: str = nextcord.SlashOption(
            required=True, description="The message to uwuify."
        ),
    ):
        await interaction.response.defer(ephemeral=True)

        if not isinstance(interaction.channel, nextcord.TextChannel):
            await interaction.followup.send(
                generate_uwu(
                    "Oh no! Turns out this command cannot be run in Voice Channels or Threads :("
                ),
                ephemeral=True,
            )
            return

        await send_webhook_message(
            channel=interaction.channel,
            content=generate_uwu(message),
            username=generate_uwu(interaction.user.display_name),
            avatar_url=interaction.user.display_avatar.url,
        )

        await interaction.followup.send("done :3", ephemeral=True)

    @fun.subcommand(description="Flips a coin.")
    async def coinflip(self, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=False)

        flip_result = random.randint(1, 2)
        if flip_result == 2:
            await interaction.followup.send(
                "https://tenor.com/view/heads-coinflip-flip-a-coin-coin-coins-gif-21479854",
                ephemeral=False,
            )
        elif flip_result == 1:
            await interaction.followup.send(
                "https://tenor.com/view/coins-tails-coin-flip-a-coin-coinflip-gif-21479856",
                ephemeral=False,
            )

    @fun.subcommand(
        description="Rolls given number of dice, with given number of sides."
    )
    async def roll(
        self,
        interaction: nextcord.Interaction,
        dice: int = nextcord.SlashOption(
            required=False,
            default=1,
            min_value=1,
            max_value=10,
            description="The number of dice to roll.",
        ),
        sides: int = nextcord.SlashOption(
            required=False,
            default=6,
            choices=[2, 4, 6, 8, 10, 12, 20],
            description="The number of sides on each die.",
        ),
        advantage: bool = nextcord.SlashOption(
            required=False,
            default=False,
            choices={"yes": True, "no": False},
            description="Whether to roll with advantage.",
        ),
        disadvantage: bool = nextcord.SlashOption(
            required=False,
            default=False,
            choices={"yes": True, "no": False},
            description="Whether to roll with disadvantage.",
        ),
        base: int = nextcord.SlashOption(
            required=False, default=0, description="The base number to add to the roll."
        ),
        advanced: bool = nextcord.SlashOption(
            required=False,
            default=False,
            choices={"yes": True, "no": False},
            description="Whether to show information about each dice.",
        ),
    ):
        await interaction.response.defer(ephemeral=False)

        # roll all dice, sort them
        roll = sorted(
            [
                random.randint(1, sides)
                for _ in range(dice + int(advantage) + int(disadvantage))
            ]
        )

        roll_result = base + sum(roll[int(advantage) : dice + int(advantage)])

        extra = []
        if advantage:
            extra.append(" with advantage")
        if disadvantage:
            extra.append(" with disadvantage")

        dice_info = f"{dice}d{sides}{f' + {base}' if base else ''}"
        if extra:
            dice_info += " and".join(extra)

        if not advanced:
            await interaction.followup.send(
                f"You rolled **{roll_result}**! *({dice_info})*", ephemeral=False
            )
            return

        await interaction.followup.send(
            f"You rolled {dice_info}"
            f"```{f' #{roll[0]}# | ' if advantage else ''}"
            f"{' | '.join(str(n) for n in roll[int(advantage) : dice+int(advantage)])}"
            f"{f' | #{roll[-1]}# ' if disadvantage else ''}```"
            f"You rolled **{roll_result}**!",
            ephemeral=False,
        )

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

    # events
    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
            return

        if self.config.bot.dev_mode or chance(clamp(len(message.content), 10, 25)):
            match match_regex(message.content.lower()):
                case r".*admin furry stash.*":
                    await message.channel.send(
                        embed=SersiEmbed(
                            title="Admin Furry Stash Rumour",
                            description='The so called "Admin Furry Stash" channel does not exist. It has never "'
                            "existed, and never will exist, as there are no furry admins on this server. Please remain "
                            "calm as our specialist anti-disinformation team arrives at your address in order to "
                            "further educate you on this matter.",
                            footer="Sersi Anti Rumour Aktion",
                        )
                    )

                case r".*literally 1984.*":
                    years: list[int] = [
                        1483,
                        1848,
                        1894,
                        1942,
                        1948,
                        1968,
                        1989,
                    ]
                    await message.channel.send(
                        f"Oh my god, so true. It literally is like George Orlando's {random.choice(years)}"
                    )

                case r"(nya+ ?)+":
                    await message.channel.send(
                        f"Nya... nya? What are you, a fucking weeb {message.author.mention}?"
                    )

                case r"(meow ?)+":
                    await message.channel.send(
                        f"Meow meow meow, we get it you have a prissy attitude {message.author.mention}, we already noticed."
                    )

                case r"(mrow ?)+":
                    await message.channel.send(
                        f"Mrow? You're feeling particularly wild right now, do you? {message.author.mention}"
                    )

                case r"(woo+f ?)+":
                    await message.channel.send(
                        f"Who's a good dog? You are! {message.author.mention}"
                    )

                case r"(bark ?)+":
                    await message.channel.send(
                        f"What are you barking about? Do you need a muzzle {message.author.mention}?"
                    )

                case r"(wuff ?)+":
                    await message.channel.send(
                        f"Feeling particularly wild right now, are you {message.author.mention}?"
                    )

                case r"awoo+|grr+":
                    await message.channel.send(
                        f'{message.author.mention} is a degenerate furry. How do I know? They just said "{message.content}".'
                    )

                case r".*g(o|ö)mb(o|ö)c.*":
                    gombik = message.guild.get_member(264502855602274306)
                    await gombik.edit(nick="Gömböc")
                    await message.channel.send(gombik.mention, delete_after=1)


        # don't know what to do with this -mel
        # maybe we could rebalance the chances? -gombik
        if message.author.is_on_mobile():
            randomValue = random.randint(1, 100000)
            if randomValue == 1:
                # let's have it simple _and_ gender-neutral. okay?
                await message.reply(
                    "Discord mobile was the greatest mistake in the history of humankind"
                )
            elif randomValue < 4:
                await message.reply("Phone user detected, opinion rejected")


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Jokes(bot, kwargs["config"]))
