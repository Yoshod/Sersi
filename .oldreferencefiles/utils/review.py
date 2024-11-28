import nextcord

from utils.config import Configuration
from utils.database import Case


def highest_mod_role(moderator: nextcord.Member, config: Configuration):
    role_list: list[int] = [
        config.roles.staff.admin,
        config.roles.staff.mod_lead,
        config.roles.staff.mod,
        config.roles.staff.trial_mod,
    ]

    for role in moderator.roles[::-1]:
        if role.id in role_list:
            return role.id

    return 0


def determine_reviewer(moderator: nextcord.Member, config: Configuration):
    review_relations: dict[int:int] = {
        config.roles.staff.trial_mod: config.roles.staff.mod,
        config.roles.staff.mod: config.roles.staff.mod_lead,
        config.roles.staff.mod_lead: config.roles.staff.admin,
        config.roles.staff.admin: config.roles.staff.admin,
    }

    mod_role = highest_mod_role(moderator, config)

    return review_relations[mod_role]


def create_alert(
    moderator: nextcord.Member,
    config: Configuration,
    review_embed: nextcord.Embed,
    case: Case,
    url: str,
):
    reviewer = determine_reviewer(moderator, config)

    match reviewer:
        case config.roles.staff.compliance:
            review_channel = moderator.guild.get_channel(
                config.channels.staff.compliance_review
            )
            reviewer_role = moderator.guild.get_role(reviewer)
            reviewed_role = moderator.guild.get_role(
                config.roles.staff.admin
            )

        case config.roles.staff.admin:
            review_channel = moderator.guild.get_channel(
                config.channels.staff.admin_review
            )

            reviewer_role = moderator.guild.get_role(reviewer)

            mod_role = highest_mod_role(moderator, config)

            if mod_role == config.roles.staff.admin:
                reviewed_role = moderator.guild.get_role(
                    config.roles.staff.admin
                )
            else:
                reviewed_role = moderator.guild.get_role(
                    config.roles.staff.mod_lead
                )

        case config.roles.staff.mod_lead:
            review_channel = moderator.guild.get_channel(
                config.channels.staff.mod_lead_review
            )
            reviewer_role = moderator.guild.get_role(reviewer)
            reviewed_role = moderator.guild.get_role(config.roles.staff.mod)

        case config.roles.staff.mod:
            review_channel = moderator.guild.get_channel(
                config.channels.staff.mod_review
            )
            reviewer_role = moderator.guild.get_role(reviewer)
            reviewed_role = moderator.guild.get_role(
                config.roles.staff.trial_mod
            )

    review_embed.title = f"{reviewed_role.name} {case.type} Case"
    review_embed.add_field(name="Jump URL:", value=f"[Jump!]({url})")

    return reviewer_role, reviewed_role, review_embed, review_channel
