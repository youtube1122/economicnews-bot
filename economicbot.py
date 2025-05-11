import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import time

BOT_TOKEN = "ТАНЫ_БОТ_ТОКЕН"
CHAT_ID = "ТАНЫ_CHAT_ID"
RSS_URL = 'https://www.investing.com/rss/news_25.rss'

translator = Translator()
sent_titles = set()  # илгээсэн гарчгуудыг энд хадгална

def fetch_and_send_news():
    try:
        response = requests.get(RSS_URL)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')[:5]

        for item in items:
            title = item.title.text.strip()
            link = item.link.text.strip()

            if title not in sent_titles:
                translated = translator.translate(title, src='en', dest='mn').text
                message = f"📰 {translated}\n🔗 {link}"
                send_message(message)
                sent_titles.add(title)
    except Exception as e:
        print(f"Алдаа гарлаа: {e}")

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    response = requests.post(url, data=payload)
    print("Илгээв:", response.status_code, response.text)

if __name__ == "__main__":
    while True:
        fetch_and_send_news()
        time.sleep(120)  # 2 минут тутамд шалгана
