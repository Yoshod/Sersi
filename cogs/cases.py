import nextcord
import pickle
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord.ext import commands
from os import remove

from baseutils import ConfirmView
from configutils import get_config_int, get_options, get_config
from permutils import permcheck, is_mod, cb_is_mod, is_custom_role


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
            with open(self.case_history_file, "rb") as file:
                self.case_history = pickle.load(file)
            try:
                cases = self.case_history[member.id]
                num_of_cases = len(cases)
                case_string = ""
                print(cases)
                for i in range(num_of_cases):
                    case_string = case_string + (f"**__Case {cases[i][0]}__**\n")
                    case_string = case_string + (f"Type: {cases[i][1]}\n\n")
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

def setup(bot):
    bot.add_cog(Cases(bot))
