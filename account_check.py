import requests
import os

BEARER_TOKEN = os.getenv('BEARER_TOKEN')
print(f"Bearer Token: {BEARER_TOKEN}")  # Message de débogage pour vérifier le token (attention à la sécurité)

def create_url(user_id):
    return f"https://api.twitter.com/2/users/{user_id}/tweets"

def get_params():
    return {"max_results": 20}

def bearer_oauth(r):
    r.headers["Authorization"] = f"Bearer {BEARER_TOKEN}"
    r.headers["User-Agent"] = "v2UserTweetsPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
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
        text = tweet["text"].lower()
        if any(keyword in text for keyword in reject_keywords):
            return False
    return True

def check_following(user_handle):
    url = f"https://api.twitter.com/2/users/by/username/{user_handle}"
    response = requests.get(url, auth=bearer_oauth)
    print(f"Fetching user ID, Status Code: {response.status_code}, Response: {response.text}")  # Message de débogage
    if response.status_code != 200:
        raise Exception(f"Error fetching user ID: {response.status_code} {response.text}")
    user_id = response.json()["data"]["id"]

    url = f"https://api.twitter.com/2/users/{user_id}/following"
    response = requests.get(url, auth=bearer_oauth)
    print(f"Fetching following list, Status Code: {response.status_code}, Response: {response.text}")  # Message de débogage
    if response.status_code != 200:
        raise Exception(f"Error fetching following list: {response.status_code} {response.text}")
    following = response.json()["data"]

    mutual_following = [user for user in following if user["username"].lower() == "gaulerie"]
    return len(mutual_following) >= 50

def check_account(user_handle):
    if "🇫🇷" in user_handle or "🇦🇶" in user_handle:
        return True
    
    if check_following(user_handle):
        return True

    url = f"https://api.twitter.com/2/users/by/username/{user_handle}"
    response = requests.get(url, auth=bearer_oauth)
    print(f"Fetching user ID for tweets, Status Code: {response.status_code}, Response: {response.text}")  # Message de débogage
    if response.status_code != 200:
        raise Exception(f"Error fetching user ID: {response.status_code} {response.text}")
    user_id = response.json()["data"]["id"]

    tweets = fetch_tweets(user_id)["data"]
    return check_tweets(tweets)
