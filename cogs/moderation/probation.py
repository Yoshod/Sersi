import nextcord
from nextcord.ext import commands

from baseutils import ConfirmView, DualCustodyView, SersiEmbed
from configutils import Configuration
from permutils import permcheck, is_mod, is_full_mod
from caseutils import case_history, probation_case


class Probation(commands.Cog):
    def __init__(self, bot: nextcord.Client, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersisuccess = config.emotes.success
        self.sersifail = config.emotes.fail

    @commands.command(aliases=["addp", "addprob", "pn"])
    async def addprobation(
        self, ctx: commands.Context, member: nextcord.Member, *, reason="not specified"
    ):
        if not await permcheck(ctx, is_mod):
            return

        probation_role = ctx.guild.get_role(self.config.roles.probation)

        if probation_role in member.roles:
            await ctx.reply(f"{self.sersifail} member is already in probation")
            return

        @ConfirmView.query(title="Add Member to probation",
            prompt="Following member will be given probation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            })
        @DualCustodyView.query(title="Add Member to probation",
            prompt="Following member will be given probation:",
            perms=is_full_mod,
            embed_args={
                "User": member.mention,
                "Reason": reason,
                "Moderator": ctx.author.mention,
            })
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            await member.add_roles(probation_role, reason=reason, atomic=True)

            unique_id = case_history(self.config, member.id, "Probation")
            probation_case(self.config, unique_id, member.id,
                           ctx.author.id, confirming_moderator.id, reason)

            log_embed = SersiEmbed(
                title="Member put into Probation",
                fields={
                    "Resposible Moderator:": ctx.author.mention,
                    "Confirming Moderator:": confirming_moderator.mention,
                    "Member": member.mention,
                    "Reason:": reason,
                }
            )

            log_channel = ctx.guild.get_channel(
                self.config.channels.logging)
            await log_channel.send(embed=log_embed)

            log_channel = ctx.guild.get_channel(
                self.config.channels.mod_logs)
            await log_channel.send(embed=log_embed)

            dm_embed = SersiEmbed(
                title="Adam Something Central Probation",
                description="Your behaviour on Adam Something Central has resulted in being put into probation by a moderator, continued rule breaking may result in a ban",
                colour=nextcord.Colour.brand_red(),
                fields={"Reason specified by moderator:", reason}
            )
            await member.send(embed=dm_embed)

            return SersiEmbed(
                title="Member in Probation",
                description=f"{member.mention} has been put into probation, continued rule breaking may result in a ban",
                colour=nextcord.Colour.brand_red(),
                fields={
                    "User": member.mention,
                    "Reason": reason,
                    "Moderator": ctx.author.mention,
                }
            )
        await execute(self.bot, self.config, ctx)

    @commands.command(aliases=["rmp", "rmprob"])
    async def removeprobation(self, ctx: commands.Context, member: nextcord.Member, *, reason):
        if not await permcheck(ctx, is_mod):
            return

        probation_role = ctx.guild.get_role(self.config.roles.probation)

        if probation_role not in member.roles:
            await ctx.reply(
                "Error: cannot remove user from probation, member is currently not in probation"
            )
            return
        
        @ConfirmView.query(title="Remove Member from probation",
            prompt="Following member will be removed from probation:",
            embed_args={
                "User": member.mention,
                "Reason": reason,
            })
        @DualCustodyView.query(title="Remove Member from probation",
            prompt="Following member will be removed from probation:",
            perms=is_full_mod,
            embed_args={
                "User": member.mention,
                "Reason": reason,
                "Moderator": ctx.author.mention,
            })
        async def execute(*args, confirming_moderator: nextcord.Member, **kwargs):
            await member.remove_roles(probation_role, reason=reason, atomic=True)

            log_embed = SersiEmbed(
                title="Member removed from Probation",
                fields={
                    "Resposible Moderator:": ctx.author.mention,
                    "Confirming Moderator:": confirming_moderator.mention,
                    "Member": member.mention,
                    "Reason:": reason,
                }
            )

            log_channel = ctx.guild.get_channel(
                self.config.channels.logging)
            await log_channel.send(embed=log_embed)

            log_channel = ctx.guild.get_channel(
                self.config.channels.mod_logs)
            await log_channel.send(embed=log_embed)

            dm_embed = SersiEmbed(
                title="Adam Something Central Probation Over",
                description="You were removed from probation on Adam Something Central",
                colour=nextcord.Colour.brand_red(),
                fields={"Reason specified by moderator:", reason}
            )
            await member.send(embed=dm_embed)

            return SersiEmbed(
                title="Member removed from Probation",
                description=f"{member.mention} was succesfully removed from probation!",
                colour=nextcord.Colour.brand_red(),
                fields={
                    "User": member.mention,
                    "Reason": reason,
                    "Moderator": ctx.author.mention,
                }
            )
        await execute(self.bot, self.config, ctx)


def setup(bot, **kwargs):
    bot.add_cog(Probation(bot, kwargs["config"]))
