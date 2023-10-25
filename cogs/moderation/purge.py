import datetime
import io

import nextcord
from chat_exporter import raw_export
from nextcord.ext import commands

from utils.config import Configuration
from utils.perms import permcheck, is_mod
from utils.sersi_embed import SersiEmbed


class Purge(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.MAXTIME = 15

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
        name="purge",
    )
    async def purge(self, interaction: nextcord.Interaction):
        pass

    @purge.subcommand()
    async def standard(
        self,
        interaction: nextcord.Interaction,
        amount: int = nextcord.SlashOption(min_value=1, max_value=100),
        member: nextcord.Member = nextcord.SlashOption(required=False),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        if not member:
            deleted_messages = await interaction.channel.purge(limit=amount + 1)

        else:
            deleted_messages = await interaction.channel.purge(
                limit=amount + 1,
                check=lambda x: True if (x.author.id == member.id) else False,
            )

        logging = SersiEmbed(
            title="Messages Purged",
            fields={
                "Moderator:": interaction.user.mention,
                "Messages Requested:": amount,
                "Messages Purged:": len(deleted_messages) - 1,
                "Channel Purged:": interaction.channel.mention,
            },
        )

        if member is not None:
            logging.add_field(
                name="User Targeted:", value=f"{member.mention} ({member.id})"
            )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=logging,
            file=nextcord.File(
                io.BytesIO(
                    (
                        await raw_export(
                            channel=interaction.channel,
                            messages=deleted_messages,
                            military_time=True,
                        )
                    ).encode()
                ),
                filename=f"purge-{interaction.channel.name}.html",
            ),
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} All {len(deleted_messages) - 1} messages deleted!"
        )

    @commands.cooldown(1, 900, commands.BucketType.user)
    @purge.subcommand()
    async def timed(
        self,
        interaction: nextcord.Interaction,
        time: int = nextcord.SlashOption(
            description="The last x minutes to purge", min_value=1, max_value=15
        ),
        member: nextcord.Member = nextcord.SlashOption(required=False),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        time_to_delete_all_messages_after: datetime.datetime = (
            interaction.created_at - datetime.timedelta(minutes=time)
        )

        if member:
            deleted_messages = await interaction.channel.purge(
                limit=10 * time,
                check=lambda x: True if (x.author.id == member.id) else False,
                after=time_to_delete_all_messages_after,
            )

        else:
            deleted_messages = await interaction.channel.purge(
                limit=10 * time,
                after=time_to_delete_all_messages_after,
            )

        transcript_file = nextcord.File(
            io.BytesIO(
                (
                    await raw_export(
                        channel=interaction.channel,
                        messages=deleted_messages,
                        military_time=True,
                    )
                ).encode()
            ),
            filename=f"purge-{interaction.channel.name}.html",
        )

        logging = SersiEmbed(
            title="Messages Purged",
            fields={
                "Moderator:": interaction.user.mention,
                "Time Specified:": f"{time} minutes",
                "Messages Purged:": len(deleted_messages) - 1,
                "Channel Purged:": interaction.channel.mention,
            },
        )
        if member:
            logging.add_field(
                name="User Targeted:", value=f"{member.mention} ({member.id})"
            )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=logging,
            file=nextcord.File(
                io.BytesIO(
                    (
                        await raw_export(
                            channel=interaction.channel,
                            messages=deleted_messages,
                            military_time=True,
                        )
                    ).encode()
                ),
                filename=f"purge-{interaction.channel.name}.html",
            ),
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} All {len(deleted_messages) - 1} messages deleted!"
        )

    @nextcord.message_command(
        name="Purge After This Message",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640],
    )
    async def until(self, interaction: nextcord.Interaction, message: nextcord.Message):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=True)

        deleted_messages: list[nextcord.Message] = await message.channel.purge(
            after=message
        )

        await interaction.guild.get_channel(self.config.channels.mod_logs).send(
            embed=SersiEmbed(
                title="Messages Purged",
                fields={
                    "Moderator:": interaction.user.mention,
                    "Message Specified:": message.jump_url,
                    "Messages Purged:": len(deleted_messages) - 1,
                    "Channel Purged:": message.channel.mention,
                },
            ),
            file=nextcord.File(
                io.BytesIO(
                    (
                        await raw_export(
                            channel=interaction.channel,
                            messages=deleted_messages,
                            military_time=True,
                        )
                    ).encode()
                ),
                filename=f"purge-{interaction.channel.name}.html",
            ),
        )

        await interaction.followup.send(
            f"{self.config.emotes.success} All {len(deleted_messages) - 1} messages deleted!"
        )


def setup(bot, **kwargs):
    bot.add_cog(Purge(bot, kwargs["config"]))
