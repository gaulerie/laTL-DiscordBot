import discord
from discord.ext import commands
import os  # Ajout de l'importation du module os
from commands import register_commands  # Importer la fonction pour enregistrer les commandes

print("Starting bot...")  # Log initial

# Remplacez ces valeurs par vos vrais tokens et clés API
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

register_commands(bot)  # Enregistrer les commandes

bot.run(DISCORD_TOKEN)
