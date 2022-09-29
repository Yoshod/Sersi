import nextcord
import pickle
from nextcord.ext import commands

from baseutils import PageView
from caseutils import get_member_cases
from configutils import Configuration
from permutils import permcheck, is_mod


class Cases(commands.Cog):

    def __init__(self, bot, config: Configuration):
        self.bot = bot
        self.config = config
        self.sersifail = config.emotes.fail
        self.case_history_file = config.datafiles.casehistory
        self.case_details_file = config.datafiles.casedetails
        self.case_history = {}
        self.case_details = {}

    @commands.command(aliases=['c', 'usercases', 'modcases'])
    async def cases(self, ctx, search_term):
        if not await permcheck(ctx, is_mod):
            return

        try:
            converter = commands.MemberConverter()
            member = await converter.convert(ctx, search_term)
            search_by_member = True
        except commands.errors.MemberNotFound:
            search_by_member = False

        if search_by_member is True:
            cases_embed = nextcord.Embed(
                title=(f"{member.name}'s Cases"),
                colour=nextcord.Color.from_rgb(237, 91, 6))
            cases_embed.set_thumbnail(url=member.display_avatar.url)

            view = PageView(
                config=self.config,
                base_embed=cases_embed,
                fetch_function=get_member_cases,
                author=ctx.author,
                entry_form="**__Case `{entry[0]}`__**: {entry[1]} <t:{entry[2]}>",
                member_id=member.id)
            await view.send_embed(ctx.channel)
            with open(self.case_history_file, "rb") as file:
                self.case_history = pickle.load(file)

        elif search_by_member is not True:

            with open(self.case_details_file, "rb") as file:
                self.case_details = pickle.load(file)

            if search_term not in self.case_details:
                ctx.send(f"{self.sersifail} Case {search_term} not found.")

            elif self.case_details[search_term][0] == "Reformation":
                case_embed = nextcord.Embed(
                    title=(f"__**Reformation Case {search_term}**__"),
                    colour=nextcord.Color.from_rgb(237, 91, 6)
                )

                user = ctx.guild.get_member(self.case_details[search_term][2])
                moderator = ctx.guild.get_member(self.case_details[search_term][3])
                reform_channel = ctx.guild.get_channel(self.case_details[search_term][4])

                case_embed.add_field(name="User:", value=(f"{user.mention} ({user.id})"), inline=False)
                case_embed.add_field(name="Moderator:", value=(f"{moderator.mention} ({moderator.id})"), inline=False)
                case_embed.add_field(name="Reformation Case Number:", value=self.case_details[search_term][1], inline=False)
                case_embed.add_field(name="Reformation Channel:", value=(f"{reform_channel.mention} ({reform_channel.id})"), inline=False)
                case_embed.add_field(name="Reason:", value=self.case_details[search_term][5], inline=False)
                case_embed.add_field(name="Timestamp:", value=(f"<t:{self.case_details[search_term][5]}:R>"), inline=False)
                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Probation":
                case_embed = nextcord.Embed(
                    title=(f"__**Probation Case {search_term}**__"),
                    colour=nextcord.Color.from_rgb(237, 91, 6)
                )

                user = ctx.guild.get_member(self.case_details[search_term][1])
                initial_moderator = ctx.guild.get_member(self.case_details[search_term][2])
                approval_moderator = ctx.guild.get_member(self.case_details[search_term][3])

                case_embed.add_field(name="User:", value=(f"{user.mention} ({user.id})"), inline=False)
                case_embed.add_field(name="Initial Moderator:", value=(f"{initial_moderator.mention} ({initial_moderator.id})"), inline=False)
                case_embed.add_field(name="Approving Moderator:", value=(f"{approval_moderator.mention} ({approval_moderator.id})"), inline=False)
                case_embed.add_field(name="Reason:", value=self.case_details[search_term][4], inline=False)
                case_embed.add_field(name="Timestamp:", value=(f"<t:{self.case_details[search_term][5]}:R>"), inline=False)
                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Anonymous Message Mute":
                case_embed = nextcord.Embed(
                    title=(f"__**Anonymous Message Mute Case {search_term}**__"),
                    colour=nextcord.Color.from_rgb(237, 91, 6)
                )

                user = ctx.guild.get_member(self.case_details[search_term][1])
                moderator = ctx.guild.get_member(self.case_details[search_term][2])

                case_embed.add_field(name="User:", value=(f"{user.mention} ({user.id})"), inline=False)
                case_embed.add_field(name="Moderator:", value=(f"{moderator.mention} ({moderator.id})"), inline=False)
                case_embed.add_field(name="Reason:", value=self.case_details[search_term][3], inline=False)
                case_embed.add_field(name="Timestamp:", value=(f"<t:{self.case_details[search_term][4]}:R>"), inline=False)
                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Slur Usage":
                case_embed = nextcord.Embed(
                    title=(f"__**Slur Usage Case {search_term}**__"),
                    colour=nextcord.Color.from_rgb(237, 91, 6)
                )

                user = ctx.guild.get_member(self.case_details[search_term][3])
                moderator = ctx.guild.get_member(self.case_details[search_term][4])

                case_embed.add_field(name="User:", value=(f"{user.mention} ({user.id})"), inline=False)
                case_embed.add_field(name="Moderator:", value=(f"{moderator.mention} ({moderator.id})"), inline=False)
                case_embed.add_field(name="Slur Used:", value=self.case_details[search_term][1], inline=False)
                case_embed.add_field(name="Report URL:", value=self.case_details[search_term][2], inline=False)
                case_embed.add_field(name="Timestamp:", value=(f"<t:{self.case_details[search_term][5]}:R>"), inline=False)
                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            elif self.case_details[search_term][0] == "Bad Faith Ping":
                case_embed = nextcord.Embed(
                    title=(f"__**Bad Faith Ping Case {search_term}**__"),
                    colour=nextcord.Color.from_rgb(237, 91, 6)
                )

                user = ctx.guild.get_member(self.case_details[search_term][1])
                moderator = ctx.guild.get_member(self.case_details[search_term][3])

                case_embed.add_field(name="User:", value=(f"{user.mention} ({user.id})"), inline=False)
                case_embed.add_field(name="Moderator:", value=(f"{moderator.mention} ({moderator.id})"), inline=False)
                case_embed.add_field(name="Report URL:", value=self.case_details[search_term][2], inline=False)
                case_embed.add_field(name="Timestamp:", value=(f"<t:{self.case_details[search_term][4]}:R>"), inline=False)
                case_embed.set_thumbnail(url=user.display_avatar.url)
                await ctx.send(embed=case_embed)

            else:
                return


def setup(bot, **kwargs):
    bot.add_cog(Cases(bot, kwargs["config"]))
