import nextcord

from utils.alerts import add_response_time
from utils.config import Configuration
from utils.database import db_session, PeerReview, Case
from utils.perms import (
    permcheck,
    is_compliance,
    is_admin,
    is_mod_lead,
    is_full_mod,
)
from utils.sersi_embed import SersiEmbed


class ObjectionButton(nextcord.ui.Button):
    def __init__(self, config: Configuration, sersi_case: Case):
        super().__init__(label="Object", style=nextcord.ButtonStyle.red)
        self.config = config
        self.sersi_case = sersi_case

    async def callback(self, interaction: nextcord.Interaction) -> None:
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Moderation Action Objected To",
            value=interaction.user.mention,
            inline=True,
        )
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)

        # Database
        review_case = PeerReview(
            case_id=self.sersi_case.id,
            reviewer=interaction.user.id,
            review_outcome="Objection",
        )

        with db_session(interaction.user) as session:
            session.add(review_case)
            session.commit()

            review_case = session.query(PeerReview).filter_by(id=review_case.id).first()

        # Logging
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Moderation Action Objected To",
                description="A Moderator Action has been objected to by a moderator in response to a report.",
                fields={
                    "Report:": interaction.message.jump_url,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                },
                footer="Sersi Moderation Peer Review",
            )
        )

        add_response_time(interaction.message)


class ApprovalButton(nextcord.ui.Button):
    def __init__(self, config: Configuration, sersi_case: Case):
        super().__init__(label="Approve", style=nextcord.ButtonStyle.green)
        self.config = config
        self.sersi_case = sersi_case

    async def callback(self, interaction: nextcord.Interaction) -> None:
        new_embed: nextcord.Embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Moderation Action Approved",
            value=interaction.user.mention,
            inline=True,
        )
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # Database
        review_case = PeerReview(
            case_id=self.sersi_case.id,
            reviewer=interaction.user.id,
            review_outcome="Approved",
        )

        with db_session(interaction.user) as session:
            session.add(review_case)
            session.commit()

            review_case = session.query(PeerReview).filter_by(id=review_case.id).first()

        # Logging
        await interaction.guild.get_channel(self.config.channels.logging).send(
            embed=SersiEmbed(
                title="Moderation Action Approved",
                description="A Moderator Action has been approved by a moderator in response to a report.",
                fields={
                    "Report:": interaction.message.jump_url,
                    "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
                },
                footer="Sersi Moderation Peer Review",
            )
        )

        add_response_time(interaction.message)


class AlertView(nextcord.ui.View):
    def __init__(
        self, config: Configuration, reviewer: nextcord.Role, sersi_case: Case
    ):
        super().__init__(timeout=None)
        self.config = config
        self.reviewer = reviewer
        self.add_item(ApprovalButton(config, sersi_case))
        self.add_item(ObjectionButton(config, sersi_case))

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        match self.reviewer.id:
            case self.config.permission_roles.compliance:
                return await permcheck(interaction, is_compliance)
            case self.config.permission_roles.dark_moderator:
                return await permcheck(interaction, is_admin)
            case self.config.permission_roles.senior_moderator:
                return await permcheck(interaction, is_mod_lead)
            case self.config.permission_roles.moderator:
                return await permcheck(interaction, is_full_mod)
            case _:
                return False
