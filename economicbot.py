import feedparser
import time
import requests
import hashlib
import os
from deep_translator import GoogleTranslator

# Telegram Bot тохиргоо
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# RSS эх сурвалжууд
FEEDS = [
    "https://cointelegraph.com/rss",
    "https://cryptonews.com/news/feed",
    "https://decrypt.co/feed",
    "https://www.coindesk.com/arc/outboundfeeds/rss/"
]

# Давхардсан мэдээг шалгахын тулд ID хадгална
SEEN_FILE = "seen_rss_crypto.json"
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, 'r') as f:
        seen_ids = set(f.read().splitlines())
else:
    seen_ids = set()

def translate(text):
    try:
        return GoogleTranslator(source='auto', target='mn').translate(text)
    except:
        return text

def send_telegram(title, desc, link, image_url=None):
    caption = f"<b>{title}</b>\n\n{desc}\n\n<a href='{link}'>Дэлгэрэнгүй унших</a>"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "caption": caption,
        "photo": image_url,
        "parse_mode": "HTML"
    } if image_url else {
        "chat_id": CHAT_ID,
        "text": caption,
        "parse_mode": "HTML"
    }
    requests.post(url, data=data)

def fetch_news():
    global seen_ids
    for feed_url in FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:
            uid = hashlib.md5(entry.link.encode()).hexdigest()
            if uid in seen_ids:
                continue
            seen_ids.add(uid)

            title = translate(entry.title)
            desc = translate(entry.summary if hasattr(entry, 'summary') else '')
            link = entry.link

            image_url = None
            if 'media_content' in entry:
                image_url = entry.media_content[0].get('url')
            elif 'links' in entry:
                for link_obj in entry.links:
                    if link_obj.type.startswith('image'):
                        image_url = link_obj.href
                        break

            send_telegram(title, desc, link, image_url)
            time.sleep(2)

    with open(SEEN_FILE, 'w') as f:
        f.write('\n'.join(seen_ids))

if __name__ == "__main__":
    while True:
        fetch_news()
        time.sleep(300)  # 5 минут тутамд шалгана

