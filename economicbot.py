import os
import json
import time
import requests
from deep_translator import GoogleTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

TWITTER_ACCOUNTS = {
    "Макро": ["business"],
    "Крипто": ["coindesk", "CryptoAlerts_", "cointelegraph"]
}

SEEN_FILE = "seen_tweets.json"

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return {}

def save_seen(data):
    with open(SEEN_FILE, "w") as f:
        json.dump(data, f)

def fetch_tweets(username):
    url = f"https://api.twitter.com/2/tweets/search/recent?query=from:{username}&tweet.fields=text,created_at&expansions=attachments.media_keys,author_id&media.fields=url"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        print(f"[{username}] Error: {response.status_code}, {response.text}")
        return []

def translate(text):
    try:
        return GoogleTranslator(source='auto', target='mn').translate(text)
    except Exception as e:
        print("Орчуулгын алдаа:", e)
        return text

def send_telegram(title, desc, img_url=None, category="Крипто"):
    text = f"<b>{category}</b>\n\n<b>{title}</b>\n\n{desc}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto" if img_url else f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "caption": text,
        "parse_mode": "HTML"
    }

    if img_url:
        payload["photo"] = img_url
    else:
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}

    res = requests.post(url, data=payload)
    print("Telegram response:", res.status_code)

def main():
    seen = load_seen()

    while True:
        for category, usernames in TWITTER_ACCOUNTS.items():
            for user in usernames:
                tweets = fetch_tweets(user)
                if user not in seen:
                    seen[user] = []

                for tweet in tweets:
                    tweet_id = tweet["id"]
                    if tweet_id in seen[user]:
                        continue

                    seen[user].append(tweet_id)
                    title = translate(tweet.get("text", "")[:100])
                    desc = translate(tweet.get("text", ""))
                    send_telegram(title, desc, category=category)
                    time.sleep(1)

        save_seen(seen)
        time.sleep(60)

if __name__ == "__main__":
    main()
