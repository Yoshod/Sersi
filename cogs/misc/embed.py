# nextcord imports
import nextcord
from nextcord.ext import commands

# other libs
import datetime

# sersi imports
from utils.sersi_embed import SersiEmbed
from utils.base import get_discord_timestamp
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

        # build embed
        announcement_embed: nextcord.Embed = SersiEmbed(
            title=title, description=body, footer="Sersi Announcement"
        )

        match embed_type:
            case "moderator":
                role: nextcord.Role = interaction.guild.get_role(
                    self.config.permission_roles.moderator
                )

                announcement_embed.colour = role.colour
                if role.icon:
                    announcement_embed.set_author(
                        name="Moderator Announcement", icon_url=role.icon.url
                    )
                else:
                    announcement_embed.set_author(name="Moderator Announcement")

            case "admin":
                role: nextcord.Role = interaction.guild.get_role(
                    self.config.permission_roles.dark_moderator
                )

                announcement_embed.colour = role.colour
                if role.icon:
                    announcement_embed.set_author(
                        name="Administration Announcement", icon_url=role.icon.url
                    )
                else:
                    announcement_embed.set_author(name="Administration Announcement")

            case "cet":
                role: nextcord.Role = interaction.guild.get_role(
                    self.config.permission_roles.cet
                )

                announcement_embed.colour = role.colour
                if role.icon:
                    announcement_embed.set_author(
                        name="Community Announcement", icon_url=role.icon.url
                    )
                else:
                    announcement_embed.set_author(name="Community Announcement")

            case "staff":
                announcement_embed.set_author(name="Staff Announcement")

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


def setup(bot, **kwargs):
    bot.add_cog(Embeds(bot, kwargs["config"]))
