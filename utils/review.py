import nextcord

from utils.config import Configuration
from utils.database import Case


def highest_mod_role(moderator: nextcord.Member, config: Configuration):
    role_list: list[int] = [
        config.permission_roles.dark_moderator,
        config.permission_roles.senior_moderator,
        config.permission_roles.moderator,
        config.permission_roles.trial_moderator,
    ]

    for role in moderator.roles[::-1]:
        if role.id in role_list:
            return role.id

    return 0


def determine_reviewer(moderator: nextcord.Member, config: Configuration):
    review_relations: dict[int:int] = {
        config.permission_roles.trial_moderator: config.permission_roles.moderator,
        config.permission_roles.moderator: config.permission_roles.senior_moderator,
        config.permission_roles.senior_moderator: config.permission_roles.dark_moderator,
        config.permission_roles.dark_moderator: config.permission_roles.compliance,
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
        case config.permission_roles.compliance:
            review_channel = moderator.guild.get_channel(
                config.channels.compliance_review
            )
            reviewer_role = moderator.guild.get_role(reviewer)
            reviewed_role = moderator.guild.get_role(
                config.permission_roles.dark_moderator
            )

        case config.permission_roles.dark_moderator:
            review_channel = moderator.guild.get_channel(
                config.channels.dark_mod_review
            )
            reviewer_role = moderator.guild.get_role(reviewer)
            reviewed_role = moderator.guild.get_role(
                config.permission_roles.senior_moderator
            )

        case config.permission_roles.senior_moderator:
            review_channel = moderator.guild.get_channel(
                config.channels.senior_mod_review
            )
            reviewer_role = moderator.guild.get_role(reviewer)
            reviewed_role = moderator.guild.get_role(config.permission_roles.moderator)

        case config.permission_roles.moderator:
            review_channel = moderator.guild.get_channel(
                config.channels.moderator_review
            )
            reviewer_role = moderator.guild.get_role(reviewer)
            reviewed_role = moderator.guild.get_role(
                config.permission_roles.trial_moderator
            )

    review_embed.title = f"{reviewed_role.name} {case.type} Case"
    review_embed.add_field(name="Jump URL:", value=f"[Jump!]({url})")

    return reviewer_role, reviewed_role, review_embed, review_channel
