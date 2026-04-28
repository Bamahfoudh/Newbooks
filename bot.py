import requests
import json
import os
from datetime import datetime, timedelta

# ===== إعداداتك =====
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABf79AEAAAAAsSJXhaMKhIF3c%2FfU%2BXYfgvXkBhg%3DR4POVIWJTq0DdeIL54huHEMtezwfFrDGXQXpFsgwlnJAyf5Pei"
TELEGRAM_TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

HASHTAGS = ["#صدر_حديثًا","#صدر_حديثا","#جديد_الكتب"]

# ===== استبعاد =====
EXCLUDE = [
    "رواية","روايات","قصة","قصص","novel","story","شعر","قصيدة","ديوان",
    "سياسة","سياسي","انتخابات","حكومة","حزب","رئيس","وزير",
    "فيلم","مسلسل","ممثل","مغني","أغنية","فن","مشاهير",
    "خصم","كود","كوبون","عرض","توصيل","شحن","اطلب","متجر","الدفع",
    "مسابقة","سحب","اربح","جائزة","شارك",
    "وظيفة","وظائف","دورة","دورات","تدريب","ورشة",
    "يوتيوب","فيديو","مقطع","تيك توك","بودكاست","بث","مساحة",
    "رأيي","وش رايكم","نقاش","سؤال","فضفضة",
    "ثريد","سلسلة","يتبع","تابع",
    "اقتباس","اقتباسات","حكمة","قال",
    "برمجة","AI","تقنية","تطبيق"
]

# ===== إشارات كتاب =====
BOOK_HINTS = [
    "كتاب","إصدار","صدر","طبعة","تحقيق","شرح",
    "دار","نشر","مكتبة","مجلد","جزء","سلسلة",
    "المؤلف","تأليف","ترجمة","غلاف","ردمك","isbn"
]

# ===== فلتر ذكي =====
def is_valid(text):
    t = text.lower()

    if any(b in t for b in EXCLUDE):
        return False

    if len(t) < 50:
        return False

    score = 0

    for h in BOOK_HINTS:
        if h in t:
            score += 2

    extra = ["pdf","نسخة","تحميل","مكتبة","غلاف","فهرس","طبعة جديدة"]
    for e in extra:
        if e in t:
            score += 1

    weak = ["رأي","تجربة","اقتباس","ملخص"]
    for w in weak:
        if w in t:
            score -= 1

    return score >= 3

# ===== تخزين =====
DB_FILE = "data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE,"r") as f:
            return json.load(f)
    return {"ids": [], "day": ""}

def save_data(data):
    with open(DB_FILE,"w") as f:
        json.dump(data,f)

# ===== منع تكرار يومي =====
def already_sent_today(data):
    today = (datetime.utcnow()+timedelta(hours=3)).strftime("%Y-%m-%d")
    return data.get("day") == today

def mark_today(data):
    today = (datetime.utcnow()+timedelta(hours=3)).strftime("%Y-%m-%d")
    data["day"] = today

# ===== جلب =====
def get_tweets(tag):
    url = "https://api.twitter.com/2/tweets/search/recent"

    query = f"{tag} -is:retweet has:images"

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
                results.append((t["id"], text, media_map[k]))
                break

    return results

# ===== إرسال =====
def send_photo(text, img):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": img,
        "caption": text[:1000]
    })

# ===== تشغيل =====
def main():
    data = load_data()

    if already_sent_today(data):
        print("أرسل اليوم")
        return

    sent_ids = set(data.get("ids", []))

    for tag in HASHTAGS:
        tweets = get_tweets(tag)
        count = 0

        for tid, text, img in tweets:
            if tid in sent_ids:
                continue

            send_photo(text, img)
            sent_ids.add(tid)
            count += 1

            if count >= 10:
                break

    data["ids"] = list(sent_ids)
    mark_today(data)
    save_data(data)

if __name__ == "__main__":
    main()
