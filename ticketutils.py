import json
import pickle
import nextcord
import io
from chat_exporter import export
from dataclasses import dataclass, asdict
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
        user: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=False, embed_links=False, attach_files=False, use_external_emojis=False)
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
