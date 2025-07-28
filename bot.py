from typing import Any
from traceback import format_exc

import nextcord
from nextcord.ext.commands import Bot

from utils.base import limit_string
from utils.sersi_embed import SersiEmbed


class SersiBot(Bot):
    def __init__(self):
        super().__init__()
        self.error_channel: nextcord.abc.Messageable = None

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        if not self.error_channel:
            return super().on_error(self, event_method, *args, **kwargs)

        embed_fields = {
            "Event": event_method,
            "Arguments": limit_string(", ".join(args)),
        }

        for name, arg in kwargs.items():
            embed_fields[name.upper()] = limit_string(str(arg))

        await self.error_channel.send(
            embed=SersiEmbed(
                title="An Error Has Occurred",
                description=f"```{limit_string(''.join(format_exc()), 4090)}```",
                fields=embed_fields,
                footer=f"{self.user.global_name} ({self.user.name})",
                footer_icon=self.user.avatar.url,
                colour=nextcord.Color.from_rgb(208, 29, 29),
            )
        )
