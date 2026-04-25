import requests
import time

TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

hashtags = [
    "#صدر_حديثًا",
    "#صدر_حديثا",
    "#جديد_الكتب"
]

def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

def search():
    results = []

    for tag in hashtags:
        url = f"https://nitter.net/search?f=tweets&q={tag}"
        r = requests.get(url)
        
        if r.status_code == 200:
            results.append(f"نتائج {tag} جاهزة 👇\n{url}\n")

    if results:
        send_message("\n\n".join(results))

if __name__ == "__main__":
    search()
