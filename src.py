import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import random

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

STATUS_ROTATION = [
    "over Woolwich British army",
    "over High Command",
    "over Intelligence Corps"
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    if not change_status_loop.is_running():
        change_status_loop.start()

@tasks.loop(seconds=20)
async def change_status_loop():
    status_name = STATUS_ROTATION[change_status_loop.current_loop % len(STATUS_ROTATION)]
    bot_activity = discord.Activity(
        type=discord.ActivityType.watching,
        name=status_name
    )
    await bot.change_presence(status=discord.Status.online, activity=bot_activity)

roasts = [
    "You look like poop", 
    "You stink", 
    "Yo mama so dumb she thought eating redbull will make her fly"
]

@bot.command()
async def roast(ctx, member: discord.Member):
    chosen_roast = random.choice(roasts)
    await ctx.send(f"{chosen_roast} {member.mention}")

ROLES = {
    "Army Staff": 1561268102203834378,
    "Academy Staff": 1561268399127142430,
    "Graduates": 1561268668552319006,
    "Academy Student": 1561268475622727750
}

@bot.command()
@commands.has_permissions(administrator=True)
async def role(ctx, member: discord.Member, *, role_name: str):
    if role_name not in ROLES:
        await ctx.send("Invalid role name. Please choose a valid group role.")
        return
        
    role_id = ROLES[role_name]
    role = ctx.guild.get_role(role_id)
    
    if role:
        await member.add_roles(role)
        await ctx.send(f"Successfully gave the role **{role.name}** to {member.mention}")
    else:
        await ctx.send("Role ID not found in this server.")

@bot.command(name="timeout")
@commands.has_permissions(moderate_members=True)
async def timeout_member(ctx, member: discord.Member, minutes: int, *, reason: str = "No reason provided"):
    if minutes <= 0:
        await ctx.send("Please specify a duration greater than 0 minutes.")
        return
        
    duration = datetime.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)
    await ctx.send(f"Successfully timed out **{member.display_name}** for {minutes} minutes. Reason: {reason}")

@timeout_member.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You need the `Moderate Members` permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!timeout @User [minutes] [reason]`")

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(1537790309570715648)
    if channel:
        await channel.send(f"Welcome {member.mention} Please read the rules they should be in the channel called rules. Type help to get more information.")

@bot.command()
async def help(ctx):
    help_embed = discord.Embed(title="Server Information", color=discord.Color.blue())
    if ctx.guild.icon:
        help_embed.set_thumbnail(url=ctx.guild.icon.url)
        
    help_embed.add_field(
        name="***Important Information***",
        value=(
            "\nThe server owner and Intelligence Director is **Roseanne_blink4**\n "
            "Everyone is to follow the rules and regulations, moderators will be watching for any rule breakers\n "
            "Any concerns regarding a threat or intel must be presented to the appropriate party."
        ),
        inline=False
    )
    await ctx.send(embed=help_embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"Banned {member} for {reason}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"Kicked {member} for {reason}")

questions = [
    "Who are you reporting? (include their roblox and discord username)",
    "Why are you reporting this person?",
    "Evidence must directly be sent to the Director. Say 'None' if you have no evidence. (say 'Yes' if you do)"
]

@bot.command()
async def report(ctx):
    user = ctx.author
    try:
        await ctx.reply("Please check your DMs for further instructions.", delete_after=5)
        dm = await user.create_dm()
        await dm.send("You have 5 minutes on each question. If you have evidence regarding your report then send it to the director.")
        
        answers = []
        def check(m):
            return m.author.id == user.id and isinstance(m.channel, discord.DMChannel)
            
        for i, question in enumerate(questions, start=1):
            await dm.send(f"Question {i}: {question}")
            try:
                msg = await bot.wait_for("message", check=check, timeout=300.0)
                answers.append({"question": question, "answer": msg.content})
            except asyncio.TimeoutError:
                await dm.send("You failed to reply within the given timeframe. This report has been automatically cancelled.")
                return
                
        await dm.send("Thank you for the report, a moderator will be with you shortly.")
        
        channel = bot.get_channel(1561186144534929438)
        if channel:
            embed = discord.Embed(
                title="New report submitted.",
                description=f"Submitted by {user} ({user.id})",
                color=discord.Color.blue()
            )
            for item in answers:
                embed.add_field(name=item['question'], value=item['answer'], inline=False)
            await channel.send(embed=embed)
            
    except discord.Forbidden:
        await ctx.reply("Please turn on your DMs and type the command again to continue.", delete_after=5)

class verifyButton(discord.ui.View):
  def __init__(self):
    super().__init__(timeout=None)
    
  @discord.ui.button(label="Verify Here", style=discord.ButtonStyle.blurple, custom_id="verifybtn")
  async def clicked(self, interaction: discord.Interaction, button: discord.ui.Button):
    role_id = 1562471613675475055
    guild = interaction.guild
    role = guild.get_role(role_id)
    await interaction.user.add_roles(role)
    await interaction.response.send_message("You have been verified.", ephemeral=True)
      
@bot.command()
async def deploy(ctx):
  await ctx.send("Click the button below to verify!", view=verifyButton())

@bot.command()
async def baan(ctx):
  embed = discord.Embed(
    title="Ban Command",
    description="Information about this command are as follows",
    color=discord.Color.blue()
    )
    
  embed.add_field(
    name="What the command does",
    value="When the command is triggered the bot checks for the mentioned user and checks their role, if the role is below the bot's the bot will complete the action by banning the user.",
    inline=False
    )
    
  embed.add_field(name="Abusing this command will result in strict disciplinary action taken towards the abuser.", value=None, inline=False)
  
  await ctx.send(embed=embed)

bot.run("Token here")
