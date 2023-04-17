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

    @nextcord.slash_command(
        name="get_caps_length",
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Shows the currently active caps length",
    )
    async def getcapslength(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.send(
            f"Current caps lock detection starts at messages longer than **{self.MIN_CHARS_FOR_DETECTION}**.",
            ephemeral=True,
        )

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:  # ignores message if message is by bot
            return

        # remove emotes
        msg_string = re.sub(r"(<a?)?:\w+:(\d{18}>)?", "", message.content)

        # remove nums and non-alpanumeric
        new_msg_string = re.sub(r"[\W0-9]", "", msg_string)

        if len(new_msg_string) < int(
            self.MIN_CHARS_FOR_DETECTION
        ):  # should be an int, somehow isn't
            return

        # msg_string = unidecode.unidecode(msg_string)

        uppercase = sum(1 for char in new_msg_string if char.isupper())

        percentage = uppercase / len(new_msg_string)

        if percentage < 0.7:
            return

        await message.delete(delay=None)

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
