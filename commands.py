import discord
from discord.ext import commands, tasks
import requests
from datetime import datetime, timedelta
import random
import string
import html
import re

verification_codes = {}

def generate_verification_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def update_sheet(discord_id, twitter_handle, verified=False, left_date=''):
    join_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data = {
        'discord_id': discord_id,
        'twitter_handle': twitter_handle,
        'join_date': join_date,
        'leave_date': left_date,
        'verified': verified
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

        # Vérifier si l'utilisateur a entré une URL au lieu d'un pseudo Twitter
        if re.match(r'^https?://(www\.)?(twitter|x)\.com/[A-Za-z0-9_]+/status/[0-9]+$', twitter_handle):
            await ctx.send("Pour vérifier un lien, utilisez !check [lien]")
            return

        # Enlever les crochets autour du pseudo si présents
        if twitter_handle.startswith('[') and twitter_handle.endswith(']'):
            twitter_handle = twitter_handle[1:-1]

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

        # Vérifier si l'utilisateur a entré un pseudo Twitter au lieu d'un lien
        if not re.match(r'^https?://(www\.)?(twitter|x)\.com/[A-Za-z0-9_]+/status/[0-9]+$', tweet_url):
            await ctx.send("Pour vérifier votre compte, utilisez !verify [pseudo]")
            return

        if ctx.author.id not in verification_codes:
            await ctx.send("Vous n'avez pas encore demandé de vérification. Utilisez !verify <votre_handle_twitter>")
            return

        twitter_handle, code, expiration_time = verification_codes[ctx.author.id]

        if datetime.now() > expiration_time:
            del verification_codes[ctx.author.id]
            await ctx.send("Le code de vérification a expiré. Veuillez recommencer le processus de vérification.")
            return

        try:
            response = requests.get(f"https://publish.twitter.com/oembed?url={tweet_url}")
            tweet_data = response.json()
            
            if response.status_code == 200:
                tweet_html = tweet_data['html']
                print(f"HTML du tweet: {tweet_html}")  # Impression pour débogage

                # Décoder les entités HTML
                tweet_html = html.unescape(tweet_html)
                
                # Extraction du handle Twitter depuis le HTML
                match = re.search(r'\(@([^)]+)\)', tweet_html)
                if match:
                    extracted_handle = match.group(1).lower()
                    print(f"Handle extrait: {extracted_handle}")
                    print(f"Handle attendu: {twitter_handle}")
                    print(f"Code attendu: {code}")
                    
                    # Vérifiez si le handle Twitter et le code de vérification sont présents dans le HTML du tweet
                    if extracted_handle == twitter_handle and code.lower() in tweet_html.lower():
                        print("Handle et code vérifiés avec succès.")
                        role_verified = discord.utils.get(ctx.guild.roles, name='Membre')
                        role_non_verified = discord.utils.get(ctx.guild.roles, name='Non Vérifié')
                        if role_verified and role_non_verified:
                            await ctx.author.add_roles(role_verified)
                            await ctx.author.remove_roles(role_non_verified)
                            update_sheet(ctx.author.id, twitter_handle, verified=True)
                            await purge_user_messages(ctx.channel, ctx.author.id)
                            await ctx.send(f"Utilisateur {ctx.author.mention} vérifié et rôle 'Membre' attribué.")
                            del verification_codes[ctx.author.id]
                            return
                    else:
                        print("Le handle ou le code ne correspondent pas.")
                await ctx.send("Le tweet ne contient pas le code de vérification ou n'a pas été tweeté par le bon utilisateur. Veuillez réessayer.")
            else:
                await ctx.send(f"Erreur lors de l'accès au tweet: {response.status_code}")
        except Exception as e:
            await ctx.send(f"Erreur lors de l'accès au tweet: {str(e)}")

    async def purge_user_messages(channel, user_id):
        def check(m):
            return m.author.id == user_id or (m.author == bot.user and not any(role.name == 'Admin' for role in m.author.roles))
        
        deleted = await channel.purge(limit=100, check=check)
        print(f"Deleted {len(deleted)} messages")

def start_clean_verification_codes():
    clean_verification_codes.start()
