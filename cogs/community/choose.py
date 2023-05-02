import nextcord
import nextcord.ui
from nextcord.ext import commands

from utils.baseutils import SersiEmbed
from utils.configutils import Configuration


class DropdownMenu(nextcord.ui.Select):
    def __init__(self, choices: list[nextcord.SelectOption]):
        super().__init__(placeholder="Pick One", options=choices)

    async def callback(self, interaction: nextcord.Interaction) -> None:
        await interaction.send(f"{self.values}")


class Choose(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.emotes: list[str] = [
            "1️⃣",
            "2️⃣",
            "3️⃣",
            "4️⃣",
            "5️⃣",
            "6️⃣",
            "7️⃣",
            "8️⃣",
            "9️⃣",
            "🔟",
        ]
        self.filled: str = "█"
        self.empty: str = "░"

    @nextcord.slash_command(
        dm_permission=False, guild_ids=[977377117895536640, 856262303795380224]
    )
    async def choose(self, interaction: nextcord.Interaction):
        pass

    @choose.subcommand(description="Creates a poll")
    async def create(
        self,
        interaction: nextcord.Interaction,
        query: str = nextcord.SlashOption(description="The question to ask"),
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

        primitive_options: list[str | None] = [
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
        while None in primitive_options:
            primitive_options.remove(None)

        options: list[nextcord.SelectOption] = []
        for option in primitive_options:
            options.append(nextcord.SelectOption(label=option))

        selection = nextcord.ui.Select(placeholder="Pick One", options=options)

        dropdown_menu = nextcord.ui.View(timeout=None)
        dropdown_menu.add_item(selection)

        poll: nextcord.Message = await interaction.send(
            embed=SersiEmbed(
                title=query,
                footer=f"Poll by {interaction.user.display_name}",
            ),
            view=dropdown_menu,
        )

        counter: int = 0
        for option in primitive_options:
            await poll.add_reaction(self.emotes[counter])
            counter += 1

    @choose.subcommand(description="Shows the result of a past poll")
    async def evaluate(
        self,
        interaction: nextcord.Interaction,
        message_id: str = nextcord.SlashOption(
            description="the message ID of the poll"
        ),
    ):
        eval_bar_width: int = 20

        await interaction.response.defer()

        try:
            message: nextcord.Message = await interaction.channel.fetch_message(
                int(message_id)
            )
        except nextcord.NotFound:
            await interaction.send(
                embed=SersiEmbed(
                    title=f"{self.config.emotes.fail} Message not found!",
                    description="Please note that this command needs to be run in the same channel as the poll is in.",
                    footer="Sersi Poll",
                ),
                ephemeral=True,
            )
            return
        except nextcord.Forbidden:
            await interaction.send(
                embed=SersiEmbed(
                    title=f"{self.config.emotes.fail} Forbidden!", footer="Sersi Poll"
                ),
                ephemeral=True,
            )
            return
        except nextcord.HTTPException:
            await interaction.send(
                embed=SersiEmbed(
                    title=f"{self.config.emotes.fail} Something went wrong!",
                    footer="Sersi Poll",
                ),
                ephemeral=True,
            )
            return

        poll: nextcord.Embed = message.embeds[0]
        options: list[str] = [
            option.split(" ", maxsplit=1)[1]
            for option in poll.description.split("\n\n")
        ]

        counter: int = 0
        total_votes: int = 0
        results: dict[str:int] = {}
        for option in options:
            reaction: nextcord.Reaction = message.reactions[counter]

            # one, two, three...
            results[option] = reaction.count - 1
            total_votes += reaction.count - 1

            counter += 1

        if total_votes == 0:
            await interaction.send(
                embed=SersiEmbed(
                    title=f"{self.config.emotes.fail} Cannot evaluate poll with no votes!"
                ),
                ephemeral=True,
            )
            return

        result_embed: nextcord.Embed = SersiEmbed(
            title=f"{poll.title} ({total_votes} votes)",
            footer=f"Results of Poll {message_id}",
        )

        for result in results:
            percentage: float = results[result] / total_votes
            bar_filled: int = round(percentage * eval_bar_width)
            bar = f"{self.filled*bar_filled}{self.empty*(eval_bar_width-bar_filled)} {percentage*100}% ({results[result]} votes)"

            result_embed.add_field(name=result, value=bar, inline=False)

        await interaction.send(embed=result_embed)


def setup(bot, **kwargs):
    bot.add_cog(Choose(bot, kwargs["config"]))
