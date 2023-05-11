import nextcord

from nextcord.ext import commands
from utils.config import Configuration
from utils.perms import permcheck, is_mod
from utils.cases import (
    offence_validity_check,
    create_warn_case,
    create_warn_case_embed,
    get_case_by_id,
    fetch_offences_by_partial_name,
)
from utils.base import SersiEmbed


class WarningSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to do warn stuff",
    )
    async def warn(self, interaction: nextcord.Interaction):
        pass

    @warn.subcommand(description="Used to warn a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The person you wish to warn.",
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence for which the user is being warned.",
        ),
        detail: str = nextcord.SlashOption(
            name="detail",
            description="Details on the offence,",
            min_length=8,
            max_length=1024,
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        if not offence_validity_check(self.config, offence):
            await interaction.followup.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. Try again or consider using the 'Other' offence."
            )

        uuid = create_warn_case(
            self.config, offender, interaction.user, offence, detail
        )

        warn_embed = SersiEmbed(
            title=f"You have been warned in {interaction.guild.name}!",
            fields={"Offence:": f"`{offence}`", "Detail:": f"`{detail}`"},
            footer="Sersi Warning",
        )

        warn_embed.set_thumbnail(interaction.guild.icon.url)

        try:
            await offender.send(embed=warn_embed)
            not_sent = False

        except nextcord.Forbidden:
            not_sent = True

        except nextcord.HTTPException:
            not_sent = True

        warn_case = get_case_by_id(self.config, uuid, False)

        logging_embed = create_warn_case_embed(warn_case, interaction)

        modlog_channel = interaction.guild.get_channel(self.config.channels.mod_logs)
        sersi_logs = interaction.guild.get_channel(self.config.channels.logging)

        await modlog_channel.send(embed=logging_embed)
        await sersi_logs.send(embed=logging_embed)

        confirm_embed = SersiEmbed(
            title="Warn Result:",
            fields={
                "Offence:": f"`{offence}`",
                "Detail:": f"`{detail}`",
                "Member:": f"{offender.mention} ({offender.id})",
            },
        )

        if not_sent:
            confirm_embed.add_field(
                name="DM Sent:", value=self.config.emotes.fail, inline=True
            )
            await interaction.followup.send(embed=confirm_embed)

        else:
            confirm_embed.add_field(
                name="DM Sent:", value=self.config.emotes.success, inline=True
            )
            await interaction.followup.send(embed=confirm_embed)

    @add.on_autocomplete("offence")
    async def search_offences(self, interaction: nextcord.Interaction, offence):
        if not is_mod(interaction.user):
            await interaction.response.send_autocomplete([])

        offences = fetch_offences_by_partial_name(self.config, offence)
        await interaction.response.send_autocomplete(offences)


def setup(bot, **kwargs):
    bot.add_cog(WarningSystem(bot, kwargs["config"]))
