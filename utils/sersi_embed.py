from datetime import datetime, timezone

import nextcord


class SersiEmbed(nextcord.Embed):
    def __init__(
        self,
        *,
        fields: dict[str, str] = None,
        footer: str = nextcord.embeds.EmptyEmbed,
        footer_icon: str = nextcord.embeds.EmptyEmbed,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Configure Embed Footer
        self.set_footer(text=footer, icon_url=footer_icon)
        self.timestamp = datetime.now(timezone.utc)

        # Configure Colour
        if "color" not in kwargs and "colour" not in kwargs:
            self.colour = nextcord.Color.from_rgb(237, 91, 6)

        # Configure Fields
        if fields:
            for field in fields:
                self.add_field(name=field, value=fields[field], inline=False)

    def add_id_field(self, ids: dict):
        id_string: str = f"```ini"
        for key in ids:
            id_string += f"\n{key} = {ids[key]}"
        id_string += "```"
        self.add_field(name="IDs", value=id_string, inline=False)
        return self
