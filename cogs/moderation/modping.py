import nextcord
from nextcord.ext import commands

import discordTokens
from openai import OpenAI

from utils.alerts import create_alert_log, AlertType, AlertView
from utils.sersi_embed import SersiEmbed
from utils.base import (
    modmention_check,
    ignored_message,
)
from utils.config import Configuration


class ModPing(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.Cog.listener()
    async def on_message(self, message: nextcord.Message):
        if ignored_message(self.config, message):
            return

        if modmention_check(self.config, message.content):
            # Reply to user
            response_embed: nextcord.Embed = SersiEmbed(
                title="Moderator Ping Acknowledgment",
                description=f"{message.author.mention} moderators have been notified of your ping and will investigate when able to do so.",
                footer="Sersi Moderator Ping Detection",
            )
            await message.channel.send(embed=response_embed)
            await message.channel.send(
                message.guild.get_role(self.config.roles.staff.trial_mod).mention,
                delete_after=1,
            )

            original_message = message

            # last 100 messages in the channel in user: message format
            messages = []
            authors = {}
            counter = 0
            async for message in message.channel.history(limit=100):
                if message.author.bot:
                    continue

                if message.author.name not in authors.keys():
                    authors[message.author.name] = counter
                    counter += 1

                messages.append(
                    f"NEW MESSAGE - {authors[message.author.name]}: {message.content}"
                )

            messages_content = "\n".join(messages)

            client = OpenAI(api_key=discordTokens.getOpenAIApiKey())

            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a moderation assistant tool in a Discord server. The moderation team has been pinged and will investigate the ping when able to do so. Examine the messages below to provide context to the moderation team. Reply with: **Summary of Discussion**: <summary>, **Likely Reason for Mod Ping**: <reason>. Keep it concise, to the point, professional, and never recommend any action to the moderation team.You should refer to users by their number before the colon in the message.",
                        },
                        {"role": "user", "content": messages_content},
                    ],
                )
            except Exception:
                completion = None

            if completion:
                await message.guild.owner.send(
                    f"**Mod Ping Detected**\n\n**AI Response**\n\n{completion.choices[0].message.content}",
                    embed=SersiEmbed(
                        title="Authors",
                        description=f"The following authors were detected in the last 100 messages in the channel:\n\n{authors}",
                    ),
                )

            # notification for mods
            channel = self.bot.get_channel(self.config.channels.staff.alert)
            alert_embed: nextcord.Embed = SersiEmbed(
                title="Moderator Ping",
                description="A moderation role has been pinged, please investigate the ping and take action as appropriate.",
                fields={
                    "Channel:": original_message.channel.mention,
                    "User:": original_message.author.mention,
                    "Context:": original_message.content,
                    "URL:": original_message.jump_url,
                },
                footer="Sersi Moderator Ping Detection",
            )

            alert = await channel.send(
                embed=alert_embed, view=AlertView(AlertType.Ping, message.author)
            )
            create_alert_log(message=alert, alert_type=AlertType.Ping)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(ModPing(bot, kwargs["config"]))
