import nextcord
from nextcord.ext import commands


async def is_sersi_contributor(member: nextcord.Member, bot: commands.Bot) -> bool:
    app_info = await bot.application_info()

    if member.id not in [developer.id for developer in app_info.team.members]:
        return False

    return True
