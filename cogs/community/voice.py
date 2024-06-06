import nextcord
import mutagen
import os
import time
import datetime
from pydub import AudioSegment
from nextcord.ext import commands
from openai import OpenAI
import discordTokens

from utils.config import Configuration
from utils.perms import permcheck, is_staff
from utils.sersi_embed import SersiEmbed
from utils.database import db_session, VoiceMessageAnalytics


PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)


class Voice(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = self.config.emotes.success
        self.sersifail = self.config.emotes.fail

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Voice commands.",
    )
    async def voice(self, interaction: nextcord.Interaction):
        pass

    @voice.subcommand(
        description="Mass move members from one VC to another.",
    )
    async def mass_move(
        self,
        interaction: nextcord.Interaction,
        current: nextcord.VoiceChannel,
        target: nextcord.VoiceChannel,
    ):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        memberlist = ""
        for member in current.members:
            memberlist = memberlist + f"**{member.display_name}** ({member.id})\n"
            await member.move_to(
                channel=target,
                reason=f"Mass move by {interaction.user} ({interaction.user.id})",
            )

        await interaction.followup.send(
            f"All members in {current.mention} were moved to {target.mention}",
            ephemeral=True,
        )

        # logging

        embed = SersiEmbed(
            title="Members mass moved to other VC",
            description="All members in channel were moved to another VC",
            fields=[
                {
                    "Move done by:": interaction.user.mention,
                    "From channel:": current.mention,
                    "To channel:": target.mention,
                },
                {
                    "Members Moved:": memberlist,
                },
            ],
            footer="Voice Cog",
            footer_icon=interaction.user.avatar.url,
        )

        channel = interaction.guild.get_channel(self.config.channels.log.general)
        await channel.send(embed=embed)

    @voice.subcommand(
        description="Get number of voice messages sent today.",
    )
    async def voice_messages(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        today = datetime.datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        with db_session(interaction.user) as session:
            voice_messages_today = (
                session.query(VoiceMessageAnalytics)
                .filter(
                    VoiceMessageAnalytics.timestamp == today,
                )
                .count()
            )

        await interaction.followup.send(
            f"Number of voice messages sent today: {voice_messages_today}",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: nextcord.Member,
        before: nextcord.VoiceState,
        after: nextcord.VoiceState,
    ):
        if after.channel != before.channel:
            # channel change. at least one message has to be sent
            # specifications regardless of message content

            if after.channel is not None:
                embed = SersiEmbed(
                    description=(
                        f"Hello {member.mention}, welcome to {after.channel.mention}!"
                        if before.channel is None
                        else f"Hello {member.mention}, welcome to {after.channel.mention}! Glad you came over from {before.channel.mention}"
                    ),
                    footer=member.display_name,
                    footer_icon=member.avatar.url,
                )
                await after.channel.send(embed=embed)

            if before.channel is not None:
                embed = SersiEmbed(
                    description=(
                        f"{member.mention} has left the voice channel. Goodbye!"
                        if after.channel is None
                        else f"{member.mention} ran off to {after.channel.mention}, guess the grass was greener there!"
                    ),
                    footer=member.display_name,
                    footer_icon=member.avatar.url,
                )
                await before.channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.author.bot:
            return

        if not message.attachments:
            return

        if (
            message.attachments[0].content_type.startswith("audio")
            and message.attachments[0].filename == "voice-message.ogg"
        ):
            filename = f"voice-message-{message.author.id}-{time.time()}.ogg"

            await message.attachments[0].save(f"files/TempAudio/{filename}")

            try:
                ogg_file = AudioSegment.from_ogg(
                    f"{GRANDPARENT_DIR}/files/TempAudio/{filename}"
                )

                ogg_file.export(
                    f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav",
                    format="wav",
                )

                os.remove(f"{GRANDPARENT_DIR}/files/TempAudio/{filename}")

                audio_file = mutagen.File(
                    f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav"
                )

                duration = audio_file.info.length
                filesize = os.path.getsize(
                    f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav"
                )

            except mutagen.MutagenError:
                pass

            with db_session(message.author) as session:
                # get a count of the number of voice messages sent today by any user
                today = datetime.datetime.today()
                today = today.replace(hour=0, minute=0, second=0, microsecond=0)

                voice_messages_today = (
                    session.query(VoiceMessageAnalytics)
                    .filter(
                        VoiceMessageAnalytics.timestamp == today,
                    )
                    .count()
                )

                if voice_messages_today > 119:
                    await message.reply(
                        "Sorry, the voice message limit has been reached for today. Please try again tomorrow.",
                        delete_after=5,
                    )

                    await message.delete()

                    return

                else:
                    session.add(
                        VoiceMessageAnalytics(
                            message_id=message.id,
                            author=message.author.id,
                            channel=message.channel.id,
                            link=message.jump_url,
                            duration=duration,
                            filesize=filesize,
                        )
                    )

                    session.commit()

            if duration > 60 or filesize > 25000000:
                os.remove(f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav")
                await message.reply(
                    f"This voice message is too long or too large to be processed. It is {duration} seconds long and {filesize} bytes in size.",
                    delete_after=5,
                )

                await message.delete()

                return

            client = OpenAI(api_key=discordTokens.getOpenAIApiKey())

            with open(
                f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav", "rb"
            ) as file:

                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=file,
                )

            if transcription.text == "":
                await message.reply(
                    "No transcription could be made from this audio. The Moderation Team has been notified. If this has been done intentionally, please refrain from doing so in the future. Future violations will result in being unable to send voice messages."
                )

                os.remove(f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav")
                return

            message.content = transcription.text
            self.bot.dispatch("message", message)

            await message.reply(f"**Transcription:**\n{transcription.text}")

            os.remove(f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav")


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Voice(bot, kwargs["config"]))
