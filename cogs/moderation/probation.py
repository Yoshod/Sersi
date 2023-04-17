import nextcord
from nextcord.ext import commands

from baseutils import ConfirmView, DualCustodyView, SersiEmbed
from configutils import Configuration
from permutils import permcheck, is_mod, is_full_mod


class Probation(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Puts a member into probation",
    )
    async def add_to_probation(
        self,
        interaction: nextcord.Interaction,
        member: nextcord.Member,
        reason: str = nextcord.SlashOption(required=False),
    ):
        if not await permcheck(interaction, is_mod):
            return

        probation_role = interaction.guild.get_role(self.config.roles.probation)

        if probation_role in member.roles:
            await interaction.send(
                f"{self.sersifail} member is already in probation", ephemeral=True
            )
            return

        @ConfirmView.query(
            title="Add Member to probation",
            prompt="Following member will be given probation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            },
        )
        @DualCustodyView.query(
            title="Add Member to probation",
            prompt="Following member will be given probation:",
            perms=is_full_mod,
            embed_args={
                "User": member.mention,
                "Reason": reason,
                "Moderator": interaction.user.mention,
            },
        )
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            await member.add_roles(probation_role, reason=reason, atomic=True)

            """unique_id = case_history(self.config, member.id, "Probation")
            probation_case(
                self.config,
                unique_id,
                member.id,
                interaction.user.id,
                confirming_moderator.id,
                reason,
            )"""

            log_embed = SersiEmbed(
                title="Member put into Probation",
                fields={
                    "Responsible Moderator:": interaction.user.mention,
                    "Confirming Moderator:": confirming_moderator.mention,
                    "Member": member.mention,
                    "Reason:": reason,
                },
            )

            log_channel = interaction.guild.get_channel(self.config.channels.logging)
            await log_channel.send(embed=log_embed)

            log_channel = interaction.guild.get_channel(self.config.channels.mod_logs)
            await log_channel.send(embed=log_embed)

            dm_embed = SersiEmbed(
                title="Adam Something Central Probation",
                description="Your behaviour on Adam Something Central has resulted in being put into probation by a "
                "moderator, continued rule breaking may result in a ban",
                colour=nextcord.Colour.brand_red(),
                fields={"Reason specified by moderator:": reason},
            )
            await member.send(embed=dm_embed)

            return SersiEmbed(
                title="Member in Probation",
                description=f"{member.mention} has been put into probation, continued rule breaking may result in a ban",
                fields={
                    "User": member.mention,
                    "Reason": reason,
                    "Moderator": interaction.user.mention,
                },
            )

        await execute(self.bot, self.config, interaction)

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Removes a member from probation",
    )
    async def remove_from_probation(
        self, interaction: nextcord.Interaction, member: nextcord.Member, reason:str = nextcord.SlashOption(required=False)
    ):
        if not await permcheck(interaction, is_mod):
            return

        probation_role:nextcord.Role = interaction.guild.get_role(self.config.roles.probation)

        if probation_role not in member.roles:
            await interaction.reply(
                "Error: cannot remove user from probation, member is currently not in probation"
            )
            return

        @ConfirmView.query(
            title="Remove Member from probation",
            prompt="Following member will be removed from probation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            },
        )
        @DualCustodyView.query(
            title="Remove Member from probation",
            prompt="Following member will be removed from probation:",
            perms=is_full_mod,
            embed_args={
                "User": member.mention,
                "Reason": reason,
                "Moderator": ctx.author.mention,
            },
        )
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            await member.remove_roles(probation_role, reason=reason, atomic=True)

            log_embed = SersiEmbed(
                title="Member removed from Probation",
                fields={
                    "Responsible Moderator:": ctx.author.mention,
                    "Confirming Moderator:": confirming_moderator.mention,
                    "Member": member.mention,
                    "Reason:": reason,
                },
            )

            log_channel = ctx.guild.get_channel(self.config.channels.logging)
            await log_channel.send(embed=log_embed)

            log_channel = ctx.guild.get_channel(self.config.channels.mod_logs)
            await log_channel.send(embed=log_embed)

            dm_embed = SersiEmbed(
                title="Adam Something Central Probation Over",
                description="You were removed from probation on Adam Something Central",
                colour=nextcord.Colour.brand_red(),
                fields={"Reason specified by moderator:": reason},
            )
            await member.send(embed=dm_embed)

            return SersiEmbed(
                title="Member removed from Probation",
                description=f"{member.mention} was successfully removed from probation!",
                fields={
                    "User": member.mention,
                    "Reason": reason,
                    "Moderator": ctx.author.mention,
                },
            )

        await execute(self.bot, self.config, ctx)


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Probation(bot, kwargs["config"]))
