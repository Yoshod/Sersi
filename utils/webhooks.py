import nextcord


async def send_webhook_message(*, channel: nextcord.TextChannel, **kwargs):
    channel_webhooks = await channel.webhooks()
    msg_sent = False
    if "allowed_mentions" in kwargs:
        del kwargs["allowed_mentions"]

    for webhook in channel_webhooks:  # tries to find existing webhook
        if webhook.name == "sersi webhook":
            return await webhook.send(
                allowed_mentions=nextcord.AllowedMentions.none(), **kwargs
            )

    if not msg_sent:  # creates webhook if none found
        webhook = await channel.create_webhook(name="sersi webhook")
        return await webhook.send(**kwargs)
