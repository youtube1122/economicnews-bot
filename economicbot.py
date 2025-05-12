import tweepy
import requests
import json
import os
import time
from deep_translator import GoogleTranslator

# 🔐 Нууцууд
BEARER_TOKEN = os.getenv("BEARER_TOKEN", "Чиний_Bearer_Token")
BOT_TOKEN = os.getenv("BOT_TOKEN", "Чиний_Telegram_Bot_Token")
CHAT_ID = os.getenv("CHAT_ID", "Чиний_Chat_ID")

# 🔎 Твиттер хэрэглэгчид (username)
TWITTER_ACCOUNTS = {
    "macro": ["business"],
    "crypto": ["CryptoAlerts_", "coindesk", "cointelegraph"]
}

# 🗃 Давхардал шалгах JSON файл
POSTED_FILE = "posted.json"
if not os.path.exists(POSTED_FILE):
    with open(POSTED_FILE, "w") as f:
        json.dump([], f)

with open(POSTED_FILE, "r") as f:
    posted_ids = json.load(f)

# 🐦 Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def translate(text):
    try:
        return GoogleTranslator(source='auto', target='mn').translate(text)
    except:
        return text

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=data)

def fetch_and_send():
    global posted_ids

    for category, accounts in TWITTER_ACCOUNTS.items():
        for username in accounts:
            try:
                user = client.get_user(username=username)
                tweets = client.get_users_tweets(id=user.data.id, max_results=5, tweet_fields=["created_at", "text"])
                if not tweets.data:
                    continue

                for tweet in tweets.data:
                    if tweet.id in posted_ids:
                        continue
                    
                    title = tweet.text.split('\n')[0][:80]
                    translated_text = translate(tweet.text)
                    link = f"https://x.com/{username}/status/{tweet.id}"
                    message = f"📌 {category.upper()} мэдээ\n\n📰 {translated_text}\n🔗 {link}"

                    send_telegram(message)
                    print("Илгээлээ:", tweet.id)
                    
                    posted_ids.append(tweet.id)
                    with open(POSTED_FILE, "w") as f:
                        json.dump(posted_ids, f)

                    time.sleep(2)  # хооронд нь бага зэрэг зайтай явуулах
            except Exception as e:
                print("⚠️ Алдаа:", e)

if __name__ == "__main__":
    while True:
        fetch_and_send()
        time.sleep(60)  # минут тутамд шалгах
