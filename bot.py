import requests
import json
import os
import hashlib

# =========================
# 🔐 إعدادات
# =========================
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABf79AEAAAAAsSJXhaMKhIF3c%2FfU%2BXYfgvXkBhg%3DR4POVIWJTq0DdeIL54huHEMtezwfFrDGXQXpFsgwlnJAyf5Pei"
TELEGRAM_TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

# =========================
# 👤 الحسابات
# =========================
ACCOUNTS = [
    "newsunnabooks","kotobnew","dar_atlas","Aljawzi","sfaar16","center_rakaez",
    "khizama7","AlMabarrah","darlmalikiya","Taqrib_sa","dr_belhay21","ihsancenter",
    "mktabtsuotuor","falsalalmutairi","drdaghashalajmi","dorarnet","malturki",
    "drabdelhalimben","booksnew1","dar_rakaezkw","eqleede","muqarbah","soturcenter",
    "ataat11","darlataif","cons_books","alla1402","ithraaSA","dar_tg","yest1350",
    "HKS_1407","fayez_alsuraih","daralminhaj","thmarat"
]

# =========================
# #️⃣ هاشتاقات
# =========================
HASHTAGS = [
    "#جديد_إصدارات_الكتب",
    "#جديد_الكتب",
    "#كتب_جديدة",
    "#إصدارات_الكتب",
    "#صدر_حديثاً",
    "#صدر_حديثًا",
    "#صدر_حديثا",
    "#يصدر_قريبًا",
    "#يصدر_قريبا"
]

# =========================
# 🔒 بصمة الصورة
# =========================
def hash_image(url):
    try:
        img = requests.get(url, timeout=10).content
        return hashlib.md5(img).hexdigest()
    except:
        return None

# =========================
# 💾 تخزين
# =========================
FILE = "data.json"

def load_data():
    if os.path.exists(FILE):
        with open(FILE, "r") as f:
            return json.load(f)
    return {"images": []}

def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# =========================
# 📡 جلب (مع دعم الريتويت)
# =========================
def get_tweets():
    url = "https://api.twitter.com/2/tweets/search/recent"
    results = []

    accounts_query = " OR ".join([f"from:{a}" for a in ACCOUNTS])

    for tag in HASHTAGS:
        # 🔥 لا نستبعد الريتويت
        query = f"({accounts_query}) {tag} -is:reply has:images"

        params = {
            "query": query,
            "max_results": 10,
            "expansions": "attachments.media_keys,referenced_tweets.id,referenced_tweets.id.author_id",
            "media.fields": "url",
            "tweet.fields": "text,referenced_tweets"
        }

        r = requests.get(url, headers=HEADERS, params=params)

        if r.status_code != 200:
            print("خطأ:", r.text)
            continue

        data = r.json()
        tweets = data.get("data", [])
        includes = data.get("includes", {})
        media = includes.get("media", [])
        referenced = includes.get("tweets", [])

        media_map = {
            m["media_key"]: m["url"]
            for m in media if m.get("type") == "photo"
        }

        # خريطة للتغريدات الأصلية
        ref_map = {t["id"]: t for t in referenced}

        for t in tweets:
            text = t["text"]
            keys = t.get("attachments", {}).get("media_keys", [])

            # 🔥 إذا ما فيه صورة، نحاول من التغريدة الأصلية
            if not keys and "referenced_tweets" in t:
                for ref in t["referenced_tweets"]:
                    if ref["type"] == "retweeted":
                        original = ref_map.get(ref["id"])
                        if original:
                            text = original.get("text", text)
                            keys = original.get("attachments", {}).get("media_keys", [])
                        break

            for k in keys:
                if k in media_map:
                    results.append((text, media_map[k]))
                    break

    return results

# =========================
# 📤 إرسال
# =========================
def send_photo(text, img):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": img,
        "caption": text[:1000]
    })

# =========================
# 🚀 التشغيل
# =========================
def main():
    data = load_data()
    seen = set(data.get("images", []))

    tweets = get_tweets()

    sent = 0

    for text, img in tweets:
        h = hash_image(img)

        if not h or h in seen:
            continue

        send_photo(text, img)
        seen.add(h)
        sent += 1

        if sent >= 5:
            break

    data["images"] = list(seen)
    save_data(data)

# =========================
if __name__ == "__main__":
    main()
