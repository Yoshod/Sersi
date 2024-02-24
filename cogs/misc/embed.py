# nextcord imports
import nextcord
from nextcord.ext import commands, tasks

# other libs
import datetime

# sersi imports
from utils.base import get_discord_timestamp, serialise_timedelta, deserialise_timedelta
from utils.config import Configuration
from utils.perms import permcheck, is_mod, is_dark_mod, is_staff, is_cet
from utils.database import Autopost as AutopostDB, db_session, AutopostFields
from utils.embeds import AutopostData, determine_embed_type


class SendButton(nextcord.ui.Button):
    def __init__(
        self, channel: nextcord.TextChannel, autopost_data: AutopostData | None
    ) -> None:
        super().__init__(label="Send Embed", style=nextcord.ButtonStyle.green)
        self.channel = channel
        self.autopost_data = autopost_data

    async def callback(self, interaction: nextcord.Interaction):
        if self.autopost_data:
            with db_session() as session:
                session.add(
                    AutopostDB(
                        author=self.autopost_data.author,
                        title=self.autopost_data.title,
                        description=self.autopost_data.description,
                        type=self.autopost_data.embed_type,
                        channel=self.autopost_data.channel,
                        timedelta_str=self.autopost_data.timedelta,
                        media_url=self.autopost_data.media_url,
                    )
                )
                session.commit()

                autopost = (
                    session.query(AutopostDB)
                    .order_by(AutopostDB.created.desc())
                    .first()
                )

                autopost_id = autopost.autopost_id

                if self.autopost_data.fields:
                    for name, value in self.autopost_data.fields.items():
                        session.add(
                            AutopostFields(
                                autopost_id=autopost_id,
                                field_name=name,
                                field_value=value,
                            )
                        )
                    session.commit()

        message = await self.channel.send(embed=interaction.message.embeds[0])

        await interaction.message.edit(
            embed=interaction.message.embeds[0].add_field(
                name="Embed Sent",
                value=f"Sent to {self.channel.mention} at {get_discord_timestamp(datetime.datetime.now(datetime.timezone.utc))}",
                inline=False,
            ),
            view=None,
        )

        await interaction.send("Embed sent!", ephemeral=True)

        if self.autopost_data:
            with db_session() as session:
                autopost = (
                    session.query(AutopostDB).filter_by(autopost_id=autopost_id).first()
                )
                autopost.last_post_id = message.id
                session.commit()


class CancelButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="Cancel Embed", style=nextcord.ButtonStyle.red)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.message.delete()
        await interaction.send("Cancelled!", ephemeral=True)


class YesNoView(nextcord.ui.View):
    def __init__(
        self,
        embed_creator: nextcord.Member,
        channel: nextcord.TextChannel,
        autopost_data: AutopostData | None,
    ):
        super().__init__(timeout=None)
        self.embed_creator = embed_creator
        self.add_item(SendButton(channel, autopost_data))
        self.add_item(CancelButton())

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user == self.embed_creator


class Embeds(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

        if self.bot.is_ready():
            self.autopost_loop.start(bot=self.bot)

    def cog_unload(self):
        self.autopost_loop.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.autopost_loop.start(bot=self.bot)

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def embed(self, interaction: nextcord.Interaction):
        pass

    @embed.subcommand(description="Creates an embed and sends it somewhere nice")
    async def send(
        self,
        interaction: nextcord.Interaction,
        embed_type: str = nextcord.SlashOption(
            choices={
                "Moderator": "moderator",
                "Administator": "admin",
                "Community Emgagement": "cet",
                "Staff": "staff",
            }
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="The Channel to send the Embed to"
        ),
        title: str = nextcord.SlashOption(
            description="The Title of the Embed", max_length=256
        ),
        body: str = nextcord.SlashOption(
            description="The Body of the Embed", max_length=2048
        ),
    ):
        # permcheck
        match embed_type:
            case "moderator":
                if not await permcheck(interaction, is_mod):
                    return
            case "admin":
                if not await permcheck(interaction, is_dark_mod):
                    return
            case "cet":
                if not await permcheck(interaction, is_cet):
                    return
            case "staff":
                if not await permcheck(interaction, is_staff):
                    return

        await interaction.response.defer()

        announcement_embed: nextcord.Embed = await determine_embed_type(
            title, body, embed_type, interaction, self.config
        )

        await interaction.send(
            embeds=[
                announcement_embed,
                nextcord.Embed(
                    title=f"Send to {channel.mention}?",
                    colour=nextcord.Color.from_rgb(237, 91, 6),
                ),
            ],
            view=YesNoView(interaction.user, channel),
        )

    @embed.subcommand(
        description="Creates an autopost and sends it somewhere nice repeatedly"
    )
    async def autopost(
        self,
        interaction: nextcord.Interaction,
        embed_type: str = nextcord.SlashOption(
            choices={
                "Moderator": "moderator",
                "Administator": "admin",
                "Community Emgagement": "cet",
                "Staff": "staff",
            }
        ),
        channel: nextcord.TextChannel = nextcord.SlashOption(
            description="The Channel to send the Embed to"
        ),
        title: str = nextcord.SlashOption(
            description="The Title of the Embed", max_length=256
        ),
        body: str = nextcord.SlashOption(
            description="The Body of the Embed", max_length=2048
        ),
        duration: int = nextcord.SlashOption(
            name="duration",
            description="The length of time the embed should be posted for",
            min_value=1,
            max_value=40320,
        ),
        timespan: str = nextcord.SlashOption(
            name="timespan",
            description="The unit of time being used",
            choices={
                "Minutes": "m",
                "Hours": "h",
            },
        ),
        media_url: str = nextcord.SlashOption(
            name="media_url",
            description="The URL of the media to attach to the embed",
            required=False,
        ),
        field_1_title: str = nextcord.SlashOption(
            name="field_1_title",
            description="The title of the first field",
            required=False,
        ),
        field_1_body: str = nextcord.SlashOption(
            name="field_1_body",
            description="The body of the first field",
            required=False,
        ),
        field_2_title: str = nextcord.SlashOption(
            name="field_2_title",
            description="The title of the second field",
            required=False,
        ),
        field_2_body: str = nextcord.SlashOption(
            name="field_2_body",
            description="The body of the second field",
            required=False,
        ),
        field_3_title: str = nextcord.SlashOption(
            name="field_3_title",
            description="The title of the third field",
            required=False,
        ),
        field_3_body: str = nextcord.SlashOption(
            name="field_3_body",
            description="The body of the third field",
            required=False,
        ),
        field_4_title: str = nextcord.SlashOption(
            name="field_4_title",
            description="The title of the fourth field",
            required=False,
        ),
        field_4_body: str = nextcord.SlashOption(
            name="field_4_body",
            description="The body of the fourth field",
            required=False,
        ),
    ):

        if timespan == "m" and duration < 1 or duration > 1440:
            await interaction.send(
                "Duration must be between 5 and 1440 minutes", ephemeral=True
            )
            return

        if timespan == "h" and duration < 1 or duration > 24:
            await interaction.send(
                "Duration must be between 1 and 24 hours", ephemeral=True
            )
            return

        # permcheck
        match embed_type:
            case "moderator":
                if not await permcheck(interaction, is_mod):
                    return
            case "admin":
                if not await permcheck(interaction, is_dark_mod):
                    return
            case "cet":
                if not await permcheck(interaction, is_cet):
                    return
            case "staff":
                if not await permcheck(interaction, is_staff):
                    return

        await interaction.response.defer()

        fields = {}

        for i in range(1, 5):
            field_title = locals().get(f"field_{i}_title")
            field_body = locals().get(f"field_{i}_body")

            if field_title and field_body:
                fields[field_title] = field_body

        if not fields:
            fields = None

        announcement_embed: nextcord.Embed = await determine_embed_type(
            title, body, embed_type, interaction, self.config, media_url, fields
        )

        await interaction.send(
            embeds=[
                announcement_embed,
                nextcord.Embed(
                    title=f"Send to {channel.mention}?",
                    colour=nextcord.Color.from_rgb(237, 91, 6),
                ),
            ],
            view=YesNoView(
                interaction.user,
                channel,
                AutopostData(
                    author=interaction.user.id,
                    title=title,
                    description=body,
                    embed_type=embed_type,
                    channel=channel.id,
                    timedelta=serialise_timedelta(duration, timespan),
                    active=True,
                    fields=fields,
                    media_url=media_url,
                ),
            ),
        )

    @tasks.loop(minutes=1)
    async def autopost_loop(self, bot: commands.Bot):
        with db_session() as session:
            autoposts = session.query(AutopostDB).filter_by(active=True).all()

            for autopost in autoposts:
                modified_time: datetime.datetime = autopost.modified
                modified_time = modified_time.replace(tzinfo=datetime.timezone.utc)
                current_time = datetime.datetime.now(datetime.timezone.utc)
                timedelta = deserialise_timedelta(autopost.timedelta_str)

                if (current_time - modified_time) < timedelta:
                    continue

                channel: nextcord.TextChannel = bot.get_channel(autopost.channel)

                total_characters = 0
                post_autopost = True

                async for message in channel.history(limit=100):
                    if message.id == autopost.last_post_id:
                        post_autopost = False
                        break

                    total_characters += len(message.content)
                    if message.attachments:
                        total_characters += len(message.attachments) * 100

                    # TODO: Change 20 to 8000 once testing is done
                    if total_characters > 20:
                        break

                old_embed = None

                if not post_autopost:
                    continue

                partial_message = await channel.fetch_message(autopost.last_post_id)

                old_embed = partial_message.embeds[0]

                await partial_message.delete()

                message_new = await channel.send(embed=old_embed)
                autopost.last_post_id = message_new.id
                session.commit()


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Embeds(bot, kwargs["config"]))
