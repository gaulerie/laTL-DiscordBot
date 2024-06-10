import discord
from discord.ext import commands
import os
import sys
from commands import register_commands

print("Starting bot...")  # Log initial

# Remplacez ces valeurs par vos vrais tokens et clés API
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Verrouillage
lock_file = "/tmp/discord_bot.lock"

def check_and_create_lock():
    if os.path.exists(lock_file):
        print("Another instance is already running. Exiting.")
        sys.exit(1)
    with open(lock_file, 'w') as f:
        f.write(str(os.getpid()))

def remove_lock():
    if os.path.exists(lock_file):
        os.remove(lock_file)

check_and_create_lock()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_disconnect():
    remove_lock()

# Enregistrer les commandes
register_commands(bot)

try:
    bot.run(DISCORD_TOKEN)
finally:
    remove_lock()
