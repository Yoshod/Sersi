import io

import nextcord
from nextcord.ext import commands
from chat_exporter import export


async def make_transcript(
        from_channel: nextcord.TextChannel,
        to_channel: nextcord.TextChannel = None,
        embed: nextcord.Embed = None,
    ) -> str|None:
    """Make a transcript from a channel and send it to another channel if specified."""
    transcript: str = await export(from_channel, military_time=True)

    if transcript is None:
        return None

    transcript_file = nextcord.File(
        io.BytesIO(transcript.encode()),
        filename=f"transcript-{from_channel.name}.html",
    )

    if to_channel is not None:
        await to_channel.send(file=transcript_file, embed=embed)
    
    return transcript


async def get_message_from_url(bot: commands.Bot, url: str):
    *_, guild_id, channel_id, message_id = url.split("/")
    guild = bot.get_guild(int(guild_id))
    channel = guild.get_channel(int(channel_id))
    return await channel.fetch_message(int(message_id))
