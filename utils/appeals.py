import nextcord

from utils.base import encode_button_id


class SubmitBanAppealUnjust(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="My Ban Was Overly Harsh",
            custom_id=encode_button_id(
                "submit_appeal", type_of_appeal="ban", reason="unjust"
            ),
            disabled=False,
        )


class SubmitBanAppealNoRuleBroken(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="I Did Not Break Any Rules",
            custom_id=encode_button_id(
                "submit_appeal", type_of_appeal="ban", reason="no_rule_broken"
            ),
            disabled=False,
        )


class SubmitTimeoutAppealUnjust(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="My Timeout Was Overly Harsh",
            custom_id=encode_button_id(
                "submit_appeal", type_of_appeal="timeout", reason="unjust"
            ),
            disabled=False,
        )


class SubmitTimeoutAppealNoRuleBroken(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="I Did Not Break Any Rules",
            custom_id=encode_button_id(
                "submit_appeal", type_of_appeal="timeout", reason="no_rule_broken"
            ),
            disabled=False,
        )


class AppealAcceptedButton(nextcord.ui.Button):
    def __init__(self, case_id: str):
        super().__init__(
            style=nextcord.ButtonStyle.green,
            label="Accept Appeal",
            custom_id=encode_button_id("appeal_accepted", case_id=case_id),
            disabled=False,
        )


class AppealDeniedButton(nextcord.ui.Button):
    def __init__(self, case_id: str):
        super().__init__(
            style=nextcord.ButtonStyle.red,
            label="Deny Appeal",
            custom_id=encode_button_id("appeal_denied", case_id=case_id),
            disabled=False,
        )


class AppealViewCaseButton(nextcord.ui.Button):
    def __init__(self, case_id: str):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="View Case",
            custom_id=encode_button_id("appeal_view_case", case_id=case_id),
            disabled=False,
        )


class AppealDMUserButton(nextcord.ui.Button):
    def __init__(self, offender_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="DM Appellant",
            custom_id=encode_button_id("appeal_dm_user", offender_id=offender_id),
            disabled=False,
        )


class AppealDMModeratorsButton(nextcord.ui.Button):
    def __init__(self, thread_id: int):
        super().__init__(
            style=nextcord.ButtonStyle.blurple,
            label="DM Moderators",
            custom_id=encode_button_id("appeal_dm_moderators", thread_id=thread_id),
            disabled=False,
        )


class AppealOngoingView(nextcord.ui.View):
    def __init__(self, thread_id: int):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(AppealDMModeratorsButton(thread_id))


class AppealReceivedView(nextcord.ui.View):
    def __init__(self, case_id: str, offender_id: int):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(AppealAcceptedButton(case_id))
        self.add_item(AppealDeniedButton(case_id))
        self.add_item(AppealViewCaseButton(case_id))
        self.add_item(AppealDMUserButton(offender_id))


class TimeoutAppealsSubmitView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(SubmitTimeoutAppealUnjust())
        self.add_item(SubmitTimeoutAppealNoRuleBroken())


class AppealsSubmitView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None, auto_defer=False)
        self.add_item(SubmitBanAppealUnjust())
        self.add_item(SubmitBanAppealNoRuleBroken())
