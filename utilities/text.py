def text_embed_value_escape_codeblock(content: str | None) -> str:
    if content is None:
        return "**None**"

    return "\n```\n" + content.replace("```", "'''") + "\n```"
