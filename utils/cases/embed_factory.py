import nextcord

from utils.base import SersiEmbed
from utils.config import Configuration


def create_scrubbed_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(
        name="Type:", value=f"`{sersi_case['Case Type']}`", inline=True
    )

    scrubber = interaction.guild.get_member(sersi_case["Scrubber ID"])

    if not scrubber:
        case_embed.add_field(
            name="Scrubber:",
            value=f"`{sersi_case['Scrubber ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Scrubber ID:",
            value=f"{scrubber.mention}",
            inline=True,
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=False,
        )

    else:
        case_embed.add_field(
            name="Offender:", value=f"{offender.mention}", inline=False
        )
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Reason:", value=sersi_case["Scrub Reason"], inline=False)

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_slur_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Slur Usage`", inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Slur Used:", value=sersi_case["Slur Used"], inline=False)

    case_embed.add_field(
        name="Report URL:", value=sersi_case["Report URL"], inline=False
    )

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_reformation_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Reformation`", inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Reason:", value=sersi_case["Reason"], inline=False)
    reformation_channel = interaction.client.get_channel(sersi_case["Channel ID"])

    if not reformation_channel:
        case_embed.add_field(
            name="Reformation Channel:",
            value="Channel No Longer Exists",
            inline=False,
        )
    else:
        case_embed.add_field(
            name="Reformation Channel:",
            value=reformation_channel.mention,
            inline=False,
        )

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_probation_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Probation`", inline=True)

    initial_moderator = interaction.guild.get_member(sersi_case["Initial Moderator ID"])

    if not initial_moderator:
        case_embed.add_field(
            name="Initial Moderator:",
            value=f"`{sersi_case['Initial Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Initial Moderator:",
            value=f"{initial_moderator.mention}",
            inline=True,
        )

    approving_moderator = interaction.guild.get_member(
        sersi_case["Approving Moderator ID"]
    )

    if not approving_moderator:
        case_embed.add_field(
            name="Approving Moderator:",
            value=f"`{sersi_case['Approving Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Approving Moderator:",
            value=f"{approving_moderator.mention}",
            inline=True,
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=False,
        )

    else:
        case_embed.add_field(
            name="Offender:", value=f"{offender.mention}", inline=False
        )
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Reason:", value=sersi_case["Reason"], inline=False)

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_bad_faith_ping_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Bad Faith Ping`", inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(
        name="Report URL:", value=sersi_case["Report URL"], inline=False
    )

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_warn_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Warn`", inline=True)

    if sersi_case["Active"]:
        active_emote = Configuration.from_yaml_file(
            "./persistent_data/config.yaml"
        ).emotes.success

    else:
        active_emote = Configuration.from_yaml_file(
            "./persistent_data/config.yaml"
        ).emotes.fail

    case_embed.add_field(name="Active:", value=active_emote, inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Offence:", value=sersi_case["Offence"], inline=False)

    case_embed.add_field(
        name="Offence Details:", value=sersi_case["Offence Details"], inline=False
    )

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed


def create_kick_case_embed(
    sersi_case: dict, interaction: nextcord.Interaction
) -> SersiEmbed:
    case_embed = SersiEmbed()
    case_embed.add_field(name="Case:", value=f"`{sersi_case['ID']}`", inline=True)
    case_embed.add_field(name="Type:", value="`Kick`", inline=True)

    moderator = interaction.guild.get_member(sersi_case["Moderator ID"])

    if not moderator:
        case_embed.add_field(
            name="Moderator:",
            value=f"`{sersi_case['Moderator ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(
            name="Moderator:", value=f"{moderator.mention}", inline=True
        )

    offender = interaction.guild.get_member(sersi_case["Offender ID"])

    if not offender:
        case_embed.add_field(
            name="Offender:",
            value=f"`{sersi_case['Offender ID']}`",
            inline=True,
        )

    else:
        case_embed.add_field(name="Offender:", value=f"{offender.mention}", inline=True)
        case_embed.set_thumbnail(url=offender.display_avatar.url)

    case_embed.add_field(name="Reason:", value=sersi_case["Reason"], inline=False)

    case_embed.add_field(
        name="Timestamp:",
        value=f"<t:{sersi_case['Timestamp']}:R>",
        inline=True,
    )

    case_embed.set_footer(text="Sersi Case Tracking")

    return case_embed
