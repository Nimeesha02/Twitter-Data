import asyncio
import json
import configparser
import time
from datetime import datetime
from random import randint
import csv
from twikit.client.client import Client, TooManyRequests

# Read credentials from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

USERNAME = config["AUTH"]["username"]
EMAIL = config["AUTH"]["email"]
PASSWORD = config["AUTH"]["password"]
COOKIES_FILE = "cookies.json"

# Constants
MINIMUM_TWEETS = 10000
# QUERY = "(from:elonmusk) lang:en until:2020-01-01 since:2018-01-01"

QUERY = (
    '("Colombo Stock Exchange" OR "CSE Sri Lanka" OR "Sri Lanka stocks" OR '
    '"Sri Lanka share market" OR "Sri Lanka stock market" OR "SL20 index" OR '
    '"All Share Price Index (ASPI)" OR "Sri Lanka market trend" OR "CSE trading" OR '
    '#SriLankaStocks OR #SriLankaEconomy OR #InvestSriLanka OR #CSE OR #SL20 OR '
    '#SriLankaFinance OR #SriLankaTrading OR #SriLankaBudget OR #SriLankaIMF) '
    'lang:en -filter:links -filter:replies'
)

# Create CSV file
with open("tweets.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Tweet_count", "Username", "Text", "Created At", "Retweets", "Likes"])

async def get_tweets(client, tweets):
    if tweets is None:
        print(f"{datetime.now()} - Getting tweets...")
        tweets = await client.search_tweet(QUERY, product="Top", count=10)
    else:
        wait_time = randint(5, 10)
        print(f"{datetime.now()} - Getting next tweets after {wait_time} seconds...")
        await asyncio.sleep(wait_time)
        tweets = await tweets.next()
    return tweets

async def main():
    client = Client(language='en-US')
    
    try:
        client.load_cookies(COOKIES_FILE)
        print("Loaded cookies from file.")
    except Exception:
        print("Cookies not found, logging in...")
        await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
        client.save_cookies(COOKIES_FILE)
        print("Cookies saved for future logins.")
    
    tweet_count = 0
    tweets = None
    
    while tweet_count < MINIMUM_TWEETS:
        try:
            tweets = await get_tweets(client, tweets)
        except TooManyRequests as e:
            rate_limit_reset = datetime.fromtimestamp(e.rate_limit_reset)
            wait_time = (rate_limit_reset - datetime.now()).total_seconds()
            print(f"{datetime.now()} - Rate limit reached. Waiting until {rate_limit_reset}")
            await asyncio.sleep(wait_time)
            continue
        
        if not tweets:
            print(f"{datetime.now()} - No more tweets found")
            break
        
        for tweet in tweets:
            tweet_count += 1
            tweet_data = [
                tweet_count, tweet.user.name, tweet.text, tweet.created_at,
                tweet.retweet_count, tweet.favorite_count
            ]
            
            with open("tweets.csv", "a", newline="", encoding="utf-8-sig") as file:
                writer = csv.writer(file)
                writer.writerow(tweet_data)

            
            print(f"{datetime.now()} - Processed {tweet_count} tweets")
    
    print(f"{datetime.now()} - Done! Got {tweet_count} tweets.")

# Run the async function
asyncio.run(main())