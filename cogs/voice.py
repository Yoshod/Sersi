import nextcord
import requests

from nextcord.ext import commands

from baseutils import ConfirmView
from configutils import get_config, get_config_int
from permutils import permcheck, is_mod
import discordTokens


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
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
            await member.move_to(channel=target, reason=f"Mass move by {interaction.user} ({interaction.user.id})")

        await interaction.message.edit(f"All members in {current.mention} were moved to {target.mention} by {interaction.user.mention}", embed=None, view=None)

        # logging
        embed = nextcord.Embed(
            title="Members mass moved to other VC",
            color=nextcord.Color.from_rgb(237, 91, 6)
        )
        embed.add_field(name="Moderator:", value=interaction.user.mention, inline=False)
        embed.add_field(name="Original channel:", value=current.mention, inline=False)
        embed.add_field(name="Members moved to channel:", value=target.mention, inline=False)
        embed.add_field(name="Members Moved:", value=memberlist, inline=False)

        channel = interaction.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=embed)

    @commands.command(aliases=['mvc', 'movevc', 'vcmove', 'mm'])
    async def massmove(self, ctx, current: nextcord.VoiceChannel, target: nextcord.VoiceChannel):
        """Mass move members from one VC to another.

        both VCs must be referenced to by mention or Channel ID
        """
        if not await permcheck(ctx, is_mod):
            return

        dialog_embed = nextcord.Embed(
            title="Move Members to different voice channel",
            color=nextcord.Color.from_rgb(237, 91, 6))
        dialog_embed.add_field(name='\u200b', value='All members in channel:', inline=False)
        dialog_embed.add_field(name="Source Channel", value=current.mention)
        dialog_embed.add_field(name="Source ID", value=current.id)
        dialog_embed.add_field(name='\u200b', value='will be moved to channel:', inline=False)
        dialog_embed.add_field(name="Destination Channel", value=target.mention)
        dialog_embed.add_field(name="Destination ID", value=target.id)

        await ConfirmView(self.cb_massmove_proceed).send_as_reply(ctx, embed=dialog_embed)

    """@commands.command(aliases=['f'])
    async def forcejoin(self, ctx, channel: nextcord.VoiceChannel):
        if not await permcheck(ctx, is_mod):
            return

        self.unlocked_channels.append(channel)
        await ctx.send(f"{ctx.author.voice}\n\n")
        if ctx.author.voice is not None:    # currently in antother VC
            await ctx.author.move_to(channel=channel, reason="Forcefully joined.")
        else:
            await ctx.send(f"{channel.mention} has been unlocked for you to join.")

        async with ctx.channel.typing():
            await asyncio.sleep(10)  # 10 seconds of time

        if channel in self.unlocked_channels:
            self.unlocked_channels.remove(channel)
            await ctx.send(f"{ctx.author.mention} {channel.mention} is locked again now.")

        # logging
        log_embed = nextcord.Embed(
            title="VC lock overridden",
            description="A Moderator tried to connect to an already full VC and was automatically disconnected.")
        log_embed.add_field(name="Moderator:", value=ctx.author.mention)
        log_embed.add_field(name="Voice Channel:", value=channel.name)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=log_embed)

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
        await channel.send(embed=log_embed)"""

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        def make_embed(message: str):
            embed_obj = {
                'color': 0xED5B06,
                'description': message
            }
            return embed_obj

        if after.channel != before.channel:  # channel change. at least one message has to be sent

            # specifications regardless of message content
            headers = {
                'Authorization': f'Bot {discordTokens.getToken()}',
                'Content-Type': 'application/json; charset=UTF-8'
            }

            if after.channel is not None:
                url = f"https://discord.com/api/v10/channels/{after.channel.id}/messages"
                if before.channel is not None:
                    json = {
                        "embeds": [make_embed(f"Hello {member.mention}, welcome to {after.channel.mention}! Glad you came over from {before.channel.mention}")]
                    }
                else:
                    json = {
                        "embeds": [make_embed(f"Hello {member.mention}, welcome to {after.channel.mention}!")]
                    }
                requests.post(url, headers=headers, json=json)

            if before.channel is not None:
                url = f"https://discord.com/api/v10/channels/{before.channel.id}/messages"
                if after.channel is not None:
                    json = {
                        "embeds": [make_embed(f"{member.mention} ran off to {after.channel.mention}, guess the grass was greener there!")]
                    }
                else:
                    json = {
                        "embeds": [make_embed(f"{member.mention} has left the voice channel. Goodbye!")]
                    }
                requests.post(url, headers=headers, json=json)

        #   -----------------VOICE LOCK-----------------

        """if after.channel is not None:
            if after.channel.user_limit < len(after.channel.members):
                if after.channel.user_limit == 0:   # no limit
                    return

                if after.channel in self.unlocked_channels:     # unlock used; relock channel
                    await member.edit(mute=True)
                    self.unlocked_channels.remove(after.channel)

                    # logging
                    log_embed = nextcord.Embed(
                        title="VC lock circumvented",
                        description="A Moderator joined a VC that was previously locked.")
                    log_embed.add_field(name="Offending Moderator:", value=member.mention)
                    log_embed.add_field(name="Voice Channel:", value=after.channel.name)

                    channel = member.guild.get_channel(get_config_int('CHANNELS', 'logging'))
                    await channel.send(embed=log_embed)

                    channel = member.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
                    await channel.send(embed=log_embed)

                else:
                    await member.move_to(None)
                    await member.send(f"You have been automatically disconnected from {after.channel.name} because it was full. If you want to join the VC **__for moderation purposes only__** you can do that by running the `forcejoin` command.\nInappropiate use of the command will be punished.")

                    # logging
                    log_embed = nextcord.Embed(
                        title="VC lock enforced",
                        description="A Moderator tried to connect to an already full VC and was automatically disconnected.")
                    log_embed.add_field(name="Offending Moderator:", value=member.mention)
                    log_embed.add_field(name="Voice Channel:", value=after.channel.name)

                    channel = member.guild.get_channel(get_config_int('CHANNELS', 'logging'))
                    await channel.send(embed=log_embed)

                    channel = member.guild.get_channel(get_config_int('CHANNELS', 'modlogs'))
                    await channel.send(embed=log_embed)"""


def setup(bot):
    bot.add_cog(Voice(bot))
