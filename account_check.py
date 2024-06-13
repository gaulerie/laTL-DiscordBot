import requests
from requests_oauthlib import OAuth1
import os

# Récupérer les tokens et clés de l'environnement
API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')

# Assurez-vous que toutes les variables d'environnement sont correctement définies
if not all([API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
    raise Exception("One or more API keys are not set in the environment variables.")

# Configurer l'authentification OAuth1
auth = OAuth1(API_KEY, API_SECRET_KEY, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

def create_url(user_id):
    return f"https://api.twitter.com/2/users/{user_id}/tweets"

def get_params():
    return {"max_results": 20}

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=auth, params=params)
    print(f"URL: {url}, Status Code: {response.status_code}, Response: {response.text}")  # Message de débogage
    if response.status_code != 200:
        raise Exception(f"Request returned an error: {response.status_code} {response.text}")
    return response.json()

def fetch_tweets(user_id):
    url = create_url(user_id)
    params = get_params()
    return connect_to_endpoint(url, params)

def check_tweets(tweets):
    reject_keywords = ["faf", "facho", "🇵🇸"]
    for tweet in tweets:
        text = tweet.get("text", "").lower()
        if any(keyword in text for keyword in reject_keywords):
            return False
    return True

def check_following(user_handle):
    url = f"https://api.twitter.com/2/users/by/username/{user_handle}"
    response = requests.get(url, auth=auth)
    print(f"Fetching user ID, Status Code: {response.status_code}, Response: {response.text}")  # Message de débogage
    if response.status_code != 200:
        raise Exception(f"Error fetching user ID: {response.status_code} {response.text}")
    
    user_data = response.json()
    if 'data' not in user_data or 'id' not in user_data['data']:
        raise Exception(f"Error fetching user ID: Invalid response {response.text}")

    user_id = user_data["data"]["id"]

    url = f"https://api.twitter.com/2/users/{user_id}/following"
    response = requests.get(url, auth=auth)
    print(f"Fetching following list, Status Code: {response.status_code}, Response: {response.text}")  # Message de débogage
    if response.status_code != 200:
        raise Exception(f"Error fetching following list: {response.status_code} {response.text}")

    following_data = response.json()
    following = following_data.get("data", [])

    mutual_following = [user for user in following if user.get("username", "").lower() == "gaulerie"]
    return len(mutual_following) >= 50

def check_account(user_handle):
    if "🇫🇷" in user_handle or "🇦🇶" in user_handle:
        return True
    
    if check_following(user_handle):
        return True

    url = f"https://api.twitter.com/2/users/by/username/{user_handle}"
    response = requests.get(url, auth=auth)
    print(f"Fetching user ID for tweets, Status Code: {response.status_code}, Response: {response.text}")  # Message de débogage
    if response.status_code != 200:
        raise Exception(f"Error fetching user ID: {response.status_code} {response.text}")

    user_data = response.json()
    if 'data' not in user_data or 'id' not in user_data['data']:
        raise Exception(f"Error fetching user ID: Invalid response {response.text}")

    user_id = user_data["data"]["id"]

    print(f"URL: {create_url(user_id)}, Params: {get_params()}")
    if 'data' not in user_data or 'id' not in user_data['data']:
        print(f"Invalid response: {response.text}")
        raise Exception(f"Error fetching user ID: Invalid response {response.text}")

    tweets_response = fetch_tweets(user_id)
    tweets = tweets_response.get("data", [])
    return check_tweets(tweets)

print(f"API_KEY: {API_KEY}")
print(f"API_SECRET_KEY: {API_SECRET_KEY}")
print(f"ACCESS_TOKEN: {ACCESS_TOKEN}")
print(f"ACCESS_TOKEN_SECRET: {ACCESS_TOKEN_SECRET}")