import nextcord


# Loads the cog by the given name.
#
# bot:        The bot instance to load the given cog for.
# name:       The name of the cog to load. It already includes cogs., and doesn't need ".py" at the end.
# config:     The loaded configuration.
# start_time: The timestamp of when the bot was launched.
#
# Exceptions are passed down as-is.
def load_cog(bot: nextcord.Client, name: str, config, start_time: float):
    bot.load_extension(f"cogs.{name}", extras={"config": config, "start_time": start_time})


# Unloads the cog by the given name.
#
# bot:  The bot instance to unload the given cog from.
# name: The name of the cog. It already includes cogs., and doesn't need ".py" at the end.
#
# Exceptions are passed down as-is.
def unload_cog(bot: nextcord.Client, name: str):
    bot.unload_extension(f"cogs.{name}")
