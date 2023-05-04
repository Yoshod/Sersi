# nextcord imports
import nextcord
from nextcord.ext import commands

# other libs
import datetime

# sersi imports
from utils.base import SersiEmbed, get_discord_timestamp
from utils.config import Configuration
from utils.perms import permcheck, is_mod, is_dark_mod, is_staff, is_cet


class SendButton(nextcord.ui.Button):
    def __init__(self, channel: nextcord.TextChannel):
        super().__init__(label="Send Embed", style=nextcord.ButtonStyle.green)
        self.channel = channel

    async def callback(self, interaction: nextcord.Interaction):
        await self.channel.send(embed=interaction.message.embeds[0])
        await interaction.message.edit(
            embed=interaction.message.embeds[0].add_field(
                name="Embed Sent",
                value=f"Sent to {self.channel.mention} at {get_discord_timestamp(datetime.datetime.now(datetime.timezone.utc))}",
                inline=False,
            ),
            view=None,
        )
        await interaction.send("Embed sent!", ephemeral=True)


class CancelButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(label="Cancel Embed", style=nextcord.ButtonStyle.red)

    async def callback(self, interaction: nextcord.Interaction):
        await interaction.message.delete()
        await interaction.send("Cancelled!", ephemeral=True)


class YesNoView(nextcord.ui.View):
    def __init__(self, embed_creator: nextcord.Member, channel: nextcord.TextChannel):
        super().__init__(timeout=None)
        self.embed_creator = embed_creator
        self.add_item(SendButton(channel))
        self.add_item(CancelButton())

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        return interaction.user == self.embed_creator


class Embeds(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False, guild_ids=[977377117895536640, 856262303795380224]
    )
    async def embed(self, interaction: nextcord.Interaction):
        pass

    @embed.subcommand(description="Creates an embed and sends it somewhere nice")
    async def send(
        self,
        interaction: nextcord.Interaction,
        type: str = nextcord.SlashOption(
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
        title: str = nextcord.SlashOption(description="The Title of the Embed"),
        body: str = nextcord.SlashOption(description="The Body of the Embed"),
    ):

        await interaction.response.defer()

        # permcheck
        match type:
            case "moderator":
                if not permcheck(interaction, is_mod):
                    return
            case "admin":
                if not permcheck(interaction, is_dark_mod):
                    return
            case "cet":
                if not permcheck(interaction, is_cet):
                    return
            case "staff":
                if not permcheck(interaction, is_staff):
                    return

        # build embed

        announcement_embed: nextcord.Embed = SersiEmbed(
            title=title, description=body, footer="Sersi Announcement"
        )

        match type:
            case "moderator":
                announcement_embed.set_author(name="Moderator Announcement")
                announcement_embed.colour = interaction.guild.get_role(
                    self.config.permission_roles.moderator
                ).colour

            case "admin":
                announcement_embed.set_author(name="Administration Announcement")
                announcement_embed.colour = interaction.guild.get_role(
                    self.config.permission_roles.dark_moderator
                ).colour

            case "cet":
                announcement_embed.set_author(name="Community Announcement")
                announcement_embed.colour = interaction.guild.get_role(
                    self.config.permission_roles.cet
                ).colour

            case "staff":
                announcement_embed.set_author(name="Staff Announcement")

        await interaction.send(
            embed=announcement_embed, view=YesNoView(interaction.user, channel)
        )


def setup(bot, **kwargs):
    bot.add_cog(Embeds(bot, kwargs["config"]))
