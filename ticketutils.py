import json
import nextcord
from dataclasses import dataclass, asdict
import configutils


CONFIG = configutils.Configuration.from_yaml_file("./persistent_data/config.yaml")


@dataclass(kw_only=True)
class TicketIterations():
    mod_tickets: int
    senior_tickets: int
    admin_tickets: int
    verification_tickets: int

    """def dict(self):
        return {
            'mod_tickets': self.mod_tickets.__dict__,
            'senior_tickets': self.senior_tickets.__dict__,
            'admin_tickets': self.admin_tickets.__dict__,
            'verification_tickets': self.verification_tickets.__dict__}"""


def ticket_check(id, ticket_type):
    with open("files/Tickets/ticketers.json", "r", encoding="utf-8") as f:
        ticketers = json.load(f)

    match ticket_type:
        case "mod_ticket":
            if id in ticketers["mod_tickets"]:
                return False

            else:
                ticketers["mod_tickets"].append(id)
                with open("files/Tickets/ticketers.json", "w", encoding="utf-8") as f:
                    json.dumps((ticketers), f, ensure_ascii=False, indent=4)
                return True

        case "senior_ticket":
            if id in ticketers["senior_tickets"]:
                return False

            else:
                ticketers["senior_tickets"].append(id)
                with open("files/Tickets/ticketers.json", "w", encoding="utf-8") as f:
                    json.dumps((ticketers), f, ensure_ascii=False, indent=4)
                return True

        case "admin_ticket":
            if id in ticketers["admin_tickets"]:
                return False

            else:
                ticketers["admin_tickets"].append(id)
                with open("files/Tickets/ticketers.json", "w", encoding="utf-8") as f:
                    json.dumps((ticketers), f, ensure_ascii=False, indent=4)
                return True

        case "verification_ticket":
            if id in ticketers["verification_tickets"]:
                return False

            else:
                ticketers["verification_tickets"].append(id)
                with open("files/Tickets/ticketers.json", "w", encoding="utf-8") as f:
                    json.dumps((ticketers), f, ensure_ascii=False, indent=4)
                return True


def ticket_prep(interaction, user, ticket_type):
    overwrites = {
        interaction.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
        interaction.guild.me: nextcord.PermissionOverwrite(read_messages=True),
        user: nextcord.PermissionOverwrite(read_messages=True, create_public_threads=False, create_private_threads=False, external_stickers=False, embed_links=False, attach_files=False, use_external_emojis=False)}

    with open("files/Tickets/ticketiters.json", "r", encoding="utf-8") as f:
        iters = json.load(f)
        print(iters)
        ticket_counts = TicketIterations(
            mod_tickets=iters["mod_tickets"],
            senior_tickets=iters["senior_tickets"],
            admin_tickets=iters["admin_tickets"],
            verification_tickets=iters["verification_tickets"])
        print(ticket_counts)

    match ticket_type:
        case "mod_ticket":
            overwrites.update({interaction.guild.get_role(CONFIG.permission_roles.moderator): nextcord.PermissionOverwrite(read_messages=True)})
            overwrites.update({interaction.guild.get_role(CONFIG.permission_roles.trial_moderator): nextcord.PermissionOverwrite(read_messages=True)})
            ticket_counts.mod_tickets = ticket_counts.mod_tickets + 1

            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            case_name = (f"mod-ticket-{str(ticket_counts.mod_tickets).zfill(4)}")

            return overwrites, case_name

        case "senior_ticket":
            overwrites.update({interaction.guild.get_role(CONFIG.permission_roles.senior_moderator): nextcord.PermissionOverwrite(read_messages=True)})
            ticket_counts.senior_tickets = ticket_counts.senior_tickets + 1

            with open("files/Tickets/ticketiters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            case_name = (f"senior-ticket-{str(ticket_counts.mod_tickets).zfill(4)}")

            return overwrites, case_name

        case "admin_ticket":
            print(ticket_counts.admin_tickets)
            ticket_counts.admin_tickets = int(ticket_counts.admin_tickets) + 1
            with open("files/Tickets/tickeriters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            case_name = (f"admin-ticket-{str(ticket_counts.mod_tickets).zfill(4)}")

            return overwrites, case_name

        case "verification_ticket":
            ticket_counts.verification_tickets = ticket_counts.verification_tickets + 1
            with open("files/Tickets/tickeriters.json", "w", encoding="utf-8") as f:
                json.dump(asdict(ticket_counts), f, ensure_ascii=False, indent=4)

            overwrites.update({interaction.guild.get_role(CONFIG.permission_roles.ticket_support): nextcord.PermissionOverwrite(read_messages=True)})

            case_name = (f"verification-ticket-{str(ticket_counts.mod_tickets).zfill(4)}")
            return overwrites, case_name


def ticket_close():
    pass
