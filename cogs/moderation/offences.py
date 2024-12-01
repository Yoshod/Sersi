import nextcord
from nextcord.ext import commands
from utils.database import guild_db_manager, Offences as OffencesDB
from utils.perms import get_permissions
from utils.sersi_embed import SersiEmbed


class Offences(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @nextcord.slash_command(
        name="offences", description="Manage offences", guild_ids=[977377117895536640]
    )
    async def offences(self, interaction: nextcord.Interaction):
        pass

    @offences.subcommand(
        name="add",
        description="Add an offence",
    )
    async def add(
        self,
        interaction: nextcord.Interaction,
        offence_name: str = nextcord.SlashOption(description="Name of the offence"),
        offence_severity: int = nextcord.SlashOption(
            description="Severity of the offence",
            min_value=1,
            max_value=10,
        ),
        offence_description: str = nextcord.SlashOption(
            description="Description of the offence",
            required=False,
        ),
    ):
        permissions = await get_permissions(
            interaction.guild.get_member(interaction.user.id)
        )
        if not permissions["edit_offences"]:
            await interaction.response.send_message(
                "You do not have permission to do this."
            )
            return

        await interaction.response.defer(ephemeral=True)

        try:
            with guild_db_manager.get_session() as session:
                new_offence = OffencesDB(
                    offence_name=offence_name,
                    offence_severity=offence_severity,
                    offence_description=offence_description,
                )

                session.add(new_offence)
                session.commit()

        except Exception:
            await interaction.followup.send("This offence already exists.")

        await interaction.followup.send(
            embed=SersiEmbed(
                title="Offence Added",
                description=f"**Name:** {offence_name}\n**Severity:** {offence_severity}\n**Description:** {offence_description}",
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(Offences(bot))
