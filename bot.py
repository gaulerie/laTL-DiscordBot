import discord
from discord.ext import commands, tasks
import os
from commands import register_commands, update_sheet, clean_verification_codes

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.message_content = True  # Ajoutez cette ligne

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)  # Désactiver la commande help par défaut

# Enregistrer les commandes
register_commands(bot)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    clean_verification_codes.start()

@bot.event
async def on_member_join(member):
    print(f'Member joined: {member}')
    update_sheet(member.id, '', verified=False)

# Démarrer le bot
bot.run(os.getenv('DISCORD_TOKEN'))
