import nextcord
import pickle
from nextcord.ext import commands

from baseutils import PageView, SersiEmbed
from caseutils import get_member_cases
from configutils import Configuration
from permutils import permcheck, is_mod


class Cases(commands.Cog):
    def __init__(self, bot: commands.Bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersifail = config.emotes.fail
        self.case_history_file = config.datafiles.casehistory
        self.case_details_file = config.datafiles.casedetails
        self.case_history = {}
        self.case_details = {}

    @commands.command(aliases=["c", "usercases", "modcases"])
    async def cases(self, ctx: commands.Context, search_term):
        if not await permcheck(ctx, is_mod):
            return

        member = await ctx.guild.get_member(search_term)

        if member:
            cases_embed = SersiEmbed(
                title=(f"{member.name}'s Cases"),
                colour=nextcord.Color.from_rgb(237, 91, 6),
            )
            cases_embed.set_thumbnail(url=member.display_avatar.url)

            view = PageView(
                config=self.config,
                base_embed=cases_embed,
                fetch_function=get_member_cases,
                author=ctx.author,
                entry_form="**__Case `{entry[0]}`__**: {entry[1]} <t:{entry[2]}>",
                member_id=member.id,
            )
            await view.send_embed(ctx.channel)
            with open(self.case_history_file, "rb") as file:
                self.case_history = pickle.load(file)

        elif not member:
            with open(self.case_details_file, "rb") as file:
                self.case_details = pickle.load(file)

            if search_term not in self.case_details:
                await ctx.send(f"{self.sersifail} Case {search_term} not found.")

            elif self.case_details[search_term][0] == "Reformation":
                user = ctx.guild.get_member(self.case_details[search_term][2])
                moderator = ctx.guild.get_member(self.case_details[search_term][3])
                reform_channel = ctx.guild.get_channel(
                    self.case_details[search_term][4]
                )

                case_embed = SersiEmbed(
                    title=f"__**Reformation Case {search_term}**__",
                    fields={
                        "User:": f"{user.mention} ({user.id})",
                        "Moderator:": f"{moderator.mention} ({moderator.id})",
                        "Reformation Case Number:": self.case_details[search_term][1],
                        "Reformation Channel:": f"{reform_channel.mention} ({reform_channel.id})",
                        "Reason:": self.case_details[search_term][5],
                        "Timestamp:": f"<t:{self.case_details[search_term][5]}:R>",
                    },
                )
                case_embed.set_thumbnail(url=user.display_avatar.url)

                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Probation":
                user = ctx.guild.get_member(self.case_details[search_term][1])
                initial_moderator = ctx.guild.get_member(
                    self.case_details[search_term][2]
                )
                approval_moderator = ctx.guild.get_member(
                    self.case_details[search_term][3]
                )

                case_embed = SersiEmbed(
                    title=f"__**Probation Case {search_term}**__",
                    fields={
                        "User:": f"{user.mention} ({user.id})",
                        "Initial Moderator:": f"{initial_moderator.mention} ({initial_moderator.id})",
                        "Approving Moderator:": f"{approval_moderator.mention} ({approval_moderator.id})",
                        "Reason:": self.case_details[search_term][4],
                        "Timestamp:": f"<t:{self.case_details[search_term][5]}:R>",
                    },
                )

                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Anonymous Message Mute":
                user = ctx.guild.get_member(self.case_details[search_term][1])
                moderator = ctx.guild.get_member(self.case_details[search_term][2])

                case_embed = SersiEmbed(
                    title=f"__**Anonymous Message Mute Case {search_term}**__",
                    fields={
                        "User:": f"{user.mention} ({user.id})",
                        "Moderator:": f"{moderator.mention} ({moderator.id})",
                        "Reason:": self.case_details[search_term][3],
                        "Timestamp:": f"<t:{self.case_details[search_term][4]}:R>",
                    },
                )

                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Slur Usage":
                user = ctx.guild.get_member(self.case_details[search_term][3])
                moderator = ctx.guild.get_member(self.case_details[search_term][4])

                case_embed = SersiEmbed(
                    title=f"__**Slur Usage Case {search_term}**__",
                    fields={
                        "User:": f"{user.mention} ({user.id})",
                        "Moderator:": f"{moderator.mention} ({moderator.id})",
                        "Slur Used:": self.case_details[search_term][1],
                        "Report URL:": self.case_details[search_term][2],
                        "Timestamp:": f"<t:{self.case_details[search_term][5]}:R>",
                    },
                )

                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Bad Faith Ping":
                user = ctx.guild.get_member(self.case_details[search_term][1])
                moderator = ctx.guild.get_member(self.case_details[search_term][3])

                case_embed = SersiEmbed(
                    title=f"__**Bad Faith Ping Case {search_term}**__",
                    fields={
                        "User:": f"{user.mention} ({user.id})",
                        "Moderator:": f"{moderator.mention} ({moderator.id})",
                        "Report URL:": self.case_details[search_term][2],
                        "Timestamp:": f"<t:{self.case_details[search_term][4]}:R>",
                    },
                )

                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            else:
                return


def setup(bot, **kwargs):
    bot.add_cog(Cases(bot, kwargs["config"]))
