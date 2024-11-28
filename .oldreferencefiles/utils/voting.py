from datetime import datetime, timedelta

import nextcord
from nextcord.ui import Button, View

from utils.config import VoteType
from utils.database import VoteDetails
from utils.perms import cb_is_mod


class VoteView(View):
    def __init__(self, vote_type: VoteType, details: VoteDetails):
        super().__init__(auto_defer=False)
        self.vote_type = vote_type
        self.add_item(Button(
            label="Yes",
            style=nextcord.ButtonStyle.green,
            custom_id=f"vote:{details.vote_id}:yes",
        ))
        self.add_item(Button(
            label="No",
            style=nextcord.ButtonStyle.red,
            custom_id=f"vote:{details.vote_id}:no",
        ))
        self.add_item(Button(
            label="Maybe",
            custom_id=f"vote:{details.vote_id}:maybe",
        ))
        self.interaction_check = cb_is_mod


def vote_planned_end(vote_type: VoteType) -> datetime:
    return datetime.utcnow() + timedelta(hours=vote_type.duration)
