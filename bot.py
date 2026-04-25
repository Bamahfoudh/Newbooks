import requests

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

def main():
    for tag in hashtags:
        url = f"https://twitter.com/search?q=%23{tag}&src=typed_query&f=live"
        send_message(f"📚 #{tag}\n{url}")

if __name__ == "__main__":
    main()
