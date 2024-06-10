import os
import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime, timedelta
import asyncio

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1249338900074201099  # Remplacez par l'ID du canal où vous voulez poster les mèmes
GITHUB_REPO = 'gaulerie/laTL-DiscordBot'
GITHUB_PATH = 'memes'
GITHUB_API_URL = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}'
GITHUB_RAW_URL = f'https://raw.githubusercontent.com/{GITHUB_REPO}/main/{GITHUB_PATH}'

intents = discord.Intents.default()
intents.messages = True

bot = commands.Bot(command_prefix='!', intents=intents)

sent_files = set()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await fetch_sent_files()
    post_meme.start()  # Démarre la tâche planifiée

async def fetch_sent_files():
    global sent_files
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        async for message in channel.history(limit=None):
            for attachment in message.attachments:
                sent_files.add(attachment.filename)
            if message.author == bot.user and message.content.startswith('**'):
                sent_files.add(message.content[2:-2])

def get_github_files():
    response = requests.get(GITHUB_API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        print(f'Failed to fetch files from GitHub: {response.status_code}')
        return []

@tasks.loop(hours=6)
async def post_meme():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print('Channel not found')
        return

    files = get_github_files()
    for file_info in files:
        filename = file_info['name']
        if filename in sent_files:
            continue

        file_url = f"{GITHUB_RAW_URL}/{filename}"
        file_response = requests.get(file_url)
        if file_response.status_code == 200:
            file_path = os.path.join('/tmp', filename)
            with open(file_path, 'wb') as f:
                f.write(file_response.content)

            try:
                await channel.send(content=f'**{filename}**', file=discord.File(file_path))
                await channel.send(content='▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂')
                sent_files.add(filename)
                os.remove(file_path)
                print(f'Sent {filename}')
                break
            except discord.errors.HTTPException as e:
                print(f'Failed to send {filename}: {e}')
        else:
            print(f'Failed to download {filename} from GitHub: {file_response.status_code}')

@post_meme.before_loop
async def before_post_meme():
    await bot.wait_until_ready()

bot.run(TOKEN)
