import nextcord
import nextcord.ui
from nextcord.ext import commands
from utils.perms import is_admin, permcheck

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.database import (
    StarboardPosts,
    StarboardStars,
    db_session,
    StarboardIgnoredChannels,
)
from utils.starboard import check_if_starred


class Starboard(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.minimum_entry_stars = self.config.bot.minimum_star_count
        self.minimum_exit_stars = self.config.bot.minimum_star_count - 2
        self.starboard_channel = self.config.channels.misc.starboard

    @nextcord.slash_command(
        name="starboard",
        description="Starboard Configuration",
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def starboard(self, interaction: nextcord.Interaction):
        pass

    @starboard.subcommand(
        name="ignore",
        description="Ignore a channel from starboard",
    )
    async def ignore(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel,
    ):
        if not await permcheck(interaction, is_admin):
            return

        with db_session() as session:
            ignored_channel = StarboardIgnoredChannels(channel=channel.id)
            session.add(ignored_channel)
            session.commit()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Ignored {channel.mention} from starboard",
            ephemeral=True,
        )

    @starboard.subcommand(
        name="unignore",
        description="Unignore a channel from starboard",
    )
    async def unignore(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel,
    ):
        if not await permcheck(interaction, is_admin):
            return

        with db_session() as session:
            ignored_channel = (
                session.query(StarboardIgnoredChannels)
                .filter_by(channel=channel.id)
                .first()
            )

            if not ignored_channel:
                await interaction.response.send_message(
                    f"{self.config.emotes.fail} {channel.mention} is not ignored from starboard",
                    ephemeral=True,
                )
                return

            session.delete(ignored_channel)
            session.commit()

        await interaction.response.send_message(
            f"{self.config.emotes.success} Unignored {channel.mention} from starboard",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: nextcord.RawReactionActionEvent):
        if payload.emoji.name != "⭐":
            return

        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        with db_session() as session:
            if (
                session.query(StarboardIgnoredChannels)
                .filter_by(channel=channel.id)
                .first()
            ):
                await message.clear_reaction(payload.emoji)

                return

        if channel.id == self.starboard_channel:
            original_embed = message.embeds[0]
            star_id = original_embed.footer.text[:11]

            already_starred = check_if_starred(star_id, payload.user_id)

            if already_starred:
                await message.remove_reaction(payload.emoji, payload.member)
                return

            with db_session() as session:
                star = StarboardStars(
                    unique_id=star_id,
                    user=payload.user_id,
                    channel=channel.id,
                )
                session.add(star)
                session.commit()

                star_count = (
                    session.query(StarboardStars).filter_by(unique_id=star_id).count()
                )

            await message.edit(
                embed=original_embed.set_footer(text=f"{star_id} | ⭐ {star_count}")
            )
            return

        with db_session() as session:
            starboard_post = (
                session.query(StarboardPosts).filter_by(message=message.id).first()
            )

        if starboard_post:
            already_starred = check_if_starred(
                starboard_post.unique_id, payload.user_id
            )

            if already_starred:
                await message.remove_reaction(payload.emoji, payload.member)
                return

            with db_session() as session:
                star = StarboardStars(
                    unique_id=starboard_post.unique_id,
                    user=payload.user_id,
                    channel=message.channel.id,
                )
                session.add(star)
                session.commit()

                star_count = (
                    session.query(StarboardStars)
                    .filter_by(unique_id=starboard_post.unique_id)
                    .count()
                )

            starboard_message = await self.bot.get_channel(
                self.starboard_channel
            ).fetch_message(starboard_post.starboard_message)

            await starboard_message.edit(
                embed=starboard_message.embeds[0].set_footer(
                    text=f"{starboard_post.unique_id} | ⭐ {star_count}"
                )
            )

            self.bot.dispatch("add_xp", message.author, 100, "COMMUNITY")
            return

        star_count = message.reactions[0].count

        if star_count < self.minimum_entry_stars:
            return

        starboard_channel = self.bot.get_channel(self.starboard_channel)

        starboard_embed = SersiEmbed(
            title="Starboard Post",
            description=message.content,
            fields={
                "Original": f"[Jump!]({message.jump_url})",
            },
            footer=f"{message.id} | ⭐ {star_count}",
            author=message.author,
        )

        try:
            if message.attachments[0].content_type.startswith("image"):
                starboard_embed.set_image(url=message.attachments[0].url)

        except IndexError:
            pass

        starboard_message = await starboard_channel.send(embed=starboard_embed)

        with db_session() as session:
            starboard_post = StarboardPosts(
                message=message.id,
                starboard_message=starboard_message.id,
                author=message.author.id,
                channel=message.channel.id,
            )
            session.add(starboard_post)
            session.commit()

            starboard_post = (
                session.query(StarboardPosts).filter_by(message=message.id).first()
            )

            updated_embed = starboard_message.embeds[0]
            updated_embed.set_footer(
                text=f"{starboard_post.unique_id} | ⭐ {star_count}"
            )

            await starboard_message.edit(
                embed=updated_embed,
            )

            reactions = message.reactions
            for reaction in reactions:
                if reaction.emoji == "⭐":
                    users = await reaction.users().flatten()
                    break

            for user in users:
                star = StarboardStars(
                    unique_id=starboard_post.unique_id,
                    user=user.id,
                    channel=message.channel.id,
                )
                session.add(star)
                session.commit()

        await starboard_message.add_reaction("⭐")

        self.bot.dispatch("add_xp", message.author, 100 * star_count, "COMMUNITY")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: nextcord.RawReactionActionEvent):
        if payload.emoji.name != "⭐":
            return

        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if channel.id == self.starboard_channel:
            with db_session() as session:
                star_id = message.embeds[0].footer.text[:11]
                star = (
                    session.query(StarboardStars)
                    .filter_by(unique_id=star_id, user=payload.user_id)
                    .first()
                )

                if star.channel != channel.id:
                    return

                session.delete(star)
                session.commit()

                star_count = (
                    session.query(StarboardStars).filter_by(unique_id=star_id).count()
                )

            self.bot.dispatch("remove_xp", message.author, 100, "COMMUNITY")

            await message.edit(
                embed=message.embeds[0].set_footer(text=f"{star_id} | ⭐ {star_count}")
            )

            if star_count <= self.minimum_exit_stars:
                await message.delete()

                with db_session() as session:
                    session.delete(
                        session.query(StarboardPosts)
                        .filter_by(unique_id=star_id)
                        .first()
                    )
                    session.commit()

                    session.delete(
                        session.query(StarboardStars).filter_by(unique_id=star_id).all()
                    )
                    session.commit()

                self.bot.dispatch(
                    "remove_xp", message.author, 100 * star_count, "COMMUNITY"
                )

            return

        with db_session() as session:
            starboard_post = (
                session.query(StarboardPosts).filter_by(message=message.id).first()
            )

        if starboard_post:
            with db_session() as session:
                star_id = starboard_post.unique_id
                star = (
                    session.query(StarboardStars)
                    .filter_by(unique_id=star_id, user=payload.user_id)
                    .first()
                )

                if star.channel != channel.id:
                    return

                session.delete(star)
                session.commit()

                star_count = (
                    session.query(StarboardStars).filter_by(unique_id=star_id).count()
                )

            self.bot.dispatch("remove_xp", message.author, 100, "COMMUNITY")

            starboard_message = await self.bot.get_channel(
                self.starboard_channel
            ).fetch_message(starboard_post.starboard_message)

            await starboard_message.edit(
                embed=starboard_message.embeds[0].set_footer(
                    text=f"{star_id} | ⭐ {star_count}"
                )
            )

            if star_count <= self.minimum_exit_stars:
                await starboard_message.delete()

                with db_session() as session:
                    session.delete(
                        session.query(StarboardPosts)
                        .filter_by(unique_id=star_id)
                        .first()
                    )
                    session.commit()

                    session.delete(
                        session.query(StarboardStars).filter_by(unique_id=star_id).all()
                    )
                    session.commit()

                self.bot.dispatch(
                    "remove_xp", message.author, 100 * star_count, "COMMUNITY"
                )

            return


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Starboard(bot, kwargs["config"]))
