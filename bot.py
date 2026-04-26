import requests
import json
import os
from datetime import datetime, timedelta

# =========================
# 🔐 إعداداتك
# =========================
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABf79AEAAAAAsSJXhaMKhIF3c%2FfU%2BXYfgvXkBhg%3DR4POVIWJTq0DdeIL54huHEMtezwfFrDGXQXpFsgwlnJAyf5Pei"
TELEGRAM_TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

HASHTAGS = [
    "#صدر_حديثًا",
    "#صدر_حديثا",
    "#جديد_الكتب"
]

# =========================
# ❌ استبعاد
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
    "برمجة","AI","تقنية","تطبيق"
]

# =========================
# ✔️ إشارات كتاب
# =========================
BOOK_HINTS = [
    "كتاب","إصدار","صدر","طبعة","تحقيق","شرح",
    "دار","نشر","مكتبة","مجلد","جزء","سلسلة",
    "المؤلف","تأليف","ترجمة","غلاف","ردمك","isbn"
]

# =========================
# 🧠 فلتر ذكي (نقاط)
# =========================
def is_valid(text):
    t = text.lower()

    # ❌ استبعاد مباشر
    if any(b in t for b in EXCLUDE):
        return False

    # ❌ قصير
    if len(t) < 50:
        return False

    score = 0

    # ✔️ إشارات قوية
    for h in BOOK_HINTS:
        if h in t:
            score += 2

    # ✔️ إشارات إضافية
    extra_good = [
        "pdf","نسخة","تحميل","مكتبة","دار نشر",
        "غلاف","فهرس","طبعة جديدة","صدر حديثًا"
    ]
    for g in extra_good:
        if g in t:
            score += 1

    # ❌ تقليل
    weak_bad = [
        "رأي","تجربة","اقتباس","ملخص"
    ]
    for w in weak_bad:
        if w in t:
            score -= 1

    return score >= 3

# =========================
# 📦 منع التكرار
# =========================
DB_FILE = "sent_ids.json"

def load_sent():
    if os.path.exists(DB_FILE):
        return set(json.load(open(DB_FILE)))
    return set()

def save_sent(data):
    json.dump(list(data), open(DB_FILE, "w"))

# =========================
# 🕘 حارس الوقت
# =========================
def should_run_now():
    now = datetime.utcnow() + timedelta(hours=3)
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    diff = abs((now - target).total_seconds()) / 60
    return diff <= 10

# =========================
# 📅 حارس اليوم
# =========================
DAY_FILE = "day.txt"

def already_ran_today():
    today = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d")
    if os.path.exists(DAY_FILE):
        return open(DAY_FILE).read() == today
    return False

def mark_today():
    today = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d")
    open(DAY_FILE, "w").write(today)

# =========================
# 📡 جلب تويتر
# =========================
def get_tweets(tag):
    url = "https://api.twitter.com/2/tweets/search/recent"

    query = f"{tag} (كتاب OR دار OR نشر OR إصدار) -رواية -is:retweet -is:reply has:images"

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
        if not is_valid(t["text"]):
            continue

        keys = t.get("attachments", {}).get("media_keys", [])
        for k in keys:
            if k in media_map:
                results.append((t["id"], t["text"], media_map[k]))
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

    if not should_run_now():
        print("ليس وقت الإرسال")
        return

    if already_ran_today():
        print("تم الإرسال اليوم")
        return

    sent = load_sent()

    for tag in HASHTAGS:
        tweets = get_tweets(tag)
        count = 0

        for tid, text, img in tweets:
            if tid in sent:
                continue

            send_photo(text, img)
            sent.add(tid)
            count += 1

            if count >= 10:
                break

    save_sent(sent)
    mark_today()

if __name__ == "__main__":
    main()
