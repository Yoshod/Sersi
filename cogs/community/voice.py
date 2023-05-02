import nextcord
import requests

from nextcord.ext import commands

from utils.base import ConfirmView, SersiEmbed
from utils.config import Configuration
from utils.perms import permcheck, is_mod
import discordTokens


class Voice(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = self.config.emotes.success
        self.sersifail = self.config.emotes.fail
        self.unlocked_channels = []

    async def cb_massmove_proceed(self, interaction):
        current_id, target_id = 0, 0
        for field in interaction.message.embeds[0].fields:
            if field.name == "Source ID":
                current_id = int(field.value)
            elif field.name == "Destination ID":
                target_id = int(field.value)
        current = interaction.guild.get_channel(current_id)
        target = interaction.guild.get_channel(target_id)

        memberlist = ""
        for member in current.members:
            memberlist = memberlist + f"**{member.display_name}** ({member.id})\n"
            await member.move_to(
                channel=target,
                reason=f"Mass move by {interaction.user} ({interaction.user.id})",
            )

        await interaction.message.edit(
            f"All members in {current.mention} were moved to {target.mention} by {interaction.user.mention}",
            embed=None,
            view=None,
        )

        # logging
        embed = SersiEmbed(
            title="Members mass moved to other VC",
            color=nextcord.Color.from_rgb(237, 91, 6),
            fields={
                "Moderator:": interaction.user.mention,
                "Original channel:": current.mention,
                "Members moved to channel:": target.mention,
                "Members Moved:": memberlist,
            },
            footer="Voice Cog",
        )

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

    @commands.command(aliases=["mvc", "movevc", "vcmove", "mm"])
    async def massmove(
        self, ctx, current: nextcord.VoiceChannel, target: nextcord.VoiceChannel
    ):
        """Mass move members from one VC to another.

        both VCs must be referenced to by mention or Channel ID
        """
        if not await permcheck(ctx, is_mod):
            return

        dialog_embed = SersiEmbed(
            title="Move Members to different voice channel",
            color=nextcord.Color.from_rgb(237, 91, 6),
            fields={
                "\u200b": "All members in channel:",
                "Source Channel": current.mention,
                "Source ID": current.id,
                "Destination Channel": target.mention,
                "Destination ID": target.id,
            },
            footer="Voice Cog",
        )

        await ConfirmView(self.cb_massmove_proceed).send_as_reply(
            ctx, embed=dialog_embed
        )

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        def make_embed(message: str):
            embed_obj = {"color": 0xED5B06, "description": message}
            return embed_obj

        if (
            after.channel != before.channel
        ):  # channel change. at least one message has to be sent
            # specifications regardless of message content
            headers = {
                "Authorization": f"Bot {discordTokens.getToken()}",
                "Content-Type": "application/json; charset=UTF-8",
            }

            if after.channel is not None:
                url = (
                    f"https://discord.com/api/v10/channels/{after.channel.id}/messages"
                )
                if before.channel is not None:
                    json = {
                        "embeds": [
                            make_embed(
                                f"Hello {member.mention}, welcome to {after.channel.mention}! Glad you came over from {before.channel.mention}"
                            )
                        ]
                    }
                else:
                    json = {
                        "embeds": [
                            make_embed(
                                f"Hello {member.mention}, welcome to {after.channel.mention}!"
                            )
                        ]
                    }
                requests.post(url, headers=headers, json=json)

            if before.channel is not None:
                url = (
                    f"https://discord.com/api/v10/channels/{before.channel.id}/messages"
                )
                if after.channel is not None:
                    json = {
                        "embeds": [
                            make_embed(
                                f"{member.mention} ran off to {after.channel.mention}, guess the grass was greener there!"
                            )
                        ]
                    }
                else:
                    json = {
                        "embeds": [
                            make_embed(
                                f"{member.mention} has left the voice channel. Goodbye!"
                            )
                        ]
                    }
                requests.post(url, headers=headers, json=json)


def setup(bot, **kwargs):
    bot.add_cog(Voice(bot, kwargs["config"]))
