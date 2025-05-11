import requests
import feedparser
import time
import json
import os
from deep_translator import GoogleTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN", "Чиний_Telegram_Bot_Token")
CHAT_ID = os.getenv("CHAT_ID", "Чиний_Chat_ID")

# Олон RSS эх үүсвэр
RSS_FEEDS = [
    'https://www.investing.com/rss/news_25.rss',           # Stock
    'https://www.investing.com/rss/news_285.rss',          # Crypto
    'https://www.investing.com/rss/news_301.rss',          # Commodities
]

CACHE_FILE = "sent_titles.json"

# ==== Өмнө явуулсан мэдээг ачаалах ====
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        sent_titles = set(json.load(f))
else:
    sent_titles = set()

# ==== Орчуулга ====
def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='mn').translate(text)
    except Exception as e:
        print(f"[Орчуулгын алдаа]: {e}")
        return text

# ==== Мессеж илгээх ====
def send_message(text):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {'chat_id': CHAT_ID, 'text': text}
        response = requests.post(url, data=payload)
        print("➡️ Илгээсэн:", response.status_code, response.text)
    except Exception as e:
        print(f"[Илгээхэд алдаа гарлаа]: {e}")

# ==== Файлаар хадгалах ====
def save_sent_titles():
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(sent_titles), f, ensure_ascii=False, indent=2)

# ==== Мэдээ авах & илгээх ====
def fetch_and_send_news():
    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                title = entry.title.strip()
                link = entry.link.strip()
                if title not in sent_titles:
                    translated = translate_text(title)
                    message = f"📰 {translated}\n🔗 {link}"
                    send_message(message)
                    sent_titles.add(title)
                    save_sent_titles()
                    time.sleep(1)  # зөөллөх
        except Exception as e:
            print(f"[RSS алдаа]: {e}")

# ==== Үндсэн цикл ====
if __name__ == "__main__":
    while True:
        fetch_and_send_news()
        time.sleep(600)  # 10 минут тутамд шинэчилнэ
