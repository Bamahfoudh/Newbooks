import requests
import json
import os
import hashlib
import subprocess
from datetime import datetime, timedelta

# =========================
# 🔐 إعداداتك
# =========================
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABf79AEAAAAAsSJXhaMKhIF3c%2FfU%2BXYfgvXkBhg%3DR4POVIWJTq0DdeIL54huHEMtezwfFrDGXQXpFsgwlnJAyf5Pei"
TELEGRAM_TOKEN = "8761813650:AAFtvKLzkHzMBgelkLhcY-7sWHcTVVFYsGA"
CHAT_ID = "1849103"

HEADERS = {"Authorization": f"Bearer {BEARER_TOKEN}"}

HASHTAGS = ["#صدر_حديثًا", "#صدر_حديثا", "#جديد_الكتب"]

DB_FILE = "data.json"

# =========================
# ❌ استبعاد (كما طلبت)
# =========================
EXCLUDE = [
    "رواية","روايات","قصة","قصص","novel","story","شعر","قصيدة","ديوان","روايتان",
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
# 🧠 فلتر ذكي
# =========================
def is_valid(text):
    t = text.lower()

    # استبعاد
    if any(b in t for b in EXCLUDE):
        return False

    # طول
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

    weak = ["رأي","تجربة","ملخص"]
    for w in weak:
        if w in t:
            score -= 1

    return score >= 3

# =========================
# 📥 تحميل
# =========================
def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"images": [], "day": ""}

# =========================
# 💾 حفظ
# =========================
def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

# =========================
# 🔑 بصمة الصورة
# =========================
def hash_image(url):
    try:
        r = requests.get(url, timeout=10)
        return hashlib.md5(r.content).hexdigest()
    except:
        return None

# =========================
# 🕘 وقت التشغيل
# =========================
def should_run_now():
    now = datetime.utcnow() + timedelta(hours=3)
    target = now.replace(hour=9, minute=0, second=0, microsecond=0)
    diff = abs((now - target).total_seconds()) / 60
    return diff <= 10

# =========================
# 📡 تويتر
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
# 📤 تيليجرام
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
        return

    data = load_data()

    today = (datetime.utcnow() + timedelta(hours=3)).strftime("%Y-%m-%d")

    if data.get("day") == today:
        return

    seen = set(data.get("images", []))

    tag = HASHTAGS[(datetime.utcnow().day) % len(HASHTAGS)]
    tweets = get_tweets(tag)

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
    data["day"] = today

    save_data(data)

    # حفظ في GitHub
    subprocess.run(["git", "config", "--global", "user.email", "bot@example.com"])
    subprocess.run(["git", "config", "--global", "user.name", "bot"])
    subprocess.run(["git", "add", "data.json"])
    subprocess.run(["git", "commit", "-m", "update data"], check=False)
    subprocess.run(["git", "push"])

if __name__ == "__main__":
    main()
