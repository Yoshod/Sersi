import json
import pickle
import nextcord
import io
from chat_exporter import export
from dataclasses import dataclass, asdict
from baseutils import SersiEmbed
from nextcord.ui import View, Button, Select
import configutils


@dataclass(kw_only=True)
class TicketIterations():
    mod_tickets: int
    senior_tickets: int
    admin_tickets: int
    verification_tickets: int


def ticket_check(config: configutils.Configuration, id, ticket_type):
    try:
        with open(config.datafiles.ticketers, "rb") as f:
            ticketers = pickle.load(f)

    except FileNotFoundError:
        ticketers = {
            "mod tickets": [],
            "senior tickets": [],
            "admin tickets": [],
            "verification tickets": []
        }

    match ticket_type:
        case "mod_ticket":
            if id in ticketers["mod tickets"]:
                return False

            else:
                ticketers["mod tickets"].append(id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)
                return True

        case "senior_ticket":
            if id in ticketers["senior tickets"]:
                return False

            else:
                ticketers["senior tickets"].append(id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)
                return True

        case "admin_ticket":
            if id in ticketers["admin tickets"]:
                return False

            else:
                ticketers["admin tickets"].append(id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)
                return True

        case "verification_ticket":
            if id in ticketers["verification tickets"]:
                return False

            else:
                ticketers["verification tickets"].append(id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)
                return True


def ticket_prep(config: configutils.Configuration, interaction, user, ticket_type):
    overwrites = {
        interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
        interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True),
        user: nextcord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
            create_public_threads=False,
            create_private_threads=False,
            external_stickers=True,
            embed_links=True,
            attach_files=True,
            use_external_emojis=True
        )
    }

    with open("files/Tickets/ticketiters.json", "r", encoding="utf-8") as f:
        iters = json.load(f)
        ticket_counts = TicketIterations(
            mod_tickets=iters["mod_tickets"],
            senior_tickets=iters["senior_tickets"],
            admin_tickets=iters["admin_tickets"],
            verification_tickets=iters["verification_tickets"])

    match ticket_type:
        case "mod_ticket":
            overwrites.update({interaction.guild.get_role(config.permission_roles.moderator): nextcord.PermissionOverwrite(read_messages=True)})
            overwrites.update({interaction.guild.get_role(config.permission_roles.trial_moderator): nextcord.PermissionOverwrite(read_messages=True)})
            ticket_counts.mod_tickets = int(ticket_counts.mod_tickets) + 1

            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            case_name = (f"mod-ticket-{str(ticket_counts.mod_tickets).zfill(4)}")

            return overwrites, case_name

        case "senior_ticket":
            overwrites.update({interaction.guild.get_role(config.permission_roles.senior_moderator): nextcord.PermissionOverwrite(read_messages=True)})
            ticket_counts.senior_tickets = int(ticket_counts.senior_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            case_name = (f"senior-ticket-{str(ticket_counts.senior_tickets).zfill(4)}")

            return overwrites, case_name

        case "admin_ticket":
            ticket_counts.admin_tickets = int(ticket_counts.admin_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            case_name = (f"admin-ticket-{str(ticket_counts.admin_tickets).zfill(4)}")

            return overwrites, case_name

        case "verification_ticket":
            ticket_counts.verification_tickets = int(ticket_counts.verification_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            overwrites.update({interaction.guild.get_role(config.permission_roles.ticket_support): nextcord.PermissionOverwrite(read_messages=True)})

            case_name = (f"verification-ticket-{str(ticket_counts.verification_tickets).zfill(4)}")
            return overwrites, case_name


async def ticket_close(config: configutils.Configuration, interaction, user, ticket_type):
    try:
        with open(config.datafiles.ticketers, "rb") as f:
            ticketers = pickle.load(f)

    except FileNotFoundError:
        ticketers = {
            "mod tickets": [],
            "senior tickets": [],
            "admin tickets": [],
            "verification tickets": []
        }
    channel = interaction.channel

    match ticket_type:
        case "mod_ticket":
            output_channel = interaction.guild.get_channel(config.channels.mod_ticket_logs)
            if user.id in ticketers["mod tickets"]:
                ticketers["mod tickets"].remove(user.id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

        case "senior_ticket":
            output_channel = interaction.guild.get_channel(config.channels.senior_ticket_logs)
            if user.id in ticketers["senior tickets"]:
                ticketers["senior tickets"].remove(user.id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

        case "admin_ticket":
            output_channel = interaction.guild.get_channel(config.channels.admin_ticket_logs)
            if user.id in ticketers["admin tickets"]:
                ticketers["admin tickets"].remove(user.id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

        case "verification_ticket":
            output_channel = interaction.guild.get_channel(config.channels.verification_ticket_logs)
            if user.id in ticketers["verification tickets"]:
                ticketers["verification tickets"].remove(user.id)
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

    transcript = await export(channel, military_time=True)
    if transcript is None:
        await output_channel.send(f"{config.emotes.fail} Failed to Generate Transcript!")

    else:
        transcript_file = nextcord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{channel.name}.html",
        )

        log_embed = nextcord.Embed(
            title=f"{channel.name} Transcript",
            description=f"{channel.name} has been archived.",
            color=nextcord.Color.from_rgb(237, 91, 6))

        await output_channel.send(embed=log_embed, file=transcript_file)

        # DO NOT DELETE
        # For some reason you cannot send a transcript twice so it has to be remade each time it is to be re-sent
        transcript_file = nextcord.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{channel.name}.html",
        )

        try:
            await user.send(embed=log_embed, file=transcript_file)
        except nextcord.errors.Forbidden:
            pass


async def escalation_change(config: configutils.Configuration, interaction: nextcord.Interaction, user: nextcord.User, current_ticket_type, requested_ticket_type, reason, client: nextcord.Client):
    overwrites = {
        interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
        interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True)
    }
    ticket_types = [current_ticket_type, requested_ticket_type]

    with open("files/Tickets/ticketiters.json", "r", encoding="utf-8") as f:
        iters = json.load(f)
        ticket_counts = TicketIterations(
            mod_tickets=iters["mod_tickets"],
            senior_tickets=iters["senior_tickets"],
            admin_tickets=iters["admin_tickets"],
            verification_tickets=iters["verification_tickets"])

        print(ticket_types)

    match ticket_types:
        case ["mod_ticket", "Senior Moderator Ticket"]:
            overwrites.update({interaction.guild.get_role(config.permission_roles.senior_moderator): nextcord.PermissionOverwrite(read_messages=True)})

            ticket_counts.senior_tickets = int(ticket_counts.senior_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)
            case_name = (f"senior-ticket-{str(ticket_counts.senior_tickets).zfill(4)}")

            try:
                with open(config.datafiles.ticketers, "rb") as f:
                    ticketers = pickle.load(f)
            except FileNotFoundError:
                ticketers = {
                    "mod tickets": [],
                    "senior tickets": [],
                    "admin tickets": [],
                    "verification tickets": []
                }

            try:
                initial_embed = interaction.message.embeds[0]
            except IndexError:
                raise Exception("Could not find embed when attempting to escalate ticket! Index out of range!")

            complainer_id = initial_embed.description[2:21]
            if str(complainer_id)[0] == "!":
                complainer_id = initial_embed.description[3:21]

            complainer_id = int(complainer_id)

            try:
                complainer = client.get_user(complainer_id)
                user = complainer
            except ValueError:
                raise Exception("Could not translate user ID into user")

            if user.id in ticketers["mod tickets"]:
                ticketers["mod tickets"].remove(complainer.id)
                ticketers["senior tickets"].append(str(complainer.id))
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

            overwrites.update({complainer: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=True, embed_links=True, attach_files=True, use_external_emojis=True)})

            await interaction.channel.edit(name=case_name, overwrites=overwrites)

            escalation_embed = SersiEmbed(
                title="Ticket Escalation Level Changed",
                description="This ticket has undergone a change in escalation level.",
                footer=(interaction.user.name, interaction.user.display_avatar.url),
                fields={
                    "Previous Escalation Level:": "Moderator Ticket",
                    "Current Escalation Level:": "Senior Moderator Ticket",
                    "Escalation Notes:": reason
                }
            )

            escalation_embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=escalation_embed)

            close_bttn = Button(custom_id=f"senior-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

            select_options = [
                nextcord.SelectOption(label="Moderator Ticket", description="Change escalation level to: Moderator"),
                nextcord.SelectOption(label="Senior Moderator Ticket", description="Change escalation level to: Senior Moderator"),
                nextcord.SelectOption(label="Administrator Ticket", description="Change escalation level to: Administrator")
            ]
            escalation_dropdown = Select(custom_id=f"senior-ticket-escalation:{user.id}", options=select_options, min_values=1, max_values=1, placeholder="Escalation Options")

            button_view = View(auto_defer=False)
            button_view.add_item(escalation_dropdown)
            button_view.add_item(close_bttn)

            await interaction.message.edit(view=button_view)

        case ["mod_ticket", "Administrator Ticket"]:
            ticket_counts.admin_tickets = int(ticket_counts.admin_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)
            case_name = (f"admin-ticket-{str(ticket_counts.admin_tickets).zfill(4)}")
            print(1)
            try:
                with open(config.datafiles.ticketers, "rb") as f:
                    ticketers = pickle.load(f)
            except FileNotFoundError:
                ticketers = {
                    "mod tickets": [],
                    "senior tickets": [],
                    "admin tickets": [],
                    "verification tickets": []
                }

            try:
                initial_embed = interaction.message.embeds[0]
            except IndexError:
                raise Exception("Could not find embed when attempting to escalate ticket! Index out of range!")

            complainer_id = initial_embed.description[2:21]
            if str(complainer_id)[0] == "!":
                complainer_id = initial_embed.description[3:21]

            complainer_id = int(complainer_id)

            try:
                complainer = client.get_user(complainer_id)
                user = complainer
            except ValueError:
                raise Exception("Could not translate user ID into user")

            if user.id in ticketers["mod tickets"]:
                ticketers["mod tickets"].remove(complainer.id)
                ticketers["admin tickets"].append(str(complainer.id))
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

            overwrites.update({complainer: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=True, embed_links=True, attach_files=True, use_external_emojis=True)})

            await interaction.channel.edit(name=case_name, overwrites=overwrites)

            escalation_embed = SersiEmbed(
                title="Ticket Escalation Level Changed",
                description="This ticket has undergone a change in escalation level.",
                footer=(interaction.user.name, interaction.user.display_avatar.url),
                fields={
                    "Previous Escalation Level:": "Moderator Ticket",
                    "Current Escalation Level:": "Administrator Ticket",
                    "Escalation Notes:": reason
                }
            )

            escalation_embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=escalation_embed)

            close_bttn = Button(custom_id=f"admin-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

            select_options = [
                nextcord.SelectOption(label="Moderator Ticket", description="Change escalation level to: Moderator"),
                nextcord.SelectOption(label="Senior Moderator Ticket", description="Change escalation level to: Senior Moderator"),
                nextcord.SelectOption(label="Administrator Ticket", description="Change escalation level to: Administrator")
            ]
            escalation_dropdown = Select(custom_id=f"admin-ticket-escalation:{user.id}", options=select_options, min_values=1, max_values=1, placeholder="Escalation Options")

            button_view = View(auto_defer=False)
            button_view.add_item(escalation_dropdown)
            button_view.add_item(close_bttn)

            await interaction.message.edit(view=button_view)

        case ["senior_ticket", "Moderator Ticket"]:
            overwrites.update({interaction.guild.get_role(config.permission_roles.trial_moderator): nextcord.PermissionOverwrite(read_messages=True)})
            overwrites.update({interaction.guild.get_role(config.permission_roles.moderator): nextcord.PermissionOverwrite(read_messages=True)})

            ticket_counts.mod_tickets = int(ticket_counts.mod_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)
            case_name = (f"mod-ticket-{str(ticket_counts.mod_tickets).zfill(4)}")

            try:
                with open(config.datafiles.ticketers, "rb") as f:
                    ticketers = pickle.load(f)
            except FileNotFoundError:
                ticketers = {
                    "mod tickets": [],
                    "senior tickets": [],
                    "admin tickets": [],
                    "verification tickets": []
                }

            try:
                initial_embed = interaction.message.embeds[0]
            except IndexError:
                raise Exception("Could not find embed when attempting to escalate ticket! Index out of range!")

            complainer_id = initial_embed.description[2:21]
            if str(complainer_id)[0] == "!":
                complainer_id = initial_embed.description[3:21]

            complainer_id = int(complainer_id)

            try:
                complainer = client.get_user(complainer_id)
                user = complainer
            except ValueError:
                raise Exception("Could not translate user ID into user")

            if user.id in ticketers["senior tickets"]:
                ticketers["senior tickets"].remove(complainer.id)
                ticketers["mod tickets"].append(str(complainer.id))
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

            overwrites.update({complainer: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=True, embed_links=True, attach_files=True, use_external_emojis=True)})

            await interaction.channel.edit(name=case_name, overwrites=overwrites)

            escalation_embed = SersiEmbed(
                title="Ticket Escalation Level Changed",
                description="This ticket has undergone a change in escalation level.",
                footer=(interaction.user.name, interaction.user.display_avatar.url),
                fields={
                    "Previous Escalation Level:": "Senior Moderator Ticket",
                    "Current Escalation Level:": "Moderator Ticket",
                    "Escalation Notes:": reason
                }
            )

            escalation_embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=escalation_embed)

            close_bttn = Button(custom_id=f"moderator-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

            select_options = [
                nextcord.SelectOption(label="Moderator Ticket", description="Change escalation level to: Moderator"),
                nextcord.SelectOption(label="Senior Moderator Ticket", description="Change escalation level to: Senior Moderator"),
                nextcord.SelectOption(label="Administrator Ticket", description="Change escalation level to: Administrator")
            ]
            escalation_dropdown = Select(custom_id=f"moderator-ticket-escalation:{user.id}", options=select_options, min_values=1, max_values=1, placeholder="Escalation Options")

            button_view = View(auto_defer=False)
            button_view.add_item(escalation_dropdown)
            button_view.add_item(close_bttn)

            await interaction.message.edit(view=button_view)

        case ["senior_ticket", "Administrator Ticket"]:
            ticket_counts.admin_tickets = int(ticket_counts.admin_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)
            case_name = (f"admin-ticket-{str(ticket_counts.admin_tickets).zfill(4)}")

            try:
                with open(config.datafiles.ticketers, "rb") as f:
                    ticketers = pickle.load(f)
            except FileNotFoundError:
                ticketers = {
                    "mod tickets": [],
                    "senior tickets": [],
                    "admin tickets": [],
                    "verification tickets": []
                }

            try:
                initial_embed = interaction.message.embeds[0]
            except IndexError:
                raise Exception("Could not find embed when attempting to escalate ticket! Index out of range!")

            complainer_id = initial_embed.description[2:21]
            if str(complainer_id)[0] == "!":
                complainer_id = initial_embed.description[3:21]

            complainer_id = int(complainer_id)

            try:
                complainer = client.get_user(complainer_id)
                user = complainer
            except ValueError:
                raise Exception("Could not translate user ID into user")

            if user.id in ticketers["senior tickets"]:
                ticketers["senior tickets"].remove(complainer.id)
                ticketers["admin tickets"].append(str(complainer.id))
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

            overwrites.update({complainer: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=True, embed_links=True, attach_files=True, use_external_emojis=True)})

            await interaction.channel.edit(name=case_name, overwrites=overwrites)

            escalation_embed = SersiEmbed(
                title="Ticket Escalation Level Changed",
                description="This ticket has undergone a change in escalation level.",
                footer=(interaction.user.name, interaction.user.display_avatar.url),
                fields={
                    "Previous Escalation Level:": "Senior Moderator Ticket",
                    "Current Escalation Level:": "Administrator Ticket",
                    "Escalation Notes:": reason
                }
            )

            escalation_embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=escalation_embed)

            close_bttn = Button(custom_id=f"admin-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

            select_options = [
                nextcord.SelectOption(label="Moderator Ticket", description="Change escalation level to: Moderator"),
                nextcord.SelectOption(label="Senior Moderator Ticket", description="Change escalation level to: Senior Moderator"),
                nextcord.SelectOption(label="Administrator Ticket", description="Change escalation level to: Administrator")
            ]
            escalation_dropdown = Select(custom_id=f"admin-ticket-escalation:{user.id}", options=select_options, min_values=1, max_values=1, placeholder="Escalation Options")

            button_view = View(auto_defer=False)
            button_view.add_item(escalation_dropdown)
            button_view.add_item(close_bttn)

            await interaction.message.edit(view=button_view)

        case ["admin_ticket", "Moderator Ticket"]:
            overwrites.update({interaction.guild.get_role(config.permission_roles.trial_moderator): nextcord.PermissionOverwrite(read_messages=True)})
            overwrites.update({interaction.guild.get_role(config.permission_roles.moderator): nextcord.PermissionOverwrite(read_messages=True)})

            ticket_counts.mod_tickets = int(ticket_counts.mod_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)
            case_name = (f"mod-ticket-{str(ticket_counts.mod_tickets).zfill(4)}")

            try:
                with open(config.datafiles.ticketers, "rb") as f:
                    ticketers = pickle.load(f)
            except FileNotFoundError:
                ticketers = {
                    "mod tickets": [],
                    "senior tickets": [],
                    "admin tickets": [],
                    "verification tickets": []
                }

            try:
                initial_embed = interaction.message.embeds[0]
            except IndexError:
                raise Exception("Could not find embed when attempting to escalate ticket! Index out of range!")

            complainer_id = initial_embed.description[2:21]
            if str(complainer_id)[0] == "!":
                complainer_id = initial_embed.description[3:21]

            complainer_id = int(complainer_id)

            try:
                complainer = client.get_user(complainer_id)
                user = complainer
            except ValueError:
                raise Exception("Could not translate user ID into user")

            if user.id in ticketers["admin tickets"]:
                ticketers["admin tickets"].remove(complainer.id)
                ticketers["mod tickets"].append(str(complainer.id))
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

            overwrites.update({complainer: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=True, embed_links=True, attach_files=True, use_external_emojis=True)})

            await interaction.channel.edit(name=case_name, overwrites=overwrites)

            escalation_embed = SersiEmbed(
                title="Ticket Escalation Level Changed",
                description="This ticket has undergone a change in escalation level.",
                footer=(interaction.user.name, interaction.user.display_avatar.url),
                fields={
                    "Previous Escalation Level:": "Administrator Ticket",
                    "Current Escalation Level:": "Moderator Ticket",
                    "Escalation Notes:": reason
                }
            )

            escalation_embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=escalation_embed)

            close_bttn = Button(custom_id=f"moderator-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

            select_options = [
                nextcord.SelectOption(label="Moderator Ticket", description="Change escalation level to: Moderator"),
                nextcord.SelectOption(label="Senior Moderator Ticket", description="Change escalation level to: Senior Moderator"),
                nextcord.SelectOption(label="Administrator Ticket", description="Change escalation level to: Administrator")
            ]
            escalation_dropdown = Select(custom_id=f"moderator-ticket-escalation:{user.id}", options=select_options, min_values=1, max_values=1, placeholder="Escalation Options")

            button_view = View(auto_defer=False)
            button_view.add_item(escalation_dropdown)
            button_view.add_item(close_bttn)

            await interaction.message.edit(view=button_view)

        case ["admin_ticket", "Senior Moderator Ticket"]:
            overwrites.update({interaction.guild.get_role(config.permission_roles.senior_moderator): nextcord.PermissionOverwrite(read_messages=True)})

            ticket_counts.senior_tickets = int(ticket_counts.senior_tickets) + 1
            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)
            case_name = (f"senior-ticket-{str(ticket_counts.senior_tickets).zfill(4)}")

            try:
                with open(config.datafiles.ticketers, "rb") as f:
                    ticketers = pickle.load(f)
            except FileNotFoundError:
                ticketers = {
                    "mod tickets": [],
                    "senior tickets": [],
                    "admin tickets": [],
                    "verification tickets": []
                }

            try:
                initial_embed = interaction.message.embeds[0]
            except IndexError:
                raise Exception("Could not find embed when attempting to escalate ticket! Index out of range!")

            complainer_id = initial_embed.description[2:21]
            if str(complainer_id)[0] == "!":
                complainer_id = initial_embed.description[3:21]

            complainer_id = int(complainer_id)

            try:
                complainer = client.get_user(complainer_id)
                user = complainer
            except ValueError:
                raise Exception("Could not translate user ID into user")

            if user.id in ticketers["admin tickets"]:
                ticketers["admin tickets"].remove(complainer.id)
                ticketers["senior tickets"].append(str(complainer.id))
                with open(config.datafiles.ticketers, "wb") as f:
                    pickle.dump(ticketers, f)

            overwrites.update({complainer: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=True, embed_links=True, attach_files=True, use_external_emojis=True)})

            await interaction.channel.edit(name=case_name, overwrites=overwrites)

            escalation_embed = SersiEmbed(
                title="Ticket Escalation Level Changed",
                description="This ticket has undergone a change in escalation level.",
                footer=(interaction.user.name, interaction.user.display_avatar.url),
                fields={
                    "Previous Escalation Level:": "Administrator Ticket",
                    "Current Escalation Level:": "Senior Moderator Ticket",
                    "Escalation Notes:": reason
                }
            )

            escalation_embed.set_footer(text=interaction.user.display_name, icon_url=interaction.user.display_avatar.url)
            await interaction.channel.send(embed=escalation_embed)

            close_bttn = Button(custom_id=f"senior-ticket-close:{user.id}", label="Close Ticket", style=nextcord.ButtonStyle.red)

            select_options = [
                nextcord.SelectOption(label="Moderator Ticket", description="Change escalation level to: Moderator"),
                nextcord.SelectOption(label="Senior Moderator Ticket", description="Change escalation level to: Senior Moderator"),
                nextcord.SelectOption(label="Administrator Ticket", description="Change escalation level to: Administrator")
            ]
            escalation_dropdown = Select(custom_id=f"senior-ticket-escalation:{user.id}", options=select_options, min_values=1, max_values=1, placeholder="Escalation Options")

            button_view = View(auto_defer=False)
            button_view.add_item(escalation_dropdown)
            button_view.add_item(close_bttn)

            await interaction.message.edit(view=button_view)
