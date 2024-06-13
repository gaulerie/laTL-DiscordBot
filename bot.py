import discord
from discord.ext import commands
import os
from commands import register_commands, update_sheet, start_clean_verification_codes

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# Enregistrer les commandes
register_commands(bot)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    start_clean_verification_codes()

@bot.event
async def on_member_join(member):
    print(f'Member joined: {member}')
    update_sheet(member.id, '', verified=False)

# @bot.event
# async def on_member_remove(member):
#     print(f'Member left: {member}')
#     update_sheet(member.id, '', left_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Lancement du bot
bot.run(os.getenv('DISCORD_TOKEN'))
