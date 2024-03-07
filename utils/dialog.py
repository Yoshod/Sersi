import asyncio
from asyncio import Future
from enum import Enum
from typing import Any, Optional

import nextcord
from nextcord import ButtonStyle
from nextcord.ui import View, Button

from utils.sersi_embed import SersiEmbed


class ButtonPreset(Enum):
    CONFIRM = ("Confirm", ButtonStyle.success)
    CONFIRM_DANGER = ("Confirm", ButtonStyle.danger)
    CONFIRM_PRIMARY = ("Confirm", ButtonStyle.primary)
    PROCEED = ("Proceed", ButtonStyle.success)
    PROCEED_DANGER = ("Proceed", ButtonStyle.danger)
    PROCEED_PRIMARY = ("Proceed", ButtonStyle.primary)
    YES = ("Yes", ButtonStyle.success)
    YES_DANGER = ("Yes", ButtonStyle.danger)
    YES_PRIMARY = ("Yes", ButtonStyle.primary)

    CANCEL = ("Cancel", ButtonStyle.danger)
    CANCEL_PRIMARY = ("Cancel", ButtonStyle.primary)
    CANCEL_NEUTRAL = ("Cancel", ButtonStyle.secondary)
    NO = ("No", ButtonStyle.danger)
    NO_PRIMARY = ("No", ButtonStyle.primary)
    NO_NEUTRAL = ("No", ButtonStyle.secondary)


class _DialogView(View):
    """
    View class for message based dialog.

    Attributes:
    future (Future): The future to set the result of when a button is clicked.
    author (nextcord.User): The user who initiated the dialog.
    buttons (dict[tuple[str, Optional[ButtonStyle]], Any]): A dictionary of button labels and their corresponding values.
    timeout (int, optional): The timeout for the view. Defaults to 180.
    """

    message: Optional[nextcord.Message] = None

    def __init__(
        self,
        future: Future,
        author: nextcord.User,
        buttons: dict[tuple[str, Optional[ButtonStyle]], Any],
        timeout: int = 180,
    ):
        super().__init__(timeout=timeout)
        self.future = future
        self.author = author

        for (label, style), value in buttons.items():
            button = Button(
                style=style or ButtonStyle.primary,
                label=label,
            )

            async def callback(interaction: nextcord.Interaction, *, value=value):
                self.future.set_result(value)
                if interaction.message.flags.ephemeral():
                    await interaction.response.edit_message(view=None)
                else:
                    await interaction.message.delete()
                self.stop()

            button.callback = callback
            self.add_item(button)

    def on_timeout(self):
        self.future.set_result(None)

        if self.message is None:
            return

        if self.message.flags.ephemeral():
            self.message.edit(view=None)
        else:
            self.message.delete()

    async def interaction_check(self, interaction: nextcord.Interaction):
        return interaction.user == self.author


async def message_dialog(
    interaction: nextcord.Interaction,
    buttons: dict[tuple[str, Optional[ButtonStyle]], Any],
    content: str = None,
    embed: nextcord.Embed = None,
    timeout: int = 180,
    ephemeral: bool = False,
) -> bool:
    """Creates a confirmation dialog for the user to confirm or deny an action."""
    confirm_future: Future[bool] = asyncio.get_running_loop().create_future()

    if content is None and embed is None:
        raise ValueError("You must provide either content or an embed.")
    
    view = _DialogView(confirm_future, interaction.user, buttons, timeout)

    message = await interaction.send(
        content=content,
        embed=embed,
        view=view,
        ephemeral=ephemeral,
        delete_after=timeout if not ephemeral else None,
    )
    view.message = message

    return await confirm_future


async def confirm(
    interaction: nextcord.Interaction,
    content: str = None,
    embed: nextcord.Embed = None,
    title: str = None,
    description: str = None,
    embed_fields: list[tuple[str, str]] = None,
    timeout: int = 180,
    ephemeral: bool = False,
    true_button: ButtonPreset = ButtonPreset.CONFIRM,
    false_button: ButtonPreset = ButtonPreset.CANCEL,
) -> bool:
    """Creates a confirmation dialog for the user to confirm or deny an action."""

    if embed is None and content is None:
        embed = SersiEmbed(
            title=title or "Confirmation",
            description=description or "Are you sure you want to do this?",
            fields=embed_fields,
            author=interaction.user,
        )

    response = await message_dialog(
        interaction,
        { true_button.value: True, false_button.value: False },
        content=content,
        embed=embed,
        timeout=timeout,
        ephemeral=ephemeral,
    )

    if response is False:
        await interaction.send("*Action cancelled!*")

    return response
