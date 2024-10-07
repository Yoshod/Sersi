import nextcord
from nextcord.ext import commands

from utils.config import Configuration
from utils.perms import is_admin, permcheck


class Rules(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @commands.command()
    async def rules_embeds(self, ctx: commands.Context):
        if not await permcheck(ctx, is_admin):
            return

        be_respectful_embed = nextcord.Embed(
            title="Be Respectful",
            description="Treat others with respect. Harassment, hate speech, and toxicity will not be tolerated.",
            color=nextcord.Color.brand_green(),
        )
        be_respectful_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/respect.png?raw=true"
        )

        no_bigotry_embed = nextcord.Embed(
            title="No Bigotry",
            description="Bigotry of any kind is not allowed. This includes racism, sexism, homophobia, transphobia, and ableism.",
            color=nextcord.Color.brand_green(),
        )
        no_bigotry_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/discrimination.png?raw=true"
        )

        no_nsfw_embed = nextcord.Embed(
            title="No NSFW Content",
            description="NSFW content is not allowed. This includes explicit images, videos, and discussions. We have exceptions for 'adult' but not NSFW conversations.Those should be kept to the adult only channels.",
            color=nextcord.Color.brand_green(),
        )
        no_nsfw_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/18.png?raw=true"
        )

        no_spam_embed = nextcord.Embed(
            title="No Spam",
            description="Spamming is not allowed. This includes excessive messages, emojis, mentions, all caps, as well as advertising of any kind.",
            color=nextcord.Color.brand_green(),
        )
        no_spam_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/multiple-chat.png?raw=true"
        )

        no_slurs_embed = nextcord.Embed(
            title="No Slurs",
            description="Slurs are not allowed. This includes racial, gendered, and ableist slurs. Exceptions are made when a slur is used with appropriate contextualisation. Such as in discussions about the word itself or in a quote.",
            color=nextcord.Color.brand_green(),
        )
        no_slurs_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/swearing.png?raw=true"
        )

        no_foreign_language_embed = nextcord.Embed(
            title="No Foreign Language",
            description="This is an English-speaking server. Please keep all conversations in English both to ensure that everyone can participate and to enable moderation.",
            color=nextcord.Color.brand_green(),
        )
        no_foreign_language_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/english.png?raw=true"
        )

        no_flirting_embed = nextcord.Embed(
            title="No Flirting",
            description="Flirting is not allowed. This includes any form of romantic or sexual advances. This is not a dating server. If this behaviour is observed and involves a minor there will be serious consequences.",
            color=nextcord.Color.brand_green(),
        )
        no_flirting_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/flirting.png?raw=true"
        )

        no_venting_embed = nextcord.Embed(
            title="No Venting",
            description="The Crossroads is not your therapist's office. Keep venting to the topics covered by our various channels. If you need help, please reach out to a professional.",
            color=nextcord.Color.brand_green(),
        )
        no_venting_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/angry-face.png?raw=true"
        )

        respect_user_privacy_embed = nextcord.Embed(
            title="Respect User Privacy",
            description="Do not share personal information about others without their consent. This includes real names, addresses, phone numbers, and social media profiles. Remember that just because someone has shared something to a small group of people does not mean they want it shared with the entire server.",
            color=nextcord.Color.brand_green(),
        )
        respect_user_privacy_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/private-access.png?raw=true"
        )

        respect_moderator_decisions_embed = nextcord.Embed(
            title="Respect Moderator Decisions",
            description="We understand that you may not always agree with a moderator's decision. If you would like to discuss or appeal a decision, please do so in a Moderator Ticket. If an agreement cannot be reached with the moderator in this ticket it may be escalated to the Moderation Lead or Administration Team. Do not argue with a moderator in public channels about their decision. Do not DM a moderator to argue about their decision either, all appeals must be done in a ticket.",
            color=nextcord.Color.brand_green(),
        )
        respect_moderator_decisions_embed.set_thumbnail(
            "https://github.com/Yoshod/Sersi/blob/5.4.0/assets/embed_icons/shield.png?raw=true"
        )

        await ctx.send(
            embeds=[
                be_respectful_embed,
                no_bigotry_embed,
                no_nsfw_embed,
                no_spam_embed,
                no_slurs_embed,
                no_foreign_language_embed,
                no_flirting_embed,
                no_venting_embed,
                respect_user_privacy_embed,
                respect_moderator_decisions_embed,
            ]
        )

        await ctx.message.delete()


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Rules(bot, kwargs["config"]))
