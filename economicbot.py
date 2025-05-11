import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
RSS_URL = 'https://www.investing.com/rss/news_25.rss'

translator = Translator()
last_titles = []

def fetch_and_send_news():
    global last_titles
    try:
        response = requests.get(RSS_URL)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:3]

        for item in items:
            title = item.title.text
            link = item.link.text
            if title not in last_titles:
                translated = translator.translate(title, src='en', dest='mn').text
                message = f"📰 {translated}\n🔗 {link}"
                send_message(message)
                last_titles.append(title)
    except Exception as e:
        print(f"Алдаа гарлаа: {e}")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    requests.post(url, data=payload)

if __name__ == "__main__":
    while True:
        fetch_and_send_news()
        time.sleep(3600)






