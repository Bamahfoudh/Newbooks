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

HASHTAGS = [
    "#صدر_حديثًا",
    "#صدر_حديثا",
    "#جديد_الكتب"
]

# =========================
# ❌ استثناءات قوية
# =========================
EXCLUDE = [
    "رواية","روايات","قصة","قصص","شعر","قصيدة","ديوان",
    "سياسة","انتخابات","حكومة",
    "فيلم","مسلسل","مغني","أغنية",
    "خصم","كود","عرض","متجر",
    "وظيفة","دورة","تدريب",
    "يوتيوب","فيديو","تيك توك",
    "رأيي","سؤال","نقاش",
    "اقتباس","حكمة",
    "برمجة","AI","تقنية"
]

# =========================
# ✔️ إشارات كتاب
# =========================
BOOK_HINTS = [
    "كتاب","صدر","إصدار","طبعة",
    "دار","نشر","مكتبة",
    "تأليف","تحقيق","ترجمة"
]

# =========================
# 🧠 فلتر
# =========================
def is_valid(text):
    t = text.lower()

    if len(t) < 40:
        return False

    if any(b in t for b in EXCLUDE):
        return False

    if not any(h in t for h in BOOK_HINTS):
        return False

    return True

# =========================
# 🧠 بصمة الصورة (منع التكرار الحقيقي)
# =========================
def hash_image(url):
    try:
        img = requests.get(url).content
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
# 📡 جلب التغريدات
# =========================
def get_tweets(tag):
    url = "https://api.twitter.com/2/tweets/search/recent"

    query = f"{tag} -is:retweet -is:reply has:images"

    params = {
        "query": query,
        "max_results": 10,
        "expansions": "attachments.media_keys",
        "media.fields": "url",
        "tweet.fields": "text"
    }

    r = requests.get(url, headers=HEADERS, params=params)

    if r.status_code != 200:
        print(r.text)
        return []

    data = r.json()
    tweets = data.get("data", [])
    media = data.get("includes", {}).get("media", [])

    media_map = {
        m["media_key"]: m["url"]
        for m in media if m.get("type") == "photo"
    }

    results = []

    for t in tweets:
        text = t["text"]

        if not is_valid(text):
            continue

        keys = t.get("attachments", {}).get("media_keys", [])
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

    sent = 0

    for tag in HASHTAGS:
        tweets = get_tweets(tag)

        for text, img in tweets:
            h = hash_image(img)

            # 🔥 هنا الحل الحقيقي للتكرار
            if not h or h in seen:
                continue

            send_photo(text, img)
            seen.add(h)
            sent += 1

            if sent >= 5:
                break

        if sent >= 5:
            break

    data["images"] = list(seen)
    save_data(data)

if __name__ == "__main__":
    main()
