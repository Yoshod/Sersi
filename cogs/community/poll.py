import io
import nextcord
import nextcord.ui
import matplotlib.pyplot as plt
from nextcord.ext import commands
from matplotlib import colors

from utils.sersi_embed import SersiEmbed
from utils.config import Configuration


class DropdownMenu(nextcord.ui.Select):
    def __init__(self, choices: list[str], max_values: int = 1):
        if max_values == 1:
            super().__init__(
                placeholder="Pick One",
                options=[nextcord.SelectOption(label=option) for option in choices],
            )
        else:
            super().__init__(
                placeholder="Pick Multiple",
                options=[nextcord.SelectOption(label=option) for option in choices],
            )
        self.state: dict[int : list[str]] = {}
        self.choices = choices
        self.max_values = max_values

    async def callback(self, interaction: nextcord.Interaction) -> None:
        self.state[interaction.id] = self.values

        result_embed: nextcord.Embed = interaction.message.embeds[0]
        while result_embed.fields:
            result_embed.remove_field(0)

        all_votes: list[str] = []
        for user_id in self.state:
            all_votes.extend(self.state[user_id])

        eval_bar_width: int = 20
        for option in self.choices:
            percentage: float = all_votes.count(option) / len(self.state)
            bar_filled: int = round(percentage * eval_bar_width)

            bar = f"{'█'*bar_filled}{'░'*(eval_bar_width-bar_filled)} {round(percentage*100, 2)}% ({all_votes.count(option)} votes)"

            result_embed.add_field(name=option, value=bar, inline=False)

        # make a graph using matplotlib
        poll_data = [all_votes.count(choice) for choice in self.choices]

        label_gen = (label for label in self.choices if all_votes.count(label) > 0)
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

        if multiple_choice:
            selection = DropdownMenu(options, len(options))
        else:
            selection = DropdownMenu(options)

        dropdown_menu = nextcord.ui.View(timeout=None)
        dropdown_menu.add_item(selection)

        fields: dict[str:str] = {}
        for option in options:
            fields[option] = "*No Votes Yet*"

        await interaction.send(
            embed=SersiEmbed(
                title=query,
                footer=f"Poll by {interaction.user.display_name}",
                fields=fields,
            ),
            view=dropdown_menu,
        )


def setup(bot: commands.Bot, **kwargs):
    bot.add_cog(Choose(bot, kwargs["config"]))
