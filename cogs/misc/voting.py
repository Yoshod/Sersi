from datetime import datetime, timedelta

import nextcord
from nextcord.ext import tasks, commands
from sqlalchemy import func

from utils.base import get_message_from_url
from utils.config import Configuration, VoteType
from utils.database import db_session, VoteDetails, VoteRecord
from utils.perms import (
    permcheck,
    is_mod,
    is_sersi_contributor,
    is_cet,
    is_staff,
    is_admin,
)
from utils.sersi_embed import SersiEmbed


class Voting(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        if bot.is_ready():
            self.process_votes.start()

    @nextcord.slash_command(dm_permission=False)
    async def redo_vote_action(
        self,
        interaction: nextcord.Interaction,
        vote: int = nextcord.SlashOption(name="vote_id"),
    ):
        """Allows vote action to be redone in case of an error occuring"""
        if not await permcheck(interaction, is_sersi_contributor):
            return

        with db_session() as session:
            details: VoteDetails = session.query(VoteDetails).get(vote)
            if details is None:
                await interaction.response.send_message(
                    "This vote does not exist", ephemeral=True
                )
                return
            if details.outcome is None:
                await interaction.response.send_message(
                    "This vote has not been decided yet", ephemeral=True
                )
                return

            self.bot.dispatch(self.config.voting[details.vote_type].action, details)

        await interaction.response.send_message(
            "The action has been triggered", ephemeral=True
        )

        # logging
        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(
            embed=SersiEmbed(
                title="Redo Vote Action",
                description=f"{interaction.user.mention} has redone the vote action for vote {vote}",
                fields={
                    "Vote Type": details.vote_type,
                    "Vote": details.vote_url,
                    "Outcome": details.outcome,
                },
            )
        )

    @commands.Cog.listener()
    async def on_ready(self):
        self.process_votes.start()

    def cog_unload(self):
        self.process_votes.cancel()

    async def record_vote(self, vote: VoteRecord, interaction: nextcord.Interaction):
        with db_session() as session:
            session.merge(vote)
            session.commit()

        new_embed = interaction.message.embeds[0]
        # if the user has voted before, edit previous vote
        for index, field in enumerate(new_embed.fields):
            if (
                field.name.startswith("Voted")
                and str(interaction.user.id) in field.value
            ):
                new_embed.set_field_at(
                    index,
                    name=f"Voted {vote.vote.capitalize()}",
                    value=f"<@{interaction.user.id}>\n*{vote.comment or '`No comment provided`'}*",
                    inline=False,
                )
                break
        else:  # oh no, found usage for this cursed feature
            new_embed.add_field(
                name=f"Voted {vote.vote.capitalize()}",
                value=f"<@{interaction.user.id}>\n*{vote.comment or '`No comment provided`'}*",
                inline=False,
            )

        await interaction.message.edit(embed=new_embed)

    @tasks.loop(minutes=1)
    async def process_votes(self):
        with db_session() as session:
            details_list: list[VoteDetails] = (
                session.query(VoteDetails).filter_by(outcome=None).all()
            )
            for details in details_list:
                end_vote = details.planned_end < datetime.utcnow()
                vote_type = self.config.voting[details.vote_type]

                if self.config.bot.dev_mode:
                    end_vote = details.created + timedelta(hours=1) < datetime.utcnow()

                if not vote_type.end_on_threshold and not end_vote:
                    continue

                votes: dict[str, int] = {
                    vote: count
                    for vote, count in (
                        session.query(VoteRecord.vote, func.count(VoteRecord.vote))
                        .filter_by(vote_id=details.vote_id)
                        .group_by(VoteRecord.vote)
                        .all()
                    )
                }

                diff = votes.get("yes", 0) - votes.get("no", 0)

                def accepted():
                    threshold = vote_type.threshold
                    if vote_type.supermajority:
                        match vote_type.group:
                            case "staff":
                                role_id = self.config.permission_roles.staff
                            case "mod":
                                role_id = self.config.permission_roles.moderator
                            case "cet":
                                role_id = self.config.permission_roles.cet
                            case _:
                                role_id = self.config.permission_roles.dark_moderator

                        threshold = (
                            len(
                                self.bot.get_guild(self.config.guilds.main)
                                .get_role(role_id)
                                .members
                            )
                            * 2
                            // 3
                            + 1
                        )
                    elif diff < vote_type.difference:
                        return False
                    if votes.get("yes", 0) < threshold:
                        return False
                    return True

                colour = None
                if accepted():
                    details.outcome = "Accepted"
                    colour = nextcord.Colour.brand_green()
                elif diff <= -1:
                    details.outcome = "Rejected"
                    colour = nextcord.Colour.brand_red()
                elif not end_vote:
                    continue

                details.outcome = details.outcome or "Undecided"
                details.actual_end = datetime.utcnow()
                session.commit()

                self.bot.dispatch(vote_type.action, details)

                message = await get_message_from_url(self.bot, details.vote_url)

                embed = message.embeds[0]
                embed.colour = colour or nextcord.Colour.light_grey()
                embed.add_field(name="Outcome", value=details.outcome, inline=True)
                embed.add_field(
                    name="Vote End",
                    value=f"<t:{int(details.actual_end.timestamp())}:R>",
                    inline=True,
                )

                await message.edit(embed=embed, view=None)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return
        if not interaction.data["custom_id"].startswith("vote"):
            return

        _, vote_id, vote = interaction.data["custom_id"].split(":")
        vote_id = int(vote_id)

        with db_session(interaction.user) as session:
            vote_details: VoteDetails = session.query(VoteDetails).get(vote_id)
            if vote_details is None:
                await interaction.response.send_message(
                    "This vote does not exist", ephemeral=True
                )
                return

            vote_type = self.config.voting[vote_details.vote_type]
            match vote_type.group:
                case "staff":
                    if not await permcheck(interaction, is_staff):
                        return
                case "mod":
                    if not await permcheck(interaction, is_mod):
                        return
                case "cet":
                    if not await permcheck(interaction, is_cet):
                        return
                case _:
                    if not await permcheck(interaction, is_admin):
                        return

            if vote_details.outcome is not None:
                await interaction.response.send_message(
                    "This vote has already been decided", ephemeral=True
                )
                return

            await interaction.response.send_modal(
                BallotModal(
                    vote_type=self.config.voting[vote_details.vote_type],
                    details=vote_details,
                    vote=vote,
                    on_vote=self.record_vote,
                )
            )


class BallotModal(nextcord.ui.Modal):
    def __init__(
        self, vote_type: VoteType, details: VoteDetails, vote: str, on_vote: callable
    ):
        super().__init__(f"{vote_type.name}: {vote}")
        self.vote_type = vote_type
        self.details = details
        self.vote = vote
        self.on_vote = on_vote

        self.comment = nextcord.ui.TextInput(
            label="Comment",
            min_length=8 if vote_type.comment_required else 0,
            max_length=1024,
            required=vote_type.comment_required,
            placeholder="please provide a comment for your vote",
        )
        self.add_item(self.comment)

    async def callback(self, interaction):
        await self.on_vote(
            VoteRecord(
                voter=interaction.user.id,
                vote_id=self.details.vote_id,
                vote=self.vote,
                comment=self.comment.value,
            ),
            interaction,
        )

        await interaction.response.send_message(
            "Your vote has been recorded", ephemeral=True
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Voting(bot, kwargs["config"]))
