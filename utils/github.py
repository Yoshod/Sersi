from github import Github, Auth, Issue
import nextcord
import yaml


def submit_issue(
    issue_type: str,
    interaction: nextcord.Interaction,
    modal_data: dict[str, str] | None,
):
    with open("files/import/githubapi.yaml", "r") as f:
        apikeys = yaml.safe_load(f)

        auth = Auth.Token(apikeys["apikey"])

        ghub = Github(auth=auth)

        repo = ghub.get_repo("Yoshod/Sersi")

    if issue_type == "feature":
        issue: Issue = repo.create_issue(
            title=interaction.message.embeds[0].title,
            body=f"**Description:**\n{interaction.message.embeds[0].fields[1].value}\n\n**Use Case:**\n{interaction.message.embeds[0].fields[2].value}\n\n**Proposed Solution:**\n{modal_data['proposed_solution']}\n\n**Additional Info:**\n{interaction.message.embeds[0].fields[3].value}\n\n**Impact on Project:**\n{modal_data['impact']}\n\n**Priority:**\n{modal_data['priority']}\n\n**Reason for Priority:**\n{modal_data['priority_reason']}\n\n**Milestone:**\n{modal_data['milestone']}\n\n**This issue was submitted automatically by Sersi.**",
        )

    elif issue_type == "bug":
        issue: Issue = repo.create_issue(
            title=interaction.message.embeds[0].title,
            body=f"**Description:**\n{interaction.message.embeds[0].fields[1].value}\n\n**Steps to Reproduce:**\n{interaction.message.embeds[0].fields[2].value}\n\n**Expected Behaviour:**\n{interaction.message.embeds[0].fields[3].value}\n\n**Screenshots:**\nMust be uploaded manually.\n\n**Client Type:**\n{interaction.message.embeds[0].fields[4].value}\n\n**Client Version:**\n{interaction.message.embeds[0].fields[5].value}\n\n**Additional Info:**\n{interaction.message.embeds[0].fields[6].value}\n\n**This issue was submitted automatically by Sersi.**",
            labels=[repo.get_label("Bug"), repo.get_label("Investigate")],
        )

    return issue.number
