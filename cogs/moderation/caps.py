import nextcord
from nextcord.ext import commands
import re

from utils.sersi_embed import SersiEmbed
from utils.base import ignored_message
from utils.config import Configuration
from utils.perms import permcheck, is_mod, is_staff
from utils.webhooks import send_webhook_message


class Caps(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail
        self.bot = bot
        self.config = config
        self.MIN_CHARS_FOR_DETECTION = config.bot.minimum_caps_length

    @nextcord.slash_command(
        name="get_caps_length",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
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
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
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
                if line.startswith(
                    (
                        "# ",
                        "## ",
                        "### ",
                        "* # ",
                        "* ## ",
                        "* ### ",
                        "> # ",
                        "> ## ",
                        "> ### ",
                        ">>> # ",
                        ">>> ## ",
                        ">>> ### ",
                    )
                ):
                    need_replacement = True

                    line = line.replace("### ", "")
                    line = line.replace("## ", "")
                    line = line.replace("# ", "")

                cleaned_message += f"{line}\n"
            msg_string = cleaned_message

        # count uppercase chars
        uppercase = sum(1 for char in new_msg_string if char.isupper())

        if (
            len(new_msg_string) > int(self.MIN_CHARS_FOR_DETECTION)
            and uppercase / len(new_msg_string)
        ) > 0.7:
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

        await self.bot.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Caps Lock Message replaced",
                description="",
                color=nextcord.Color.from_rgb(237, 91, 6),
                fields={
                    "User:": message.author.mention,
                    "Channel:": message.channel.mention,
                    "Original Message:": message.content,
                    "Replacement Message:": msg_string.lower(),
                    "Link to Replacement Message:": f"{replacement_message.jump_url}",
                },
                footer="Sersi Caps Removal",
            )
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Caps(bot, kwargs["config"]))
