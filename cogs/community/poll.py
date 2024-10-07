from datetime import datetime


import io
import nextcord
import nextcord.ui
import matplotlib.pyplot as plt
from nextcord.ext import commands
from matplotlib import colors

from utils.base import parse_timedelta
from utils.sersi_embed import SersiEmbed
from utils.config import Configuration
from utils.database import db_session, Poll, PollVote


class Choose(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config

    @nextcord.slash_command(
        dm_permission=False,
        guild_ids=[1166770860787515422, 977377117895536640, 856262303795380224],
    )
    async def poll(self, interaction: nextcord.Interaction):
        pass

    @poll.subcommand(description="Creates a poll")
    async def create(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(description="The question to ask"),
        multiple_choice: str = nextcord.SlashOption(
            name="type", choices={"Multiple Choice": "True", "Single Choice": ""}
        ),
        option1: str = nextcord.SlashOption(),
        option2: str = nextcord.SlashOption(),
        option3: str = nextcord.SlashOption(required=False),
        option4: str = nextcord.SlashOption(required=False),
        option5: str = nextcord.SlashOption(required=False),
        option6: str = nextcord.SlashOption(required=False),
        option7: str = nextcord.SlashOption(required=False),
        option8: str = nextcord.SlashOption(required=False),
        option9: str = nextcord.SlashOption(required=False),
        option10: str = nextcord.SlashOption(required=False),
        duration: int = nextcord.SlashOption(
            description="The duration of the poll",
            min_value=1,
            required=False,
        ),
        duration_unit: str = nextcord.SlashOption(
            description="The unit of the duration",
            choices={"Minutes": "m", "Hours": "h", "Days": "d"},
            required=False,
        ),
    ):
        await interaction.response.defer()

        options: list[str | None] = [
            option1,
            option2,
            option3,
            option4,
            option5,
            option6,
            option7,
            option8,
            option9,
            option10,
        ]
        while None in options:
            options.remove(None)

        if len(set(options)) < len(options):
            await interaction.send(
                f"{self.config.emotes.fail} Options must be unique.",
                ephemeral=True,
            )
            return

        selection = nextcord.ui.Select(
            custom_id="poll_vote",
            placeholder=f"Pick {'Multiple' if multiple_choice else 'One'}",
            options=[
                nextcord.SelectOption(
                    label=option, value=str(1 << index if multiple_choice else index),
                )
                for index, option in enumerate(options)
            ],
            max_values=len(options) if multiple_choice else 1,
        )

        dropdown_menu = nextcord.ui.View(timeout=None, auto_defer=False)
        dropdown_menu.add_item(selection)

        fields: dict[str:str] = {}
        for option in options:
            fields[option] = "*No Votes Yet*"

        poll = await interaction.send(
            embed=SersiEmbed(
                title=query,
                footer=f"Poll by {interaction.user.display_name}",
                fields=fields,
            ),
            view=dropdown_menu,
        )

        with db_session() as session:
            poll = Poll(
                poll_id=poll.id,
                poll_url=poll.jump_url,
                author=interaction.user.id,
                query=query,
                planned_end=datetime.now()
                + parse_timedelta(f"{duration or 1}{duration_unit or 'd'}"),
            )

            poll.opt_list = options

            session.add(poll)
            session.commit()

    @poll.subcommand(description="Ends a poll and displays the results")
    async def end(self, interaction: nextcord.Interaction, poll: int):
        if poll not in self.polls:
            await interaction.send(
                f"{self.config.emotes.fail} Poll not found.", ephemeral=True
            )
            return

        message = self.bot.get_channel(interaction.channel_id).get_partial_message(poll)
        await message.edit(view=None)

        await interaction.response.send_message(
            "Poll ended.",
            ephemeral=True,
        )

    @end.on_autocomplete("poll")
    async def autocomplete_poll(
        self, interaction: nextcord.Interaction, value: str
    ) -> list[str]:
        return [str(poll) for poll in [] if value in str(poll)]

    @commands.Cog.listener()
    async def on_interaction(self, interaction: nextcord.Interaction):
        if interaction.data is None or interaction.data.get("custom_id") is None:
            return

        if not interaction.data["custom_id"] == "poll_vote":
            return

        if not interaction.response.is_done():
            await interaction.response.defer(ephemeral=True)

        with db_session() as session:
            poll = (
                session.query(Poll).filter_by(poll_id=interaction.message.id).first()
            )
            if not poll:
                await interaction.send(
                    f"{self.config.emotes.fail} Poll not found.",
                    ephemeral=True,
                )
                return

            if (
                not poll.active
                or poll.planned_end
                and poll.planned_end < datetime.now()
            ):
                await interaction.send(
                    f"{self.config.emotes.fail} Poll has ended.",
                    ephemeral=True,
                )
                return

            vote = PollVote(
                poll_id=poll.poll_id,
                user_id=interaction.user.id,
                vote=sum([int(v) for v in interaction.data["values"]]),
            )

            session.merge(vote)
            session.commit()

            await interaction.send(
                f"{self.config.emotes.success} Vote registered.",
                ephemeral=True,
            )

            votes = session.query(PollVote).filter_by(poll_id=poll.poll_id).all()

        result_embed: nextcord.Embed = interaction.message.embeds[0]
        while result_embed.fields:
            result_embed.remove_field(0)

        all_votes: dict[str, int] = {option: 0 for option in poll.opt_list}
        for vote in votes:
            for index, option in enumerate(poll.opt_list):
                if poll.multiple and vote.vote & (1 << index):
                    all_votes[option] += 1
                elif not poll.multiple and vote.vote == index:
                    all_votes[option] += 1

        eval_bar_width: int = 20
        for option in poll.opt_list:
            percentage: float = all_votes[option] / len(votes)
            bar_filled: int = round(percentage * eval_bar_width)

            bar = f"{'█'*bar_filled}{'░'*(eval_bar_width-bar_filled)} {round(percentage*100, 2)}% ({all_votes[option]} votes)"

            result_embed.add_field(name=option, value=bar, inline=False)

        # make a graph using matplotlib
        poll_data = [all_votes[opt] for opt in poll.opt_list]

        label_gen = (label for label in poll.opt_list if all_votes[label] > 0)
        plt.figure(figsize=(4, 4))
        plt.pie(
            poll_data,
            colors=colors.TABLEAU_COLORS,
            autopct=lambda pct: f"{next(label_gen)}" if pct > 0 else "",
            startangle=90,
            counterclock=False,
            radius=1.2,
        )

        # make the background transparent
        plt.gca().set_facecolor("none")
        plt.gcf().set_facecolor("none")
        plt.gca().set_axis_off()
        plt.gca().set_xticks([])
        plt.gca().set_yticks([])
        plt.gca().set_frame_on(False)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        plt.close()
        buf.seek(0)

        result_embed.set_image(url="attachment://poll.png")

        await interaction.message.edit(
            embed=result_embed, file=nextcord.File(buf, filename="poll.png")
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Choose(bot, kwargs["config"]))
