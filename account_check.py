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
        tweet_text = tweet.find('div', {'lang': True}).get_text()
        tweets.append(tweet_text)
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

    for keyword, count in keyword_counts.items():
        print(f"Occurrences of '{keyword}': {count}")

    passed = all(count == 0 for count in keyword_counts.values())
    return passed, keyword_counts

def check_following(user_handle):
    # Pour la démonstration, nous allons supposer que cette fonction vérifie un critère différent,
    # car nous ne pouvons pas scraper la liste des abonnements.
    print(f"Checking following for {user_handle}")  # Log de débogage
    return True

def check_account(user_handle):
    print(f"Checking account for {user_handle}")  # Log de débogage
    if "🇫🇷" in user_handle or "🇦🇶" in user_handle:
        print(f"Account {user_handle} has special flag, automatically passing")  # Log de débogage
        return True, {}

    if check_following(user_handle):
        print(f"Account {user_handle} passes the following check")  # Log de débogage
        return True, {}

    tweets = fetch_tweets(user_handle)
    result, keyword_counts = check_tweets(tweets)
    if result:
        print(f"Account {user_handle} passes the tweet content check")  # Log de débogage
    else:
        print(f"Account {user_handle} fails the tweet content check")  # Log de débogage
    return result, keyword_counts
