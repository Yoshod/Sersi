import nextcord
from nextcord.ext import commands
from utils.base import PageView

from utils.config import Configuration
from utils.notes import fetch_notes
from utils.perms import is_mod, permcheck
from utils.sersi_embed import SersiEmbed
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

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        if not btn_id.startswith("whois-"):
            return

        await interaction.response.defer(ephemeral=True)

        match btn_id.split(":", 1):
            case ["whois-notes", user_id]:
                note_embed = SersiEmbed(title=f"{interaction.guild.name} Notes")
                note_embed.set_thumbnail(interaction.guild.icon.url)

                view = PageView(
                    config=self.config,
                    base_embed=note_embed,
                    fetch_function=fetch_notes,
                    author=interaction.user,
                    entry_form="{entry}",
                    field_title="{entries[0].list_entry_header}",
                    inline_fields=False,
                    cols=5,
                    per_col=1,
                    init_page=1,
                    ephemeral=True,
                    member_id=user_id,
                    author_id=None,
                )

                await view.send_followup(interaction)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(WhoisSystem(bot, kwargs["config"]))
