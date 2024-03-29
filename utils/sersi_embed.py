from datetime import datetime, timezone

import nextcord

from utils.base import limit_string


class SersiEmbed(nextcord.Embed):
    def __init__(
        self,
        *,
        fields: dict[str, str] | list[dict[str, str]] = None,
        footer: str = nextcord.embeds.EmptyEmbed,
        footer_icon: str = nextcord.embeds.EmptyEmbed,
        thumbnail_url: str = nextcord.embeds.EmptyEmbed,
        author: nextcord.Member = nextcord.embeds.EmptyEmbed,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Configure Embed Thumbnail
        self.set_thumbnail(url=thumbnail_url)

        # Configure Embed Footer
        self.set_footer(text=footer, icon_url=footer_icon)
        self.timestamp = datetime.now(timezone.utc)

        # Configure Colour
        if "color" not in kwargs and "colour" not in kwargs:
            self.colour = nextcord.Color.from_rgb(237, 91, 6)

        # Configure Fields
        if fields:
            self.parse_fields(fields)
        
        # Configure Author
        if author:
            self.set_author(
                name=author.display_name,
                icon_url=author.display_avatar.url,
            )

    def add_id_field(self, ids: dict):
        id_string: str = "```ini"
        for key in ids:
            id_string += f"\n{key} = {ids[key]}"
        id_string += "```"
        self.add_field(name="IDs", value=limit_string(str(id_string)), inline=False)
        return self

    def parse_fields(self, fields, inline=False):
        match fields:
            case list():
                for row in fields:
                    self.parse_fields(row, inline=True)
            case dict():
                for field in fields:
                    self.add_field(
                        name=limit_string(str(field), 256),
                        value=limit_string(str(fields[field])),
                        inline=inline if len(fields) > 1 else False,
                    )
