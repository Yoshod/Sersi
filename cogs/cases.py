import nextcord
import pickle
from nextcord.ext import commands
from nextcord.ui import Button, View
from os import remove

from baseutils import PageView
from caseutils import get_member_cases
from configutils import get_config
from permutils import permcheck, is_mod


class Cases(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.sersifail = get_config('EMOTES', 'fail')
        self.case_history_file = ("Files/Cases/casehistory.pkl")
        self.case_details_file = ("Files/Cases/casedetails.pkl")
        self.case_history = {}
        self.case_details = {}

    @commands.command(aliases=['c', 'usercases', 'modcases'])
    async def cases(self, ctx, search_term):
        if not permcheck(ctx, is_mod):
            return

        try:
            converter = commands.MemberConverter()
            print(converter)
            member = await converter.convert(ctx, search_term)
            search_by_member = True
            print(member)
        except commands.errors.MemberNotFound:
            search_by_member = False

        print(search_by_member)

        if search_by_member is True:
            cases_embed = nextcord.Embed(
                title=(f"{member.name}'s Cases"),
                colour=nextcord.Color.from_rgb(237, 91, 6))

            view = PageView(
                base_embed=cases_embed,
                fetch_function=get_member_cases,
                author=ctx.author,
                entry_form="**__Case `{entry[0]}`__**: {entry[1]} <t:{entry[2]}>",
                member_id=member.id)
            await view.send_embed(ctx.channel)
            with open(self.case_history_file, "rb") as file:
                self.case_history = pickle.load(file)
            try:
                cases = self.case_history[member.id]
                num_of_cases = len(cases)
                case_string = ""
                print(cases)
                for i, e in reversed(list(enumerate(cases))):
                    for x in range(1):
                        case_string = case_string + (f"**__Case {cases[i][0]}__**\n")
                        case_string = case_string + (f"Type: {cases[i][1]}\n")
                        case_string = case_string + (f"<t:{cases[search_term][i][2]}:R>\n\n")
                cases_embed = nextcord.Embed(
                    title=(f"{member.name}'s Cases ({num_of_cases})"),
                    description=(case_string),
                    colour=nextcord.Color.from_rgb(237, 91, 6)
                )
                cases_embed.set_thumbnail(url=member.display_avatar.url)
            except KeyError:
                cases_embed = nextcord.Embed(
                    title=(f"{member.name}'s Cases (0)"),
                    description=(f"{member.mention} ({member.id}) has no cases."),
                    colour=nextcord.Color.from_rgb(237, 91, 6)
                )
                cases_embed.set_thumbnail(url=member.display_avatar.url)
            await ctx.send(embed=cases_embed)

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
                case_embed.add_field(name="Timestamp:", value=(f"<t:{self.case_details[search_term][5]}:R>"), inline=False)
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

            else:
                return


def setup(bot):
    bot.add_cog(Cases(bot))
