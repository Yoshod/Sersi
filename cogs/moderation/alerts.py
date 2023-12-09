from datetime import datetime, timedelta

import nextcord
from nextcord.ext import commands, tasks

from utils.alerts import AlertType, get_alert_type, add_response_time
from utils.base import sanitize_mention
from utils.channels import get_message_from_url
from utils.config import Configuration
from utils.database import db_session, SlurUsageCase, BadFaithPingCase, Alert
from utils.perms import is_mod, permcheck
from utils.sersi_embed import SersiEmbed


class Alerts(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        if bot.is_ready():
            self.alerts_reminder.start()

    @tasks.loop(minutes=1)
    async def alerts_reminder(self):
        with db_session() as session:
            alerts: list[Alert] = (
                session.query(Alert)
                .filter_by(response_time=None)
                .filter(Alert.creation_time < datetime.utcnow() - timedelta(hours=3))
                .all()
            )

        for alert in alerts:
            time_since_alert: timedelta = datetime.utcnow() - alert.creation_time
            if time_since_alert.seconds // 60 % 60 != 0:
                continue

            message = await get_message_from_url(self.bot, alert.report_url)

            if message is None or not message.components:
                add_response_time(message)
                continue

            await message.reply(
                f"<@&{self.config.permission_roles.moderator}> This alert has not had a recorded response for {time_since_alert.seconds//3600} hours.",
            )

    @commands.Cog.listener()
    async def on_ready(self):
        self.alerts_reminder.start()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return
        if not interaction.data["custom_id"].startswith("alert"):
            return

        if not await permcheck(interaction, is_mod):
            return

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        embed = interaction.message.embeds[0]
        for field in embed.fields:
            if field.name == "User:":
                user_id = sanitize_mention(field.value)
            elif field.name == "Slurs Found:":
                slurs = field.value

        alert_type = get_alert_type(interaction.message)

        match interaction.data["custom_id"]:
            case "alert_action_taken":
                embed.add_field(
                    name="Action Taken By:",
                    value=interaction.user.mention,
                    inline=False,
                )
                embed.color = nextcord.Color.green()

                if alert_type == AlertType.Slur:
                    with db_session() as session:
                        case = SlurUsageCase(
                            offender=user_id,
                            moderator=interaction.user.id,
                            slur_used=slurs,
                            report_url=interaction.message.jump_url,
                        )

                        session.add(case)
                        session.commit()

            case "alert_action_not_necessary":
                embed.add_field(
                    name="Action Deemed Not Necessary By:",
                    value=interaction.user.mention,
                    inline=False,
                )
                embed.color = nextcord.Color.light_grey()

            case "alert_acceptable_use":
                embed.add_field(
                    name="Usage Deemed Acceptable By:",
                    value=interaction.user.mention,
                    inline=False,
                )
                embed.color = nextcord.Color.light_grey()

            case "alert_false_positive":
                embed.add_field(
                    name="Deemed As False Positive By:",
                    value=interaction.user.mention,
                    inline=False,
                )
                embed.color = nextcord.Color.red()

                false_positive_embed: nextcord.Embed = SersiEmbed(
                    title="Marked as False Positive",
                    description=embed.description,
                    color=nextcord.Color.red(),
                    fields={
                        "Slurs Found": slurs,
                    },
                ).set_author(
                    name=interaction.user.display_name,
                    icon_url=interaction.user.avatar.url,
                )

                await interaction.guild.get_channel(
                    self.config.channels.false_positives
                ).send(embed=false_positive_embed)

            case "alert_bad_faith_ping":
                embed.add_field(
                    name="Ping Deemed as Bad Faith by:",
                    value=interaction.user.mention,
                    inline=False,
                )
                embed.color = nextcord.Color.brand_red()

                with db_session() as session:
                    case = BadFaithPingCase(
                        offender=user_id,
                        moderator=interaction.user.id,
                        report_url=interaction.message.jump_url,
                    )

                    session.add(case)
                    session.commit()

            case "alert_dismiss":
                embed.add_field(
                    name="Dismissed By:",
                    value=interaction.user.mention,
                    inline=False,
                )
                embed.color = nextcord.Color.dark_gray()

        embed.footer.icon_url = interaction.user.avatar.url

        await interaction.message.edit(embed=embed, view=None)
        add_response_time(interaction.message)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Alerts(bot, kwargs["config"]))
