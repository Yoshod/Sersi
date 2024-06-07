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
from utils.perms import permcheck, is_staff, blacklist_check
from utils.sersi_embed import SersiEmbed
from utils.database import db_session, VoiceMessageAnalytics


PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)


def check_if_voice_message_eligible(message: nextcord.Message, config: Configuration):
    if blacklist_check(message.author, "Voice Message"):
        return (
            False,
            f"{config.emotes.fail} You are blacklisted from sending voice messages. Please open a Moderation Lead Ticket if you believe this is a mistake.",
        )

    with db_session(message.author) as session:
        today = datetime.datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        voice_messages_today = session.query(VoiceMessageAnalytics).filter(
            VoiceMessageAnalytics.timestamp == today,
        )

    author_voice_messages_seconds = 0
    global_voice_messages_seconds = 0

    for voice_message in voice_messages_today:
        if voice_message.author == message.author.id:
            author_voice_messages_seconds += voice_message.duration

        global_voice_messages_seconds += voice_message.duration

    if author_voice_messages_seconds >= 300:
        reason = (
            f"{config.emotes.fail} You have reached the maximum voice message allowance for today. Please try again tomorrow.",
        )
        return False, reason

    if global_voice_messages_seconds >= 3000:
        reason = (
            f"{config.emotes.fail} The server has reached the maximum voice message allowance for today. Please try again tomorrow.",
        )
        return False, reason

    return True, None


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

        channel = interaction.guild.get_channel(self.config.channels.logging)
        await channel.send(embed=embed)

    @voice.subcommand(
        description="Get the minutes and cost of voice messages sent today.",
    )
    async def voice_messages(self, interaction: nextcord.Interaction):
        if not await permcheck(interaction, is_staff):
            return

        await interaction.response.defer(ephemeral=True)

        today = datetime.datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        with db_session(interaction.user) as session:
            voice_messages_today = session.query(VoiceMessageAnalytics).filter(
                VoiceMessageAnalytics.timestamp == today,
            )

        global_voice_messages_seconds = 0
        for voice_message in voice_messages_today:
            global_voice_messages_seconds += voice_message.duration

        global_voice_messages_minutes = global_voice_messages_seconds / 60
        global_voice_messages_cost = global_voice_messages_minutes * 0.006

        await interaction.followup.send(
            embed=SersiEmbed(
                title="Voice Messages Today",
                description=f"Today, {global_voice_messages_minutes} minutes ({global_voice_messages_seconds} seconds) of voice messages have been sent. This costs ${global_voice_messages_cost}.",
            ),
            ephemeral=True,
        )

    @voice.subcommand(
        description="Get the minutes and cost of voice messages sent today by a specific user.",
    )
    async def user_voice_messages(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="Member to view the usage of",
            required=False,
        ),
    ):
        if user is None:
            user = interaction.user
            if not await permcheck(interaction, is_staff):
                return

        await interaction.response.defer(ephemeral=True)

        today = datetime.datetime.today()
        today = today.replace(hour=0, minute=0, second=0, microsecond=0)

        with db_session(interaction.user) as session:
            voice_messages_today = session.query(VoiceMessageAnalytics).filter(
                VoiceMessageAnalytics.timestamp == today,
                VoiceMessageAnalytics.author == user.id,
            )

        author_voice_messages_seconds = 0

        for voice_message in voice_messages_today:
            author_voice_messages_seconds += voice_message.duration

        author_voice_messages_minutes = author_voice_messages_seconds / 60
        author_voice_messages_cost = author_voice_messages_minutes * 0.006

        await interaction.followup.send(
            embed=SersiEmbed(
                title=f"Voice Messages Today by {user.display_name}",
                description=f"Today, {author_voice_messages_minutes} minutes ({author_voice_messages_seconds} seconds) of voice messages have been sent by {user.mention}. This costs ${author_voice_messages_cost}.",
            ),
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
            with db_session(message.author) as session:
                existing_voice_message = (
                    session.query(VoiceMessageAnalytics)
                    .filter_by(message_id=message.id)
                    .first()
                )

            if existing_voice_message:
                return

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

            eligible, reason = check_if_voice_message_eligible(message, self.config)

            if eligible is False:
                await message.reply(reason, delete_after=5)
                os.remove(f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav")

                await message.delete()
                return

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

            with db_session(message.author) as session:
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

            message.content = transcription.text
            self.bot.dispatch("message", message)

            await message.reply(f"**Transcription:**\n{transcription.text}")

            os.remove(f"{GRANDPARENT_DIR}/files/TempAudio/{filename[:-4]}.wav")

            with db_session(message.author) as session:
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


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Voice(bot, kwargs["config"]))
