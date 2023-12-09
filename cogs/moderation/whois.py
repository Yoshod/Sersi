import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.perms import is_mod, permcheck
from utils.whois import create_whois_embed, WhoisView


class WhoisSystem(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
        description="Whois command",
    )
    async def whois(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member = nextcord.SlashOption(
            name="user",
            description="The person you wish to learn about.",
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if interaction.channel.category.name not in self.config.ignored_categories:
            await interaction.response.defer(ephemeral=True)

        else:
            await interaction.response.defer()

        if interaction.channel.category.name not in self.config.ignored_categories:
            await interaction.followup.send(
                embed=await create_whois_embed(self.config, interaction, user),
                view=WhoisView(user.id),
                ephemeral=True,
            )

        else:
            await interaction.followup.send(
                embed=await create_whois_embed(self.config, interaction, user),
                view=WhoisView(user.id),
            )

    @nextcord.message_command(
        name="WhoIs",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def whois_message(
        self, interaction: nextcord.Interaction, message: nextcord.Message
    ):
        if not await permcheck(interaction, is_mod):
            return

        if interaction.channel.category.name not in self.config.ignored_categories:
            await interaction.response.defer(ephemeral=True)

        else:
            await interaction.response.defer()

        if interaction.channel.category.name not in self.config.ignored_categories:
            await interaction.followup.send(
                embed=await create_whois_embed(
                    self.config, interaction, message.author
                ),
                view=WhoisView(message.author.id),
                ephemeral=True,
            )

        else:
            await interaction.followup.send(
                embed=await create_whois_embed(
                    self.config, interaction, message.author
                ),
                view=WhoisView(message.author.id),
            )

    @nextcord.user_command(
        name="WhoIs",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def whois_user(self, interaction: nextcord.Interaction, user: nextcord.User):
        if not await permcheck(interaction, is_mod):
            return

        if interaction.channel.category.name not in self.config.ignored_categories:
            await interaction.response.defer(ephemeral=True)

        else:
            await interaction.response.defer()

        if interaction.channel.category.name not in self.config.ignored_categories:
            await interaction.followup.send(
                embed=await create_whois_embed(self.config, interaction, user),
                view=WhoisView(user.id),
                ephemeral=True,
            )

        else:
            await interaction.followup.send(
                embed=await create_whois_embed(self.config, interaction, user),
                view=WhoisView(user.id),
            )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(WhoisSystem(bot, kwargs["config"]))
