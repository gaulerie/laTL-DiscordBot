import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime, timedelta
import random
import string
import html
import re
import os
from bs4 import BeautifulSoup

verification_codes = {}

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def update_sheet(discord_id, twitter_handle, verified=False, left_date='', roles=''):
    join_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'discord_id': discord_id,
        'twitter_handle': twitter_handle,
        'join_date': join_date,
        'leave_date': left_date,
        'verified': verified,
        'roles': roles
    }
    SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwi3Gh5TuK2IZV2R8imZa-B2m8gZpzByRfKHvMWxwHXffkNuIJ99OyISnYWfazhK7JHng/exec'
    response = requests.post(SCRIPT_URL, json=data)
    if response.status_code != 200:
        print(f"Failed to update sheet: {response.status_code}")
        print(response.text)
    else:
        print("Data successfully sent to Google Sheets")

@tasks.loop(minutes=1)
async def clean_verification_codes():
    current_time = datetime.now()
    expired_codes = [user_id for user_id, (_, _, expiration_time) in verification_codes.items() if current_time > expiration_time]
    for user_id in expired_codes:
        del verification_codes[user_id]

def get_user_roles(member):
    return '; '.join([role.name for role in member.roles if role.name != "@everyone"])

def register_commands(bot):
    @bot.command(name='help')
    async def help_command(ctx):
        help_text = """
        **Commandes disponibles :**
        `!verify [@ Twitter]` - Démarre le processus de vérification.
        `!check [lien du tweet]` - Vérifie le tweet avec le code de vérification.
        `!clear [nombre de messages]` - Supprime le nombre spécifié de messages dans le canal.
        """
        await ctx.send(help_text)

    @bot.command(name='clear')
    @commands.has_permissions(manage_messages=True)
    async def clear(ctx, amount: int):
        if str(ctx.channel) in ['shitpost', 'memes']:
            await ctx.send("La commande !clear ne peut pas être utilisée dans ce canal.")
            return
        
        if amount < 1:
            await ctx.send("Le nombre de messages à supprimer doit être supérieur à 0.")
            return
        
        def not_pinned(message):
            return not message.pinned

        deleted = await ctx.channel.purge(limit=amount + 1, check=not_pinned)  # +1 pour inclure la commande elle-même
        deleted_count = len(deleted)  # Nombre total de messages supprimés, y compris la commande elle-même
        await ctx.send(f"{deleted_count - 1} messages ont été supprimés.", delete_after=5)  # -1 pour exclure la commande elle-même

    @bot.command(name='verify')
    async def verify(ctx, twitter_handle: str = None):
        if not twitter_handle:
            await ctx.send("Veuillez écrire !verify [@ Twitter]")
            return

        twitter_handle = twitter_handle.strip('@').lower()
        code = generate_verification_code()
        expiration_time = datetime.now() + timedelta(minutes=5)
        verification_codes[ctx.author.id] = (twitter_handle, code, expiration_time)
        await ctx.send(f"Veuillez tweeter le code suivant depuis votre compte Twitter @{twitter_handle} avec le hashtag #VerificationCode: {code}. Ce code expirera dans 5 minutes.")

    @bot.command(name='check')
    async def check(ctx, tweet_url: str = None):
        if not tweet_url:
            await ctx.send("Veuillez écrire !check [lien du tweet]")
            return

        try:
            response = requests.get(f"https://publish.twitter.com/oembed?url={tweet_url}")
            tweet_data = response.json()

            if response.status_code == 200:
                tweet_html = tweet_data['html']
                print(f"HTML du tweet: {tweet_html}")

                # Décoder les entités HTML
                tweet_html = html.unescape(tweet_html)

                # Extraire le texte du tweet pour vérifier le code de vérification
                soup = BeautifulSoup(tweet_html, 'html.parser')
                tweet_text = soup.get_text()
                print(f"Texte du tweet: {tweet_text}")

                # Vérifiez si le code de vérification est présent dans le texte du tweet
                match = re.search(r'#VerificationCode:\s?([A-Z0-9]+)', tweet_text, re.IGNORECASE)
                if match:
                    code_in_tweet = match.group(1).upper()
                    print(f"Code trouvé dans le tweet: {code_in_tweet}")

                    if ctx.author.id in verification_codes:
                        expected_code = verification_codes[ctx.author.id][1]
                        print(f"Code attendu: {expected_code}")

                        if code_in_tweet == expected_code:
                            # await ctx.send(f"Le code de vérification {code_in_tweet} a été trouvé dans le tweet et est correct.")
                            
                            # Appliquer le nouveau rôle et retirer l'ancien
                            role_verified = discord.utils.get(ctx.guild.roles, name='Congolais 🔪')
                            role_non_verified = discord.utils.get(ctx.guild.roles, name='Non Vérifié')
                            if role_verified and role_non_verified:
                                await ctx.author.add_roles(role_verified)
                                await ctx.author.remove_roles(role_non_verified)

                            # Mettre à jour la feuille Google
                            roles = get_user_roles(ctx.author)
                            update_sheet(ctx.author.id, verification_codes[ctx.author.id][0], verified=True, roles=roles)

                            # Supprimer les messages de vérification de l'utilisateur et du bot
                            await purge_user_messages(ctx.channel, ctx.author.id)

                            # Renommer l'utilisateur avec son handle Twitter
                            twitter_handle = verification_codes[ctx.author.id][0]
                            new_nickname = f"@{twitter_handle}"
                            
                            try:
                                await ctx.author.edit(nick=new_nickname)
                            except discord.Forbidden:
                                await ctx.send("Je n'ai pas la permission de changer votre surnom. Veuillez vérifier les permissions du bot et la hiérarchie des rôles.")

                            # Suppression du code de vérification après utilisation
                            del verification_codes[ctx.author.id]
                        else:
                            await ctx.send("Le code de vérification dans le tweet ne correspond pas au code attendu.")
                    else:
                        await ctx.send("Aucun code de vérification en attente pour cet utilisateur.")
                else:
                    await ctx.send("Le tweet ne contient pas le code de vérification.")
            else:
                await ctx.send(f"Erreur lors de l'accès au tweet: {response.status_code}")
        except Exception as e:
            await ctx.send(f"Erreur lors de l'accès au tweet: {str(e)}")

    @bot.command(name='testaccount')
    async def test_account_command(ctx):
        user_handle = 'gaulerie'
        await ctx.send(f"Testing account for {user_handle}")

    async def purge_user_messages(channel, user_id):
        def check(m):
            return (m.author.id == user_id or (m.author == bot.user and "#VerificationCode:" in m.content)) and not m.pinned

        deleted = await channel.purge(limit=100, check=check)
        print(f"Deleted {len(deleted)} messages")

    @bot.event
    async def on_member_join(member):
        print(f'Member joined: {member}')
        update_sheet(member.id, '', verified=False, roles=get_user_roles(member))

    @bot.event
    async def on_member_update(before, after):
        if before.roles != after.roles:
            roles = get_user_roles(after)
            update_sheet(after.id, '', roles=roles)

    return clean_verification_codes  # Retourner la tâche pour qu'elle soit démarrée dans bot.py

# Here you would set up the bot and start the loop
bot = commands.Bot(command_prefix='!')

clean_verification_codes_task = register_commands(bot)
clean_verification_codes_task.start()

bot.run('YOUR_BOT_TOKEN')
