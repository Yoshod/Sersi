import nextcord

from nextcord.ext import commands
from nextcord.ui import Button, View
from pytz import timezone
import datetime

from utils.cases.autocomplete import fetch_offences_by_partial_name
from utils.cases.delete import delete_warn
from utils.cases.embed_factory import create_ban_case_embed
from utils.cases.mend import deactivate_warn
from utils.cases.misc import offence_validity_check, deletion_validity_check
from utils.config import Configuration
from utils.cases.fetch import get_case_by_id
from utils.cases.approval import update_approved, update_objected
from utils.database import db_session, BanCase
from utils.perms import (
    is_full_mod,
    permcheck,
    is_mod,
    is_dark_mod,
    is_immune,
    target_eligibility,
    cb_is_compliance,
)
from utils.sersi_embed import SersiEmbed
from utils.review import create_alert
from utils import logs


class BanSystem(commands.Cog):
    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config

    async def cb_approve(self, interaction: nextcord.Interaction):
        new_embed: nextcord.Embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Moderation Action Approved",
            value=interaction.user.mention,
            inline=True,
        )
        new_embed.colour = nextcord.Colour.brand_green()
        await interaction.message.edit(embed=new_embed, view=None)

        update_approved(new_embed.fields[0].value, self.config)

        # Logging
        logging_embed = SersiEmbed(
            title="Moderation Action Approved",
            description="A Moderator Action has been approved by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
            footer="Sersi Moderation Peer Review",
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=logging_embed)

        await logs.update_response(
            self.config, interaction.message, datetime.datetime.now(timezone.utc)
        )

    async def cb_objection(self, interaction: nextcord.Interaction):
        new_embed = interaction.message.embeds[0]
        new_embed.add_field(
            name="Moderation Action Objected To",
            value=interaction.user.mention,
            inline=True,
        )
        new_embed.colour = nextcord.Colour.brand_red()
        await interaction.message.edit(embed=new_embed, view=None)

        update_objected(new_embed.fields[0].value, self.config)

        # Logging
        logging_embed = SersiEmbed(
            title="Moderation Action Objected To",
            description="A Moderator Action has been objected to by a moderator in response to a report.",
            fields={
                "Report:": interaction.message.jump_url,
                "Moderator:": f"{interaction.user.mention} ({interaction.user.id})",
            },
            footer="Sersi Moderation Peer Review",
        )

        channel = self.bot.get_channel(self.config.channels.logging)
        await channel.send(embed=logging_embed)

        await logs.update_response(
            self.config, interaction.message, datetime.now(timezone.utc)
        )

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[977377117895536640, 856262303795380224],
        description="Used to do ban stuff",
    )
    async def ban(self, interaction: nextcord.Interaction):
        pass

    @ban.subcommand(description="Used to ban a user")
    async def add(
        self,
        interaction: nextcord.Interaction,
        offender: nextcord.Member = nextcord.SlashOption(
            name="offender",
            description="The person you wish to warn.",
        ),
        offence: str = nextcord.SlashOption(
            name="offence",
            description="The offence for which the user is being warned.",
        ),
        detail: str = nextcord.SlashOption(
            name="detail",
            description="Details on the offence,",
            min_length=8,
            max_length=1024,
        ),
        ban_type: str = nextcord.SlashOption(
            name="type",
            description="The type of ban",
            choices={
                "Non-Urgent Ban": "non urgent",
                "Urgent Ban": "urgent",
                "Emergency Ban": "emergency",
            },
        ),
    ):
        if not await permcheck(interaction, is_mod):
            return

        if not await permcheck(interaction, is_full_mod) and ban_type == "emergency":
            return

        if ban_type == "emergency":
            await interaction.response.defer()
        else:
            await interaction.response.defer(ephemeral=True)

        if not target_eligibility(interaction.user, offender):
            warning_alert = SersiEmbed(
                title="Unauthorised Moderation Target",
                description=f"{interaction.user.mention} ({interaction.user.id}) attempted to ban {offender.mention} ({offender.id}) despite being outranked!",
            )

            logging_channel = interaction.guild.get_channel(
                self.config.channels.logging
            )

            mega_admin_role = interaction.guild.get_role(
                self.config.permission_roles.dark_moderator
            )

            await logging_channel.send(
                content=f"**ALERT:** {mega_admin_role.mention}", embed=warning_alert
            )

            await interaction.send(
                f"{self.config.emotes.fail} {offender.mention} is a higher level than you. This has been reported.",
                ephemeral=True,
            )
            return

        if is_immune(offender):
            await interaction.send(
                f"{self.config.emotes.fail} {offender.mention} is immune.",
                ephemeral=True,
            )
            return

        if not offence_validity_check(self.config, offence):
            await interaction.send(
                f"{self.config.emotes.fail} {offence} is not in the list of offences. Try again or consider using the 'Other' offence.",
                ephemeral=True,
            )
            return

        case = BanCase(
            offender=offender.id,
            moderator=interaction.user.id,
            offence=offence,
            details=detail,
            type=ban_type,
        )

        match ban_type:
            case "non urgent":
                vote_embed = SersiEmbed(
                    title=f"Non-Urgent Ban Vote: **{offender.name}** ({offender.id})",
                    description=f"A Moderator has requested a Non-Urgent Ban Vote be held for {offender.mention}. As this is a Non-Urgent Ban Vote the user has not been timedout or banned and can still participate in {interaction.guild.name}. The user has **not** been informed of this. Please review the details below carefuly in order to make an accurate decision.",
                    fields={
                        "Moderator": interaction.user.mention,
                        "Offender": offender.mention,
                        "Offence": offence,
                        "Offence Details": detail,
                    },
                )

                alert_channel: nextcord.TextChannel = interaction.guild.get_channel(
                    self.config.channels.alert
                )

                vote_message = nextcord.Message = await alert_channel.send(
                    embed=vote_embed
                )

                approve = Button(
                    label="Approve",
                    style=nextcord.ButtonStyle.grey,
                    custom_id=f"non-urgent-ban-approve:{vote_message.id}",
                )

                object = Button(
                    label="Object",
                    style=nextcord.ButtonStyle.grey,
                    custom_id=f"non-urgent-ban-object:{vote_message.id}",
                )

                override = Button(
                    label="Admin Override",
                    style=nextcord.ButtonStyle.red,
                    custom_id=f"non-urgent-ban-override:{vote_message.id}",
                )

                button_view = View(timeout=10800)
                button_view.add_item(approve)
                button_view.add_item(object)
                button_view.add_item(override)

                vote_message.edit(embed=vote_embed, view=button_view)

                await interaction.followup.send(
                    f"{self.config.emotes.success} The Non-Urgent Ban Vote has been created and can be voted on in {alert_channel.mention}. The unique identifier for this case is `{case.id}`."
                )

            case "urgent":
                vote_embed = SersiEmbed(
                    title=f"Urgent Ban Vote: **{offender.name}** ({offender.id})",
                    description=f"A Moderator has requested an Urgent Ban Vote be held for {offender.mention}. As this is an Urgent Ban Vote the user has been timedout and cannot participate in {interaction.guild.name}. The user has been informed they are timed out, but not why. Please review the details below carefuly in order to make an accurate decision.",
                    fields={
                        "Moderator": interaction.user.mention,
                        "Offender": offender.mention,
                        "Offence": offence,
                        "Offence Details": detail,
                    },
                )

                alert_channel: nextcord.TextChannel = interaction.guild.get_channel(
                    self.config.channels.alert
                )

                vote_message = nextcord.Message = await alert_channel.send(
                    embed=vote_embed
                )

                approve = Button(
                    label="Approve",
                    style=nextcord.ButtonStyle.grey,
                    custom_id=f"urgent-ban-approve:{case.id}",
                )

                object = Button(
                    label="Object",
                    style=nextcord.ButtonStyle.grey,
                    custom_id=f"urgent-ban-object:{case.id}",
                )

                override = Button(
                    label="Admin Override",
                    style=nextcord.ButtonStyle.red,
                    custom_id=f"urgent-ban-override:{case.id}",
                )

                button_view = View(timeout=10800)
                button_view.add_item(approve)
                button_view.add_item(object)
                button_view.add_item(override)

                vote_message.edit(embed=vote_embed, view=button_view)

                await offender.timeout(
                    datetime.timedelta(minutes=720),
                    reason=f"[{offence}: {detail}] - {interaction.user}",
                )

                await interaction.followup.send(
                    f"{self.config.emotes.success} The Urgent Ban Vote has been created and can be voted on in {alert_channel.mention}. The unique identifier for this case is `{case.id}`."
                )

            case "emergency":
                pass
        
        with db_session(interaction.user) as session:
            session.add(case)
            session.commit()

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        try:
            btn_id = interaction.data["custom_id"]
        except KeyError:
            return

        await interaction.response.defer(True)

        match btn_id.split(":", 1):
            case ["non-urgent-ban-approve", uuid]:
                for field in interaction.message.embeds[0].fields:
                    if field.value.splitlines()[0] == interaction.user.mention:
                        await interaction.followup.send(
                            "You already voted", ephemeral=True
                        )
                        return

                new_embed = interaction.message.embeds[0]
                new_embed.add_field(
                    name="Voted Yes:",
                    value=f"{interaction.user.mention}\n*{interaction.data['components'][0]['components'][0]['value']}*",
                    inline=True,
                )
                yes_votes = new_embed.description[-1]
                yes_votes = int(yes_votes) + 1

                new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
                await interaction.message.edit(embed=new_embed)

                if yes_votes >= 3:
                    await interaction.message.edit(view=None)

                    yes_men = []
                    for field in new_embed.fields:
                        if field.name == "Voted Yes:":
                            yes_men.append(field.value)

                    yes_list = "\n• ".join(yes_men)

                    sersi_case = get_case_by_id(self.config, uuid, False)

                    offender: nextcord.Member = interaction.guild.get_member(
                        sersi_case["Offender ID"]
                    )

                    ban_embed = create_ban_case_embed(sersi_case, interaction)

                    try:
                        await offender.send(
                            embed=SersiEmbed(
                                title=f"You have been banned in {interaction.guild.name}!",
                                description=f"You have been banned in {interaction.guild.name}. The details about the ban are "
                                "below. If you would like to appeal your ban you can do so:\n"
                                "https://appeals.wickbot.com",
                                fields={
                                    "Offence:": f"`{sersi_case['Offence']}`",
                                    "Detail:": f"`{sersi_case['Details']}`",
                                },
                                footer="Sersi Ban",
                            ).set_thumbnail(interaction.guild.icon.url)
                        )
                        not_sent = False

                    except (nextcord.Forbidden, nextcord.HTTPException):
                        not_sent = True

                    # To do:
                    # Create the embed that confirms the user has been banned
                    # Log the ban
                    # Idk I'm tired

                    await offender.ban(reason="Lol get fucked")
