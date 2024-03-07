from abc import ABC, abstractmethod
import asyncio
from asyncio import Future
from enum import Enum
from typing import Any, Optional
from discord import TextInputStyle

import nextcord
from nextcord import ButtonStyle
from nextcord.ui import View, Button, Modal, TextInput

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
                if interaction.message.flags.ephemeral:
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
) -> Any:
    """Creates a confirmation dialog for the user to confirm or deny an action."""
    confirm_future: Future[Any] = asyncio.get_running_loop().create_future()

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
        {true_button.value: True, false_button.value: False},
        content=content,
        embed=embed,
        timeout=timeout,
        ephemeral=ephemeral,
    )

    if response is False:
        await interaction.send("*Action cancelled!*")

    return response


class DialogModal(Modal):
    """
    Modal class for modal based dialog.

    Attributes:
    timeout (int, optional): The timeout for the view. Defaults to 180.
    **kwargs (TextInput): The inputs for the modal, as keyword arguments.
    """

    def __init__(
        self,
        title: str,
        timeout: int = 300,
        **kwargs: TextInput,
    ):
        super().__init__(title, timeout=timeout)

        for input in kwargs.values():
            self.add_item(input)

        self.inputs = kwargs

    async def callback(self, interaction: nextcord.Interaction):
        self.stop()

    async def get_response(self) -> dict[str, str]:
        """
        Waits for the user to respond to the modal and returns the inputs as a dictionary.

        Returns:
        dict[str, str]: The inputs from the user.
        None: If the user did not respond.
        """
        if await self.wait():
            return None
        return {name: input.value for name, input in self.inputs.items()}


async def modal_dialog(
    interaction: nextcord.Interaction,
    title: str,
    *,
    timeout: int = 300,
    **kwargs: TextInput,
) -> dict[str, str]:
    """
    Creates a modal dialog for the user to input data.

    Args:
    interaction (nextcord.Interaction): The interaction to send the modal to.
    timeout (int, optional): The timeout for the modal. Defaults to 600.
    **kwargs (TextInput): The inputs for the modal, as keyword arguments.

    Returns:
    dict[str, str]: The inputs from the user.
    None: If the user did not respond.
    """

    modal = DialogModal(title, timeout=timeout, **kwargs)

    await interaction.response.send_modal(modal)

    return await modal.get_response()


class TextField(TextInput):
    """
    TextInput class for text field based dialog.

    Attributes:
    label (str): The label for the text input.
    placeholder (str, optional): The placeholder for the text input. Defaults to None.
    required (bool, optional): If ``True``, the user cannot send the form without filling this field. Defaults to True.
    """

    def __init__(self, label: str, placeholder: str = None, required: bool = True):
        super().__init__(
            label,
            placeholder=placeholder,
            required=required,
            max_length=1024,
            min_length=8 if required else 0,
        )
