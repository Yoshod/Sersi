import datetime
import nextcord
from nextcord.ext import commands
from utils.base import convert_to_timedelta
from utils.cases import create_case_embed

from utils.config import Configuration
from utils.perms import is_staff, permcheck
from utils.database import WarningCase, TimeoutCase, db_session, Case
from utils.sersi_embed import SersiEmbed


class MassPing(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if message.guild is None:
            return

        if message.author.bot:
            return

        if await permcheck(message, is_staff):
            return

        if len(message.mentions) > 2:
            with db_session() as session:
                previous_warning = (
                    session.query(WarningCase)
                    .filter_by(offender=message.author.id)
                    .filter_by(moderator=self.bot.user.id)
                    .filter_by(offence="Spamming")
                    .order_by(WarningCase.created.desc())
                    .first()
                )

            if previous_warning:
                if previous_warning.created > (
                    datetime.datetime.now() - datetime.timedelta(days=1)
                ):
                    previous_within_day = True

                else:
                    previous_within_day = False

            else:
                previous_within_day = False

            with db_session() as session:
                warning = WarningCase(
                    offender=message.author.id,
                    moderator=self.bot.user.id,
                    offence="Spamming",
                    details=f"User mass pinged {len(message.mentions)} users in a single message. {'This is at least second time in 24 hours.' if previous_within_day else ''}",
                )
                session.add(warning)

                if previous_within_day:
                    planned_end: datetime.timedelta = convert_to_timedelta("m", 30)

                    await message.author.timeout(
                        planned_end,
                        reason="Spamming - Sersi Automoderation",
                    )

                    timeout = TimeoutCase(
                        offender=message.author.id,
                        moderator=self.bot.user.id,
                        offence="Spamming",
                        details=f"User mass pinged {len(message.mentions)} users in a single message.",
                        duration=30,
                        planned_end=datetime.datetime.utcnow() + planned_end,
                    )
                    session.add(timeout)

                session.commit()

                log_channel = message.guild.get_channel(self.config.channels.logging)
                mod_log_channel = message.guild.get_channel(
                    self.config.channels.mod_logs
                )

                if previous_within_day:
                    timeout_case = session.query(Case).filter_by(id=timeout.id).first()

                    await message.author.send(
                        embed=SersiEmbed(
                            title="You have been timed out",
                            description=f"You have been timed out for 30 minutes for mass pinging {len(message.mentions)} users in a single message. This is an automated decision by Sersi Automoderation. To appeal this timeout, please run the </ticket create:1169396755788468345> command. You can reply in that ticket using the </ticket send_message:1169396755788468345> command.",
                        )
                    )

                    logging_embed: SersiEmbed = create_case_embed(
                        timeout_case, message, self.config
                    )

                    await log_channel.send(embed=logging_embed)
                    await mod_log_channel.send(embed=logging_embed)

                    return

                await message.author.send(
                    embed=SersiEmbed(
                        title="Warning",
                        description=f"You have been warned for mass pinging {len(message.mentions)} users in a single message. This is your first warning. If you continue to mass ping, you will be timed out. This is an automated decision by Sersi Automoderation. To appeal this warning, please run the </ticket create:1169396755788468345> command.",
                    )
                )

                warning_case = session.query(Case).filter_by(id=warning.id).first()

                logging_embed: SersiEmbed = create_case_embed(
                    warning_case, message, self.config
                )

                await log_channel.send(embed=logging_embed)
                await mod_log_channel.send(embed=logging_embed)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(MassPing(bot, kwargs["config"]))
