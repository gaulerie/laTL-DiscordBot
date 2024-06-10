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
commands_registered = False  # Flag pour vérifier si les commandes ont été enregistrées

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
    global commands_registered
    print(f'{bot.user.name} has connected to Discord!')
    if not commands_registered:
        clean_verification_codes = register_commands(bot)  # Enregistrer les commandes et obtenir la tâche
        clean_verification_codes.start()  # Démarrer la tâche
        commands_registered = True

@bot.event
async def on_disconnect():
    remove_lock()

try:
    bot.run(DISCORD_TOKEN)
finally:
    remove_lock()
