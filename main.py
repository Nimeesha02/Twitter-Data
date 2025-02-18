import asyncio
import json
import configparser
from twikit.client.client import Client

# Read credentials from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

USERNAME = config["AUTH"]["username"]
EMAIL = config["AUTH"]["email"]
PASSWORD = config["AUTH"]["password"]
COOKIES_FILE = "cookies.json"

async def main():
    client = Client(language='en-US')
    
    try:
        # Try loading cookies first
        client.load_cookies(COOKIES_FILE)
        print("Loaded cookies from file.")
    except Exception:
        print("Cookies not found, logging in...")
        await client.login(auth_info_1=USERNAME, auth_info_2=EMAIL, password=PASSWORD)
        client.save_cookies(COOKIES_FILE)
        print("Cookies saved for future logins.")
    
    # Search tweets with keyword "Colombo"
    tweets = await client.search_tweet("Colombo", "Top", count=10)
    
    for tweet in tweets:
        print(tweet)

# Run the async function
asyncio.run(main())
