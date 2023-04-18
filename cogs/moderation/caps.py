import nextcord
from nextcord.ext import commands
import re

from baseutils import SersiEmbed
from configutils import Configuration
from permutils import permcheck, is_mod, is_staff
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
        need_replacement: bool = False

        # remove emotes
        msg_string = re.sub(r"(<a?)?:\w+:(\d{18}>)?", "", message.content)

        # remove nums and non-alpanumeric
        new_msg_string = re.sub(r"[\W0-9]", "", msg_string)

        # remove markdown headers
        if not is_staff(message.author):
            cleaned_message: str = ""
            for line in msg_string.splitlines():
                if line.startswith(("# ", "## ", "### ")):
                    need_replacement = True

                    line = line.replace("### ", "")
                    line = line.replace("## ", "")
                    line = line.replace("# ", "")

                cleaned_message += line
            msg_string = cleaned_message

        print("msg_string", msg_string)

        # count uppercase chars
        uppercase = sum(1 for char in new_msg_string if char.isupper())

        if (uppercase / len(new_msg_string)) > 0.7 and len(new_msg_string) > int(
            self.MIN_CHARS_FOR_DETECTION
        ):
            need_replacement = True

        if not need_replacement:
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
        logging_embed: nextcord.Embed = SersiEmbed(
            title="Caps Lock Message replaced",
            description="",
            color=nextcord.Color.from_rgb(237, 91, 6),
            fields={
                "User:": message.author.mention,
                "Channel:": message.channel.mention,
                "Original Message:": message.content,
                "Replacement Message:": msg_string.lower(),
                "Link to Replacement Message:": f"[Jump!]({replacement_message.jump_url})",
            },
            footer="Sersi Caps Removal",
        )
        await channel.send(embed=logging_embed)


def setup(bot, **kwargs):
    bot.add_cog(Caps(bot, kwargs["config"]))
