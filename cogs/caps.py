import nextcord
from nextcord.ext import commands
import re

from configutils import get_config, get_config_int, set_config
from permutils import permcheck, is_mod


class Caps(commands.Cog):
    def __init__(self, bot):
        self.sersisuccess = get_config('EMOTES', 'success')
        self.sersifail = get_config('EMOTES', 'fail')
        self.bot = bot
        self.MIN_CHARS_FOR_DETECTION = get_config_int('CAPS', 'capslength', 5)

    @commands.command()
    async def setcapslength(self, ctx, number):
        if not await permcheck(ctx, is_mod):
            return

        try:
            value = int(number)
        except ValueError:
            await ctx.send(f"{self.sersifail} {number} is not an integer.")
            return

        if value < 0:
            await ctx.send(f"{self.sersifail} {number} must be greater than **0**.")
            return

        old_val = self.MIN_CHARS_FOR_DETECTION
        self.MIN_CHARS_FOR_DETECTION = value
        set_config('CAPS', 'capslength', number)

        await ctx.send(f"{self.sersisuccess} Caps lock detection starts now at messages longer than **{value}**.")

        embed = nextcord.Embed(
            title="Minimum Letters For Detection Changed",
            description="The minimum number of letters required for a message to have caps detection has been changed",
            color=nextcord.Color.from_rgb(237, 91, 6))
        embed.add_field(name="Moderator", value=ctx.author.mention)
        embed.add_field(name="Old Value", value=str(old_val))
        embed.add_field(name="New Value", value=str(value))

        channel = ctx.guild.get_channel(get_config_int('CHANNELS', 'logging'))
        await channel.send(embed=embed)

    @commands.command()
    async def getcapslength(self, ctx):
        if not await permcheck(ctx, is_mod):
            return

        await ctx.send(f"Current caps lock detection starts at messages longer than **{self.MIN_CHARS_FOR_DETECTION}**.")

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        msg_string = message.content
        new_msg_string = re.sub(r'(<a?)?:\w+:(\d{18}>)?', '', msg_string)

        new_msg_string = re.sub(r'[^a-zA-Z]', '', new_msg_string)

        if len(new_msg_string) > self.MIN_CHARS_FOR_DETECTION:
            # remove nums and non-alpanumeric
            # msg_string = unidecode.unidecode(msg_string)

            # remove emotes
            uppercase = sum(1 for char in new_msg_string if char.isupper())

            if len(new_msg_string) == 0:
                return

            percentage = uppercase / len(new_msg_string)

            if percentage > 0.7:
                # await replace(self, message, message.author, msg_string)
                await message.delete(delay=None)

                channel_webhooks = await message.channel.webhooks()
                new_msg_jump_url = ''
                msg_sent = False

                for webhook in channel_webhooks:                  # tries to find existing webhook
                    if webhook.name == "caps webhook by sersi":
                        replacement_message = await webhook.send(str(msg_string.lower()), username=message.author.display_name, avatar_url=message.author.display_avatar.url, wait=True)
                        new_msg_jump_url = replacement_message.jump_url
                        msg_sent = True

                if not msg_sent:                          # creates webhook if none found
                    webhook = await message.channel.create_webhook(name="caps webhook by sersi")
                    replacement_message = await webhook.send(str(msg_string.lower()), username=message.author.display_name, avatar_url=message.author.display_avatar.url, wait=True)
                    new_msg_jump_url = replacement_message.jump_url
                    msg_sent = True

                # replacement_message = await webhook.send(str(msg_string.lower()), username=message.author.display_name, avatar_url=message.author.display_avatar.url, wait=True)

                channel = self.bot.get_channel(get_config_int('CHANNELS', 'logging'))
                logging_embed = nextcord.Embed(
                    title="Caps Lock Message replaced",
                    description="",
                    color=nextcord.Color.from_rgb(237, 91, 6)
                )
                logging_embed.add_field(name="User:", value=message.author.mention, inline=False)
                logging_embed.add_field(name="Channel:", value=message.channel.mention, inline=False)
                logging_embed.add_field(name="Original Message:", value=msg_string, inline=False)
                logging_embed.add_field(name="Replacement Message:", value=str(msg_string.lower()), inline=False)
                logging_embed.add_field(name="Link to Replacement Message:", value=f"[Jump!]({new_msg_jump_url})", inline=True)
                await channel.send(embed=logging_embed)


def setup(bot):
    bot.add_cog(Caps(bot))
