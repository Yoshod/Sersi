import nextcord
from utils.base import SersiEmbed
from utils.config import Configuration
from utils.database import BanCase, WarningCase, db_session


class WhoisCasesButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="Cases",
            custom_id=f"whois-cases:{user_id}",
            disabled=False,
        )


class WhoisNotesButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="Notes",
            custom_id=f"whois-notes:{user_id}",
            disabled=False,
        )


class WhoisView(nextcord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(WhoisCasesButton(user_id))
        self.add_item(WhoisNotesButton(user_id))


def create_whois_embed(
    config: Configuration, interaction: nextcord.Interaction, user: nextcord.Member
) -> SersiEmbed:
    with db_session(interaction.user) as session:
        user_warns = (
            session.query(WarningCase).filter_by(offender=user.id, active=True).count()
        )

        ban_cases = (
            session.query(BanCase)
            .filter_by(offender=user.id, ban_type="urgent", active=None)
            .first()
        )

        if ban_cases:
            ban_vote = True

        else:
            ban_vote = False

    if user.communication_disabled_until:
        timeout_string = f"**Timeout**: {config.emotes.success} <t:{int(user.communication_disabled_until.timestamp())}:R>"

    else:
        timeout_string = f"**Timeout**: {config.emotes.fail}"

    whois_embed = SersiEmbed(
        title=f"Whois {user.display_name}?",
        fields={
            "General Information": f"{config.emotes.blank}**Username**: {user.name}\n{config.emotes.blank}**Global Name**: {user.global_name}\n{config.emotes.blank}**Nickname**: {user.nick}\n{config.emotes.blank}**User ID**: {user.id}\n{config.emotes.blank}**Mention**: {user.mention}\n{config.emotes.blank}**Creation Date**: <t:{int(user.created_at.timestamp())}:R>\n{config.emotes.blank}**Join Date**: <t:{int(user.joined_at.timestamp())}:R>",
            "Sersi Information": f"{config.emotes.blank}**Active Warns**: {user_warns}\n{config.emotes.blank}**Ban Vote**: {config.emotes.success if ban_vote else config.emotes.fail}\n{config.emotes.blank}{timeout_string}",
        },
    )
    whois_embed.set_footer(text="Sersi Whois")
    whois_embed.set_thumbnail(url=user.display_avatar.url)

    return whois_embed
