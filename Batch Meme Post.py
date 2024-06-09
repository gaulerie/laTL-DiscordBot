import os
import discord
from discord.ext import commands

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1249338900074201099  # Remplacez par l'ID du canal où vous voulez poster les mèmes
MEMES_FOLDER = 'D:\\MEGA\\民族主義\\Shitpost'  # Remplacez par le chemin de votre dossier de mèmes

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

def get_file_basename_without_extension(filename):
    return os.path.splitext(filename)[0]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        sent_files = set()
        async for message in channel.history(limit=None):  # Récupère tout l'historique des messages
            for attachment in message.attachments:
                sent_files.add(get_file_basename_without_extension(attachment.filename))
            if message.author == bot.user and message.content.startswith('**'):
                sent_files.add(message.content[2:-2])  # Ajoute le contenu du message en tant que fichier envoyé
        
        for root, dirs, files in os.walk(MEMES_FOLDER):
            for filename in files:
                file_basename = get_file_basename_without_extension(filename)
                if file_basename in sent_files:
                    print(f'Skipping {filename} (already sent)')
                    continue

                file_path = os.path.join(root, filename)
                if os.path.getsize(file_path) > 25 * 1024 * 1024:  # Vérifie si le fichier dépasse 25MB
                    print(f'Skipping {filename} (file too large)')
                    continue

                if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mp3')):
                    try:
                        await channel.send(content=f'**{file_basename}**', file=discord.File(file_path))
                        await channel.send(content='▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂')
                        print(f'Sent {filename}')
                    except discord.errors.HTTPException as e:
                        print(f'Failed to send {filename}: {e}')
    await bot.close()

bot.run(TOKEN)
