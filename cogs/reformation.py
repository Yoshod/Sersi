import nextcord
from nextcord.ext import commands
from nextcord.ui import Button, View
from nextcord.ext.commands.errors import MemberNotFound
from baseutils import *

class Reformation(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
	# command
	@commands.command()
	async def rn(self, ctx, member: nextcord.Member, *args):
		"""Reform Needed.
		
		Sends a user to reformation centre for reform by giving said user the @Reformation role. Removes @Civil Engineering Initiate and all Opt-In-Roles.
		Permission Needed: Moderator, Trial Moderator
		"""
		if isMod(ctx.author.roles):
			try:
				reason_string = " ".join(args)
				reformation_role = ctx.guild.get_role(getReformationRole(ctx.guild.id))
				
				await member.add_roles(reformation_role, reason=reason_string, atomic=True)
				try:
					role_ids = [878040658244403253, 960558372837523476, 960558399471378483,
								960558452109885450, 960558507403382784, 960558557332406293,
								960558615209582672, 960558657672732712, 960558722839642212,
								960558757463605298, 960558800442646578, 960558452109885450,
								902291483040837684]
					for role in role_ids:
						await member.remove_roles(ctx.guild.get_role(role), reason=reason_string, atomic=True)
				except AttributeError:
					await ctx.reply("Could not remove roles.")
				
				await ctx.send(f"Memeber {member.mention} has been sent to reformation by {ctx.author.mention} for reson: {reason_string}")

				##LOGGING
				embedLogVar = nextcord.Embed(
					title="User Has Been Sent to Reformation", 
					description = f"Moderator {ctx.author.mention} ({ctx.author.id}) has sent user {member.mention} ({member.id}) to reformation.\n\n"
								 +f"**__Reason:__** {reason_string}",
					color=nextcord.Color.from_rgb(237,91,6))
				
				channel = self.bot.get_channel(getLoggingChannel(ctx.guild.id))
				await channel.send(embed=embedLogVar)

				channel = self.bot.get_channel(getModlogsChannel(ctx.guild.id))
				await channel.send(embed=embedLogVar)

			except MemberNotFound:
				await ctx.send("Member not found!")
		else:
			ctx.reply("__**No Permissions**__\nTo get the issue investigates, please open a Mod-Ticket or ping @moderator.")

	async def cb_yes(self, interaction):
		if isMod(interaction.user.roles):
			new_embed = interaction.message.embeds[0]
			#check if user has already voted
			for field in new_embed.fields:
				if field.value == interaction.user.mention:
					await interaction.response.send_message("You already voted", ephemeral=True)
					return 

			#make vote visible
			new_embed.add_field(name="Voted Yes:", value=interaction.user.mention, inline=True)
			#retrieve current amount of votes and iterate by 1
			yes_votes = new_embed.description[-1]
			yes_votes = int(yes_votes) + 1
			
			#automatically releases inmate at 3 yes votes
			if (yes_votes >= 3):

				#get member object of member to be released
				member_string	= new_embed.footer.text
				member_id		= int(member_string)
				member			= interaction.guild.get_member(member_id)
				
				#fetch yes voters
				yes_men = []
				for field in new_embed.fields:
					if field.name == "Voted Yes:":
						yes_men.append(field.value)
				
				#roles
				try:
					civil_enginerring_initiate	= interaction.guild.get_role(878040658244403253)
					reformed					= interaction.guild.get_role(878289678623703080)
					await member.add_roles(civil_enginerring_initiate, reformed, reason="Released out of the Reformation Centre", atomic=True)
				except AttributeError:
					await interaction.send("Could not assign roles.")		
				await member.remove_roles(interaction.guild.get_role(getReformationRole(interaction.guild.id)), reason="Released out of the Reformation Centre", atomic=True)
				
				#logs
				log_embed = nextcord.Embed(
					title=f"Release: **{member.name}** ({member.id})", 
					description=f"Reformation Inmate {member.name} was deemed well enough to be released back into the server.\n"
								+f"Release has been approved by {', '.join(yes_men)}\n",
					color=nextcord.Color.from_rgb(237,91,6))
				channel = self.bot.get_channel(getModlogsChannel(interaction.guild.id))
				await channel.send(embed=log_embed)
				await interaction.send(f"**{member.name}** ({member.id}) will now be freed.")
				
				#updates embed and removed buttons
				await interaction.message.edit(embed=new_embed, view=None)
			new_embed.description = f"{new_embed.description[:-1]}{yes_votes}"
			await interaction.message.edit(embed=new_embed)
	
	async def cb_no(self, interaction):
		if isMod(interaction.user.roles):
			new_embed = interaction.message.embeds[0]
			#check if user has already voted
			for field in new_embed.fields:
				if field.value == interaction.user.mention:
					await interaction.response.send_message("You already voted", ephemeral=True)
					return 
			
			#make vote visible
			new_embed.add_field(name="Voted No:", value=interaction.user.mention, inline=True)
	
	async def cb_maybe(self, interaction):
		if isMod(interaction.user.roles):
			new_embed = interaction.message.embeds[0]
			#check if user has already voted
			for field in new_embed.fields:
				if field.value == interaction.user.mention:
					await interaction.response.send_message("You already voted", ephemeral=True)
					return 

			#make vote visible
			new_embed.add_field(name="Voted Maybe:", value=interaction.user.mention, inline=True)
	
	@commands.command()  
	async def rq(self, ctx, member: nextcord.Member):
		"""Reformation Query.
		
		Sends query for releaso out of reformation centre for [member] into the information centre.
		Three 'Yes' votes will result in an automatic release.
		"""
		if isMod(ctx.author.roles):
			try:
				embedVar = nextcord.Embed(
					title=f"Reformation Query: **{member.name}** ({member.id})", 
					description=f"Reformation Inmate {member.name} was deemed well enough to start a query about their release\n"
								+f"Query started by {ctx.author.mention} ({ctx.author.id})\n\n"
								+f"Yes Votes: 0",
					color=nextcord.Color.from_rgb(237,91,6))
				embedVar.set_footer(text=f"{member.id}")
			except MemberNotFound:
				await ctx.send("Member not found!")
				
			yes = Button(label="Yes", style=nextcord.ButtonStyle.green)
			yes.callback = self.cb_yes
		
			no = Button(label="No", style=nextcord.ButtonStyle.red)
			no.callback = self.cb_no

			maybe = Button(label="Maybe")
			maybe.callback = self.cb_maybe

			button_view = View(timeout=None)
			button_view.add_item(yes)
			button_view.add_item(no)
			button_view.add_item(maybe)

			channel = self.bot.get_channel(getAlertChannel(ctx.guild.id))
			await channel.send(embed=embedVar, view=button_view)
			
		else:
			ctx.reply("Only Moderators can start Reformation Queries.")
	
	async def cb_done(self, interaction):
		if isMod(interaction.user.roles):
			embed = interaction.message.embeds[0]
			embed.add_field(name="User was or is banned:", value=interaction.user.mention, inline=True)
			embed.color=nextcord.Color.from_rgb(0,255,0)
			await interaction.message.edit(embed=embed)
		
	
	@commands.Cog.listener()
	async def on_member_remove(self, member):
		print(f"Member {member} has left the server")
		
		reformation_role = member.get_role(getReformationRole(member.guild.id))
		print(reformation_role)
		
		if reformation_role != None:
			channel = self.bot.get_channel(getAlertChannel(member.guild.id))
			embed = nextcord.Embed(
				title=f"User **{member}** ({member.id}) has left the server while in the reformation centre!", 
				description=f"User has left the server while having the @reformation role. If they have not been banned, they should be hack-banned using wick now.",
				color=nextcord.Color.from_rgb(255,255,0))
			done = Button(label="User was or is banned", style=nextcord.ButtonStyle.green)
			done.callback = self.cb_done
			button_view = View(timeout=None)
			button_view.add_item(done)
			await channel.send(embed=embed, view=button_view)

def setup(bot):
	bot.add_cog(Reformation(bot))