import nextcord

from nextcord.ext import commands

class Example(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # events
    @commands.Cog.listener()
    async def on_message(self, message):
        detected_slurs = detectSlur(message.content)

        if len(detected_slurs) > 0: #checks slur heat
		channel = bot.get_channel(getAlertChannel(message.guild.id))
		embedVar = nextcord.Embed(
			title="Slur(s) Detected", 
			description="A slur has been detected. Moderation action is advised.\n\n__Channel:__\n"
				+str(message.channel.mention)
				+"\n\n__User:__\n"
				+str(message.author.mention)
				+"\n\n__Context:__\n"
				+str(message.content)
				+"\n\n__Slurs Found:__\n"
				+str(detected_slurs)
				+"\n\n__URL:__\n"
				+str(message.jump_url), 
			color=nextcord.Color.from_rgb(237,91,6))
		embedVar.set_footer(text="Slur detection written by Hekkland and Melanie")

		action_taken = Button(label="Action Taken")
		action_taken.callback = cb_action_taken
		
		acceptable_use = Button(label="Acceptable Use")
		acceptable_use.callback = cb_acceptable_use

		false_positive = Button(label="False Positive")
		false_positive.callback = cb_false_positive

		button_view = View()
		button_view.add_item(action_taken)
		button_view.add_item(acceptable_use)
		button_view.add_item(false_positive)

		await channel.send(embed=embedVar, view=button_view)
    
    # command
    @commands.command()
    async def cog(self, ctx):
        await ctx.send("Cog command test")

def setup(bot):
    bot.add_cog(Example(bot))