import requests
import json
import os

# =========================
# 🔐 إعداداتك
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
# ❌ استبعاد موسّع جدًا
# =========================
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
    "برمجة","كود","AI","تقنية","تطبيق"
]

# =========================
# ✔️ إشارات كتاب قوية
# =========================
BOOK_HINTS = [
    "كتاب","إصدار","صدر","طبعة","تحقيق","شرح",
    "دار","نشر","مكتبة","مجلد","جزء","سلسلة",
    "المؤلف","تأليف","ترجمة","غلاف","ردمك","isbn"
]

# =========================
# 🧠 فلتر ذكي
# =========================
def is_valid(text):
    t = text.lower()

    # استبعاد
    for bad in EXCLUDE:
        if bad in t:
            return False

    # طول كافي
    if len(t) < 40:
        return False

    # لازم فيه دلالة كتاب
    if not any(h in t for h in BOOK_HINTS):
        return False

    return True

# =========================
# 📦 منع التكرار
# =========================
DB_FILE = "sent_ids.json"

def load_sent():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_sent(ids):
    with open(DB_FILE, "w") as f:
        json.dump(list(ids), f)

# =========================
# 📡 جلب التغريدات
# =========================
def get_tweets(tag):
    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": f"{tag} -is:retweet -is:reply has:images",
        "max_results": 10,
        "expansions": "attachments.media_keys",
        "media.fields": "url",
        "tweet.fields": "text"
    }

    res = requests.get(url, headers=HEADERS, params=params)

    if res.status_code != 200:
        print(res.text)
        return []

    data = res.json()
    tweets = data.get("data", [])
    media = data.get("includes", {}).get("media", [])

    media_dict = {
        m["media_key"]: m["url"]
        for m in media if m.get("type") == "photo"
    }

    results = []

    for tweet in tweets:
        text = tweet["text"]

        if not is_valid(text):
            continue

        keys = tweet.get("attachments", {}).get("media_keys", [])
        for k in keys:
            if k in media_dict:
                results.append((tweet["id"], text, media_dict[k]))
                break

    return results

# =========================
# 📤 إرسال تيليجرام
# =========================
def send_photo(text, photo):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    requests.post(url, data={
        "chat_id": CHAT_ID,
        "photo": photo,
        "caption": text[:1000]
    })

# =========================
# 🚀 التشغيل
# =========================
def main():
    sent_ids = load_sent()

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

    save_sent(sent_ids)

if __name__ == "__main__":
    main()
