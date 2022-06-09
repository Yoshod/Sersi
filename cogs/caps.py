import nextcord
from nextcord.ext import commands
import re
from baseutils import getLoggingChannel, isMod
from config import get_config, get_config_int, set_config
# from nextcord.ext.commands.errors import MemberNotFound


class Caps(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def setcapslength(self, ctx, number):
        if not isMod(ctx.author.roles):
            await ctx.send(f"<:sersifail:979070135799279698> Insufficient permission!")
            return

        try:
            value = int(number)
        except ValueError:
            await ctx.send(f"<:sersifail:979070135799279698> {number} is not an integer.")
            return

        if value < 0:
            await ctx.send(f"<:sersifail:979070135799279698> {number} must be greater than **0**.")
            return

        set_config('CAPS', 'capslength', str(value))

        await ctx.send(f"<:sersisuccess:979066662856822844> Caps lock detection starts now at messages longer than **{value}**.")

    @commands.command()
    async def getcapslength(self, ctx):
        if not isMod(ctx.author.roles):
            await ctx.send(f"<:sersifail:979070135799279698> Insufficient permission!")
            return

        await ctx.send(f"Current caps lock detection starts at messages longer than **{get_config('CAPS', 'capslength', 5)}**.")

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        msg_string = message.content

        if len(msg_string) > get_config_int('CAPS', 'capslength', 5):
            # remove nums and non-alpanumeric
            # msg_string = unidecode.unidecode(msg_string)

            # remove emotes
            new_msg_string = re.sub(r'(<a?)?:\w+:(\d{18}>)?', '', msg_string)

            new_msg_string = re.sub(r'[^a-zA-Z]', '', new_msg_string)
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

                channel = self.bot.get_channel(getLoggingChannel(message.guild.id))
                logging_embed = nextcord.Embed(
                    title=f"Caps Lock Message replaced",
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
