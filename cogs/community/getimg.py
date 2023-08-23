import zipfile

import nextcord
import requests
from nextcord.ext import commands

from utils.perms import is_cet, permcheck


class GetResources(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(
        dm_permission=False, guild_ids=[977377117895536640, 856262303795380224]
    )
    async def get_server_resources(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_cet):
            return

        await interaction.response.defer(ephemeral=False)

        with zipfile.ZipFile("resources.zip", "w") as file:

            for emote in interaction.guild.emojis:
                data: bytes = await emote.read()
                file.writestr(f"emotes/{emote.name}.webp", data)

            for sticker in interaction.guild.stickers:
                uri: str = f"https://media.discordapp.net/stickers/{sticker.id}.webp"

                response = requests.get(uri)

                if response.status_code != 200:
                    continue

                file.writestr(f"stickers/{sticker.name}.webp", response.content)

            for role in interaction.guild.roles:
                if not role.icon:
                    continue
                try:
                    data: bytes = await role.icon.read()
                except nextcord.NotFound:
                    continue

                file.writestr(f"role_icons/{role.name}.png", data)

        with open("resources.zip", "rb") as file:
            await interaction.followup.send(file=nextcord.File(file))


def setup(bot, **kwargs):
    bot.add_cog(GetResources(bot))
