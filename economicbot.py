import requests
from bs4 import BeautifulSoup
from googletrans import Translator
import time

BOT_TOKEN = "7041028618:AAEeZuJSJSvUm_Z1e5j7_oFEPDHFRI-V5Gc"
CHAT_ID = "5288102820"
RSS_URL = 'https://www.investing.com/rss/news_25.rss'

translator = Translator()

def fetch_and_send_news():
    try:
        response = requests.get(RSS_URL)
        soup = BeautifulSoup(response.content, 'lxml')  # Хуучин 'xml' байсан
        items = soup.find_all('item')[:3]

        for item in items:
            title = item.title.text
            link = item.link.text
            print("Мэдээ уншив:", title)
            translated = translator.translate(title, src='en', dest='mn').text
            message = f"📰 {translated}\n🔗 {link}"
            send_message(message)
    except Exception as e:
        print(f"Алдаа гарлаа: {e}")

def send_message(text):
    print("Илгээх гэж байна:", text)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': text}
    response = requests.post(url, data=payload)
    print("Telegram хариу:", response.status_code, response.text)

if __name__ == "__main__":
    while True:
        fetch_and_send_news()
        time.sleep(30)
