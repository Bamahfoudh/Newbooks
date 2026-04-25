import requests
from bs4 import BeautifulSoup

BOT_TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

hashtags = [
    "صدر_حديثًا",
    "صدر_حديثا",
    "جديد_الكتب"
]

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

def send_photo(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption
    })

def get_tweets(tag):
    url = f"https://nitter.net/search?q=%23{tag}&f=live"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "html.parser")

    tweets = []

    for item in soup.select(".timeline-item")[:3]:
        text_tag = item.select_one(".tweet-content")
        img_tag = item.select_one("img")

        if text_tag:
            text = text_tag.text.strip()
        else:
            continue

        img_url = None
        if img_tag and img_tag.get("src") and "profile_images" not in img_tag["src"]:
            img_url = "https://nitter.net" + img_tag["src"]

        tweets.append((text, img_url))

    return tweets


def main():
    for tag in hashtags:
        send_message(f"📚 #{tag}")

        tweets = get_tweets(tag)

        if tweets:
            for text, img in tweets:
                if img:
                    send_photo(img, text)
                else:
                    send_message(text)
        else:
            send_message("لا يوجد نتائج حالياً")


if __name__ == "__main__":
    main()
