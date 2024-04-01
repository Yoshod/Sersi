import nextcord
from utils.base import encode_button_id, encode_snowflake
from utils.config import Configuration
from utils.database import (
    WarningCase,
    db_session,
    VoteDetails,
    BanCase,
    BlacklistCase,
    Note,
)
from utils.sersi_embed import SersiEmbed
from utils.staff import StaffDataButton, ModerationDataButton, determine_staff_member


class WhoisCasesButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="Cases",
            custom_id=encode_button_id("cases", user=encode_snowflake(user_id)),
            disabled=False,
        )


class WhoisNotesButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="Notes",
            custom_id=encode_button_id("notes", user=encode_snowflake(user_id)),
            disabled=False,
        )


class WhoisWarningsButton(nextcord.ui.Button):
    def __init__(self, user_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="Warnings",
            custom_id=encode_button_id(
                "cases", user=encode_snowflake(user_id), type="Warning"
            ),
            disabled=False,
        )


class WhoisView(nextcord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(WhoisCasesButton(user_id))
        self.add_item(WhoisNotesButton(user_id))
        self.add_item(WhoisWarningsButton(user_id))

        if determine_staff_member(user_id):
            self.add_item(StaffDataButton(user_id))
            self.add_item(ModerationDataButton(user_id))


def _get_user_ban(user_id: int) -> BanCase | None:
    with db_session() as session:
        ban_case = (
            session.query(BanCase).filter_by(offender=user_id, active=True).first()
        )

    return ban_case


async def create_whois_embed(
    config: Configuration, interaction: nextcord.Interaction, user: nextcord.Member
) -> SersiEmbed:
    with db_session(interaction.user) as session:
        user_warns = (
            session.query(WarningCase).filter_by(offender=user.id, active=True).count()
        )

        ban_vote = (
            session.query(VoteDetails)
            .filter_by(vote_type="urgent-ban", outcome=None)
            .filter(VoteDetails.case.has(offender=user.id))
            .first()
        )

        blacklists = (
            session.query(BlacklistCase).filter_by(offender=user.id, active=True).all()
        )

        user_notes = session.query(Note).filter_by(member=user.id).count()

    try:
        if user.communication_disabled_until:
            timeout_string = f"**Timeout**: {config.emotes.success} <t:{int(user.communication_disabled_until.timestamp())}:R>\n"

        else:
            timeout_string = f"**Timeout**: {config.emotes.fail}\n"

        guild_member = True

    except AttributeError:
        ban_case = _get_user_ban(user.id)

        if not ban_case:
            guild_bans = await interaction.guild.bans().flatten()

            timeout_string = None

            for ban in guild_bans:
                if ban.user.id == user.id:
                    timeout_string = f"**User Banned**: {config.emotes.success} `Non Sersi Ban: {ban.reason}`\n"
                    break

            if not timeout_string:
                timeout_string = f"**User Banned**: {config.emotes.fail}\n"

        else:
            timeout_string = f"**User Banned**: {config.emotes.success} `{ban_case.id}` (<t:{int(ban_case.created.timestamp())}:R>)\n"

        guild_member = False

    blacklists_string = ""
    if blacklists:
        blacklists_string = (
            f"{config.emotes.blank}**Blacklisted from**: "
            + ", ".join([f"`{blacklist.blacklist}`" for blacklist in blacklists])
            + "\n"
        )

    if guild_member:
        whois_embed = SersiEmbed(
            title=f"Whois {user.display_name}?",
            fields={
                "General Information": f"{config.emotes.blank}**Username**: {user.name}\n{config.emotes.blank}**Global Name**: {user.global_name}\n{config.emotes.blank}**Nickname**: {user.nick}\n{config.emotes.blank}**User ID**: {user.id}\n{config.emotes.blank}**Mention**: {user.mention}\n{config.emotes.blank}**Creation Date**: <t:{int(user.created_at.timestamp())}:R>\n{config.emotes.blank}**Join Date**: <t:{int(user.joined_at.timestamp())}:R>",
                "Sersi Information": f"{config.emotes.blank}**Active Warns**: {user_warns}\n{config.emotes.blank}**Notes**: {user_notes}\n{config.emotes.blank}**Ban Vote**: {config.emotes.success if ban_vote else config.emotes.fail}\n{config.emotes.blank}{timeout_string}{blacklists_string}",
            },
        )
        whois_embed.set_footer(text="Sersi Whois - Server Member")
        whois_embed.set_thumbnail(url=user.display_avatar.url)

    else:
        whois_embed = SersiEmbed(
            title=f"Whois {user.display_name}?",
            fields={
                "General Information": f"{config.emotes.blank}**Username**: {user.name}\n{config.emotes.blank}**Global Name**: {user.global_name}\n{config.emotes.blank}**User ID**: {user.id}\n{config.emotes.blank}**Creation Date**: <t:{int(user.created_at.timestamp())}:R>",
                "Sersi Information": f"{config.emotes.blank}**Active Warns**: {user_warns}\n{config.emotes.blank}**Notes**: {user_notes}\n{timeout_string}{blacklists_string}",
            },
        )
        whois_embed.set_footer(text="Sersi Whois - Not a Server Member")
        whois_embed.set_thumbnail(url=user.display_avatar.url)

    return whois_embed
