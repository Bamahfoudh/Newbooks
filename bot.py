import requests

BOT_TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={"chat_id": CHAT_ID, "text": "اشتغل البوت ✅"}
)
