import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

hashtags = [
    "صدر_حديثًا",
    "صدر_حديثا",
    "جديد_الكتب"
]

for tag in hashtags:
    url = f"https://nitter.net/search?q=%23{tag}&f=images"

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")

    images = soup.find_all("img")

    count = 0
    for img in images:
        src = img.get("src")

        if src and "pic" in src:
            img_url = "https://nitter.net" + src

            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "photo": img_url,
                    "caption": f"#{tag}"
                }
            )

            count += 1
            if count == 3:
                break
