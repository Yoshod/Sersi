import io
import re
import zipfile

import aiohttp
import nextcord
from nextcord.ext import commands

from utils.perms import is_cet, permcheck


class GetResources(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.message_command(
        name="Get Emojis",
        name_localizations={nextcord.Locale.de: "Emojis Holen"},
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
    )
    async def get_emotes(
        self, interaction: nextcord.Interaction, message: nextcord.Message
    ):
        """https://stackoverflow.com/questions/76070374/how-to-get-emoji-from-message-reference"""
        if not await permcheck(interaction, is_cet):
            return
        await interaction.response.defer(ephemeral=True)

        EMOJI_REGEX: str = (
            r"<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>"
        )
        emojis: list[tuple[str]] = re.findall(EMOJI_REGEX, message.content)

        file_buffer = io.BytesIO()

        with zipfile.ZipFile(
            file_buffer, "w", compression=zipfile.ZIP_DEFLATED
        ) as file:
            for emoji in emojis:
                animated: bool = bool(emoji[0])
                name: str = emoji[1]
                snowflake: str = emoji[2]
                extension: str = "gif" if animated else "png"

                uri: str = f"https://cdn.discordapp.com/emojis/{snowflake}.{extension}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(uri) as response:
                        data: bytes = await response.read()
                        file.writestr(f"{name}.{extension}", data)

            for reaction in message.reactions:
                if not reaction.is_custom_emoji():
                    continue
                if not reaction.emoji.name:
                    continue

                data: bytes = await reaction.emoji.read()
                file.writestr(
                    f"reactions/{reaction.emoji.name}.{'gif' if reaction.emoji.animated else 'png'}",
                    data,
                )

            for sticker in message.stickers:
                async with aiohttp.ClientSession() as session:
                    async with session.get(sticker.url) as response:
                        if response.status != 200:
                            continue

                        file.writestr(
                            f"stickers/{sticker.name}.png", await response.read()
                        )

        file_buffer.seek(0)  # be kind, rewind

        await interaction.followup.send(
            file=nextcord.File(file_buffer, f"emojis_{message.id}.zip")
        )

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
        description="Fetches all image resources of the server and sends them in a ZIP-File",
    )
    async def get_server_resources(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_cet):
            return

        await interaction.response.defer(ephemeral=True)

        file_buffer = io.BytesIO()

        with zipfile.ZipFile(
            file_buffer, "w", compression=zipfile.ZIP_DEFLATED
        ) as file:
            for emote in interaction.guild.emojis:
                data: bytes = await emote.read()

                if emote.animated:
                    file.writestr(f"emotes/{emote.name}.gif", data)
                else:
                    file.writestr(f"emotes/{emote.name}.png", data)

            for sticker in interaction.guild.stickers:
                uri: str = f"https://media.discordapp.net/stickers/{sticker.id}"

                async with aiohttp.ClientSession() as session:
                    async with session.get(uri) as response:
                        if response.status != 200:
                            continue

                        file.writestr(
                            f"stickers/{sticker.name}.png", await response.read()
                        )

            for role in interaction.guild.roles:
                if not role.icon:
                    continue
                try:
                    data: bytes = await role.icon.read()
                except nextcord.NotFound:
                    continue

                file.writestr(f"role_icons/{role.name}.png", data)

        file_buffer.seek(0)  # be kind, rewind

        await interaction.followup.send(
            file=nextcord.File(file_buffer, "resources.zip")
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(GetResources(bot))
