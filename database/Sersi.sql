create table guild_preferences
(
    -- The ID of the guild.
    guild_id              int unique,

    -- The ID of the channel that'll receive updates regarding channels.
    channel_log_id        int,

    -- The ID of the channel that'll receive updates regarding the server itself.
    guild_log_id          int,

    -- The ID of the channel that'll receive updates regarding members joining, leaving or updating their account.
    member_log_id         int,

    -- The ID of the channel that'll receive updates regarding emotes and stickers.
    emote_sticker_log_id  int,

    -- The ID of the channel that'll receive updates regarding roles.
    role_log_id           int,

    -- The ID of the channel that'll receive updates regarding messages.
    message_log_id        int,

    -- The ID of the channel that'll receive YouTube notifications.
    youtube_notifications int
);

create table guild_youtube_subscriptions
(
    -- The ID of the guild.
    guild_id   int,

    -- The unique ID of the YouTube channel.
    channel_id text unique
);
