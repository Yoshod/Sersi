import nextcord

from nextcord.ext import commands

from utils.cases.misc import offence_validity_check
from utils.config import Configuration
from utils.perms import permcheck, is_mod, is_dark_mod, is_immune, target_eligibility
from utils.base import SersiEmbed


class TimeoutSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to do timeout stuff",
    )
    async def timeout(self, interaction: nextcord.Interaction):
        pass

    @timeout.subcommand(description="Used to timeout a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The person you wish to warn.",
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence for which the user is being timed out.",
        ),
        detail: str = nextcord.SlashOption(
            name="detail",
            description="Details on the offence,",
            min_length=8,
            max_length=1024,
        ),
        duration: int = nextcord.SlashOption(
            name="duration",
            description="The length of time the user should be timed out for",
            min_value=1,
            max_value=40320,
        ),
        timespan: str = nextcord.SlashOption(
            name="timespan",
            description="The unit of time being used",
            choices={
                "Minutes": "m",
                "Hours": "h",
                "Days": "d",
                "Weeks": "w",
            },
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        await interaction.response.defer(ephemeral=False)

        valid_time = False

        match timespan:
            case "m":
                valid_time = True

            case "h":
                if not duration > 672:
                    valid_time = True

            case "d":
                if not duration > 28:
                    valid_time = True

            case "w":
                if not duration > 4:
                    valid_time = True

        if not valid_time:
            interaction.followup.send(
                f"{self.config.emotes.fail} You have input an invalid timeout duration. "
                "A timeout cannot last any longer than 28 days."
            )

        if not target_eligibility(interaction.user, offender):
            warning_alert = SersiEmbed(
                title="Unauthorised Moderation Target",
                description=f"{interaction.user.mention} ({interaction.user.id}) attempted to warn {offender.mention} ({offender.id}) despite being outranked!",
            )

            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )

            mega_admin_role = interaction.guild.get_role(
                self.config.permission_roles.dark_moderator
            )

            await logging_channel.send(
                content=f"**ALERT:** {mega_admin_role.mention}", embed=warning_alert
            )

            await interaction.followup.send(
                f"{self.config.emotes.fail} {offender.mention} is a higher level than you. This has been reported."
            )
            return

        if is_immune(offender):
            if not await permcheck(interaction, is_dark_mod):
                await interaction.followup.send(
                    f"{self.config.emotes.fail} {offender.mention} is immune."
                )
                return

        if not offence_validity_check(self.config, offence):
            await interaction.followup.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. Try again or consider using the 'Other' offence."
            )
            return
