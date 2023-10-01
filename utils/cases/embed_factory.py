from typing import Type

import nextcord

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.database import (
    Case,
    BanCase,
    BadFaithPingCase,
    KickCase,
    ProbationCase,
    ReformationCase,
    SlurUsageCase,
    TimeoutCase,
    WarningCase,
)


def create_case_embed(
        case: Type[Case],
        interaction: nextcord.Interaction,
        config: Configuration,
) -> SersiEmbed:
    fields = {
        "Case": f"`{case.id}`",
        "Type": f"`{case.type}`",
        "Moderator": f"<@{case.moderator}> `{case.moderator}`",
        "Offender": f"<@{case.offender}> `{case.offender}`",
    }

    match case:
        case BanCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Ban Type": f"`{case.ban_type}`",
                "Active": config.emotes.success if case.active else config.emotes.fail
            })
            if not case.active:
                fields["Unban Reason"] = f"`{case.unban_reason}`"
        case BadFaithPingCase():
            fields["Report URL"] = case.report_url
        case KickCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
            })
        case ProbationCase():
            fields.update({
                "Reason": f"`{case.reason}`",
                "Active": config.emotes.success if case.active else config.emotes.fail
            })
        case ReformationCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Case Number": f"`{case.case_number}`",
                "Cell Channel": f"<#{case.cell_channel}>",
                "State": f"`{case.state}`"
            })
        case SlurUsageCase():
            fields.update({
                "Slur Used": f"`{case.slur_used}`",
                "Report URL": case.report_url
            })
        case TimeoutCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Muted Until": f"<t:{case.planned_end}:R>"
            })
        case WarningCase():
            fields.update({
                "Offence": f"`{case.offence}`",
                "Details": f"`{case.details}`",
                "Active": config.emotes.success if case.active else config.emotes.fail,
                "Deactivate Reason": f"`{case.deactivate_reason}`",
            })
        
    
    fields["Timestamp"] = f"<t:{case.created}:R>"

    offender = interaction.guild.get_member(case.offender)

    return SersiEmbed(
        fields=fields,
        thumbnail_url=offender.display_avatar.url if offender else None,
        footer_text="Sersi Case Tracking"
    )
