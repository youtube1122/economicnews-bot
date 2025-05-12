import tweepy
import json
import time
import requests
from googletrans import Translator

# ==== CONFIG ====

BEARER_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAObV1AEAAAAA3wxSWOhzRMvzp1RLCEmtd3rNT6w%3D7aoXAHT2lUxDBNSjYun5QJHcQlToHHFVuFdIv04R2AKniXcxx2'
BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  # Энд Telegram Bot Token-оо оруулна
CHAT_ID = 'YOUR_TELEGRAM_CHAT_ID'      # Энд Telegram Chat ID-гаа оруулна
translator = Translator()
SEEN_FILE = 'seen_tweets.json'

# ==== ТАНЫ АНГИЛАЛ БА ХАЯГУУД ====
USER_CATEGORIES = {
    'Макро': ['business', 'CryptoAlerts_'],
    'Крипто': ['coindesk', 'CryptoAlerts_', 'cointelegraph']
}

# ==== TWITTER AUTH ====
client = tweepy.Client(bearer_token=BEARER_TOKEN)

# === Твит ID ачаалж, хадгалах ===
def load_seen_ids():
    try:
        with open(SEEN_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_seen_ids(seen_ids):
    with open(SEEN_FILE, 'w') as f:
        json.dump(seen_ids, f)

# === Telegram руу илгээх ===
def send_telegram_message(title, text, image_url=None, category=""):
    caption = f"📂 {category}\n📰 {title}\n\n{text}"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'caption': caption if image_url else None,
        'photo': image_url if image_url else None,
        'text': caption if not image_url else None,
        'parse_mode': 'HTML'
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    requests.post(url, data=payload)

# === Орчуулга ===
def translate_text(text):
    try:
        return translator.translate(text, src='en', dest='mn').text
    except:
        return text

# === Шинэ мэдээ татах ===
def fetch_and_send():
    seen_ids = load_seen_ids()

    for category, usernames in USER_CATEGORIES.items():
        for username in usernames:
            try:
                user = client.get_user(username=username)
                tweets = client.get_users_tweets(id=user.data.id, max_results=5, tweet_fields=["created_at"], expansions=["attachments.media_keys"], media_fields=["url"])
                media_urls = {}
                if tweets.includes and "media" in tweets.includes:
                    media_urls = {m.media_key: m.url for m in tweets.includes['media'] if m.type == 'photo'}

                for tweet in tweets.data:
                    tweet_id = str(tweet.id)
                    if tweet_id in seen_ids.get(username, []):
                        continue

                    translated = translate_text(tweet.text)
                    image_url = None
                    if 'attachments' in tweet.data and 'media_keys' in tweet.data['attachments']:
                        keys = tweet.data['attachments']['media_keys']
                        for key in keys:
                            if key in media_urls:
                                image_url = media_urls[key]
                                break

                    send_telegram_message(category=category, title=username, text=translated, image_url=image_url)
                    seen_ids.setdefault(username, []).append(tweet_id)
                    time.sleep(2)

            except Exception as e:
                print(f"⚠️ {username} дээр алдаа: {e}")

    save_seen_ids(seen_ids)

# === LOOP ===
if __name__ == "__main__":
    while True:
        fetch_and_send()
        time.sleep(60)  # 1 мин тутамд шалгана
