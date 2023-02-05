import nextcord
from nextcord.ext import commands
import re

from configutils import Configuration
from permutils import permcheck, is_mod
from webhookutils import send_webhook_message


class Caps(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail
        self.bot = bot
        self.config = config
        self.MIN_CHARS_FOR_DETECTION = config.bot.minimum_caps_length

    @commands.command()
    async def setcapslength(self, ctx, number):
        if not await permcheck(ctx, is_mod):
            return

        try:
            value = int(number)
        except ValueError:
            await ctx.send(f"{self.sersifail} {number} is not an integer.")
            return

        if value < 0:
            await ctx.send(f"{self.sersifail} {number} must be greater than **0**.")
            return

        old_val = self.MIN_CHARS_FOR_DETECTION
        self.MIN_CHARS_FOR_DETECTION = value
        self.config.bot.minimum_caps_length = number

        await ctx.send(
            f"{self.sersisuccess} Caps lock detection starts now at messages longer than **{value}**."
        )

        embed = nextcord.Embed(
            title="Minimum Letters For Detection Changed",
            description="The minimum number of letters required for a message to have caps detection has been changed",
            color=nextcord.Color.from_rgb(237, 91, 6),
        )
        embed.add_field(name="Moderator", value=ctx.author.mention)
        embed.add_field(name="Old Value", value=str(old_val))
        embed.add_field(name="New Value", value=str(value))

        channel = ctx.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

    @commands.command()
    async def getcapslength(self, ctx):
        if not await permcheck(ctx, is_mod):
            return

        await ctx.send(
            f"Current caps lock detection starts at messages longer than **{self.MIN_CHARS_FOR_DETECTION}**."
        )

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        msg_string = message.content

        # remove emotes
        new_msg_string = re.sub(r"(<a?)?:\w+:(\d{18}>)?", "", msg_string)

        # remove nums and non-alpanumeric
        new_msg_string = re.sub(r"[\W0-9]", "", new_msg_string)

        if len(new_msg_string) > self.MIN_CHARS_FOR_DETECTION:
            # msg_string = unidecode.unidecode(msg_string)

            uppercase = sum(1 for char in new_msg_string if char.isupper())

            percentage = uppercase / len(new_msg_string)

            if percentage > 0.7:
                # await replace(self, message, message.author, msg_string)
                await message.delete(delay=None)
                # if message.mention_everyone:
                #     return

                replacement_message = await send_webhook_message(
                    channel=message.channel,
                    content=msg_string.lower(),
                    username=message.author.display_name,
                    avatar_url=message.author.display_avatar.url,
                    wait=True,
                )

                channel = self.bot.get_channel(self.config.channels.logging)
                logging_embed = nextcord.Embed(
                    title="Caps Lock Message replaced",
                    description="",
                    color=nextcord.Color.from_rgb(237, 91, 6),
                )
                logging_embed.add_field(
                    name="User:", value=message.author.mention, inline=False
                )
                logging_embed.add_field(
                    name="Channel:", value=message.channel.mention, inline=False
                )
                logging_embed.add_field(
                    name="Original Message:", value=msg_string, inline=False
                )
                logging_embed.add_field(
                    name="Replacement Message:",
                    value=str(msg_string.lower()),
                    inline=False,
                )
                logging_embed.add_field(
                    name="Link to Replacement Message:",
                    value=f"[Jump!]({replacement_message.jump_url})",
                    inline=True,
                )
                await channel.send(embed=logging_embed)


def setup(bot, **kwargs):
    bot.add_cog(Caps(bot, kwargs["config"]))
