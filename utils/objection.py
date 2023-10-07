import datetime

import nextcord

from utils import logs
from utils.config import Configuration
from utils.perms import (
    permcheck,
    is_compliance,
    is_dark_mod,
    is_senior_mod,
    is_full_mod,
)
from utils.sersi_embed import SersiEmbed


class ObjectionButton(nextcord.ui.Button):
    def __init__(self, config: Configuration):
        super().__init__(label="Object", style=nextcord.ButtonStyle.red)
        self.config = config

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
        # update_objected(new_embed.fields[0].value, self.config)

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

        await logs.update_response(
            self.config,
            interaction.message,
            datetime.datetime.now(datetime.timezone.utc),
        )


class ApprovalButton(nextcord.ui.Button):
    def __init__(self, config: Configuration):
        super().__init__(label="Approve", style=nextcord.ButtonStyle.green)
        self.config = config

    async def callback(self, interaction: nextcord.Interaction) -> None:
        new_embed: nextcord.Embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Moderation Action Approved",
            value=interaction.user.mention,
            inline=True,
        )
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        # update_approved(new_embed.fields[0].value, self.config)

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

        await logs.update_response(
            self.config,
            interaction.message,
            datetime.datetime.now(datetime.timezone.utc),
        )


class AlertView(nextcord.ui.View):
    def __init__(self, config: Configuration, reviewer: nextcord.Role):
        super().__init__(timeout=None)
        self.config = config
        self.reviewer = reviewer
        self.add_item(ApprovalButton(config))
        self.add_item(ObjectionButton(config))

    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        match self.reviewer.id:
            case self.config.permission_roles.compliance:
                return await permcheck(interaction, is_compliance)
            case self.config.permission_roles.dark_moderator:
                return await permcheck(interaction, is_dark_mod)
            case self.config.permission_roles.senior_moderator:
                return await permcheck(interaction, is_senior_mod)
            case self.config.permission_roles.moderator:
                return await permcheck(interaction, is_full_mod)
            case _:
                return False
