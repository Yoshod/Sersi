import random
import math
from dataclasses import asdict

import nextcord
from nextcord.ext import commands

from utils.sersi_embed import SersiEmbed
from utils.base import ignored_message
from utils.config import Configuration
from utils.perms import is_mod
from utils.webhooks import send_webhook_message


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


def calculate_basedness(config: Configuration, member: nextcord.Member):
    if member.id == 809891646606409779:
        return 1.0

    bias = 0.0

    for role in member.roles:
        if role.id in [
            858382469987958804,
            935673319947141230,
            config.roles.honourable_member,
        ]:
            bias += 0.5
        elif role.id in asdict(config.permission_roles).values():
            bias += 0.25
        elif role.id == config.roles.never_mod:
            bias -= 0.5
        elif role.id in config.punishment_roles.values():
            bias -= 1.0
        elif role.id == config.roles.probation:
            bias -= 2.0
        elif role.id == config.roles.reformation:
            return 0.0

    return random.triangular(low=0.0, high=1.0, mode=1 / (1 + math.exp(-bias)))


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
        dm_permission=False, guild_ids=[977377117895536640, 856262303795380224]
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

    @fun.subcommand(description="Determines how based the member is.")
    async def basedcheck(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member = nextcord.SlashOption(
            required=False, description="The member to check if they are based."
        ),
    ):
        await interaction.response.defer(ephemeral=False)

        if member is None:
            member = interaction.user

        based_levels = [
            "not based at all. In fact, they're so not based they're mega cringe",
            "so cringe that my cringe compilation can't contain them",
            "not based",
            "might be based but isn't worth the effort it would take to find out",
            "maybe based and will require second ops centre to be opened",
            "based",
            "mega based",
            "gigachad level of pure **based**",
        ]

        basedness: int = max(
            0,
            min(
                math.floor(
                    calculate_basedness(self.config, member) * len(based_levels)
                ),
                len(based_levels) - 1,
            ),
        )

        based_check_embed = SersiEmbed(
            title="Based Check",
            description="An Emergency task force at the base department convened "
            "in a rush to open a new ops centre in order to determine that "
            f"{member.mention} is {based_levels[basedness]}.",
            footer="Based Check",
        )

        await interaction.followup.send(embed=based_check_embed)

    # compromise: let's have both variants for now -gombik

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
        if ignored_message(self.config, message):
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
