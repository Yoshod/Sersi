import nextcord
from configutils import get_config_int
from nextcord.ui import View, Button


def modmention_check(messageData):
    modmentions = [
        f"<@&{get_config_int('PERMISSION ROLES', 'trial moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'senior moderator')}>",
        f"<@&{get_config_int('PERMISSION ROLES', 'dark moderator')}>"
    ]

    for modmention in modmentions:
        if modmention in messageData:
            return True
    return False


class ConfirmView(View):
    def __init__(self, on_proceed, timeout: float = 60.0):
        super().__init__(timeout=timeout)
        btn_proceed = Button(label="Proceed", style=nextcord.ButtonStyle.green)
        btn_proceed.callback = on_proceed
        btn_cancel = Button(label="Cancel", style=nextcord.ButtonStyle.red)
        btn_cancel.callback = self.cb_cancel
        self.add_item(btn_proceed)
        self.add_item(btn_cancel)

    async def cb_cancel(self, interaction):
        await interaction.message.edit("Action canceled!", embed=None, view=None)

    async def on_timeout(self):
        self.message = await self.message.channel.fetch_message(self.message.id)
        if self.message.components != []:
            await self.message.edit("Action timed out!", embed=None, view=None)

    async def interaction_check(self, interaction):
        return interaction.user == interaction.message.reference.cached_message.author

    async def send_as_reply(self, ctx, content: str = None, embed=None):
        self.message = await ctx.reply(content, embed=embed, view=self)
