import requests
from bs4 import BeautifulSoup
import re

def fetch_tweets(user_handle):
    url = f"https://twitter.com/{user_handle}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    print(f"Fetching tweets for {user_handle}, Status Code: {response.status_code}")  # Log de débogage
    if response.status_code != 200:
        raise Exception(f"Error fetching tweets: {response.status_code} {response.text}")

    soup = BeautifulSoup(response.text, 'html.parser')
    tweets = []

    for tweet in soup.find_all('div', {'data-testid': 'tweet'}):
        print(f"Tweet HTML: {tweet}")  # Log de la structure HTML du tweet
        tweet_text = tweet.find('div', {'lang': True})
        if tweet_text:
            tweets.append(tweet_text.get_text())
            print(f"Tweet fetched: {tweet_text.get_text()}")  # Log de chaque tweet trouvé
        else:
            print("No text found for a tweet, skipping it.")  # Log si aucun texte n'est trouvé

    print(f"Fetched {len(tweets)} tweets for {user_handle}")  # Log de débogage

    return tweets

def check_tweets(tweets):
    reject_keywords = ["faf", "facho", "🇵🇸"]
    keyword_counts = {keyword: 0 for keyword in reject_keywords}
    for tweet in tweets:
        text = tweet.lower()
        for keyword in reject_keywords:
            if keyword in text:
                keyword_counts[keyword] += 1
                print(f"Keyword '{keyword}' found in tweet: {tweet}")  # Log de chaque occurrence de mot-clé

    for keyword, count in keyword_counts.items():
        print(f"Occurrences of '{keyword}': {count}")  # Log de débogage

    passed = all(count == 0 for count in keyword_counts.values())
    return passed, keyword_counts

def check_following(user_handle):
    print(f"Checking following for {user_handle}")  # Log de débogage
    # Here you would implement the actual following check logic
    # For now, we assume the following check always passes
    return True

def check_account(user_handle):
    print(f"Checking account for {user_handle}")  # Log de débogage
    special_flags = "🇫🇷" in user_handle or "🇦🇶" in user_handle
    if special_flags:
        flags = []
        if "🇫🇷" in user_handle:
            flags.append("🇫🇷")
        if "🇦🇶" in user_handle:
            flags.append("🇦🇶")
        print(f"Account {user_handle} has special flag(s): {', '.join(flags)}, automatically passing")  # Log de débogage
        return True, {}

    following_check = check_following(user_handle)
    print(f"Following check for {user_handle}: {'passed' if following_check else 'failed'}")  # Log de débogage
    if following_check:
        return True, {}

    tweets = fetch_tweets(user_handle)
    if not tweets:
        print("No tweets found, failing verification.")  # Log de débogage
        return False, {"tweets": 0}

    result, keyword_counts = check_tweets(tweets)
    if result:
        print(f"Account {user_handle} passes the tweet content check")  # Log de débogage
    else:
        print(f"Account {user_handle} fails the tweet content check")  # Log de débogage

    print("Detailed keyword occurrences:")  # Log de débogage
    for keyword, count in keyword_counts.items():
        print(f"{keyword}: {count}")

    return result, keyword_counts

# Commande pour tester @gaulerie directement
def test_account():
    user_handle = 'gaulerie'
    print(f"Testing account for {user_handle}")
    result, keyword_counts = check_account(user_handle)
    if result:
        print(f"Account {user_handle} passed verification")
    else:
        print(f"Account {user_handle} failed verification")
    print("Detailed keyword occurrences:")
    for keyword, count in keyword_counts.items():
        print(f"{keyword}: {count}")

test_account()  # Pour tester le compte 'gaulerie' lors de l'exécution du script
