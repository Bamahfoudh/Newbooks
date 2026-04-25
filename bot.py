import requests

BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAABf79AEAAAAAsSJXhaMKhIF3c%2FfU%2BXYfgvXkBhg%3DR4POVIWJTq0DdeIL54huHEMtezwfFrDGXQXpFsgwlnJAyf5Pei"

HEADERS = {
    "Authorization": f"Bearer {BEARER_TOKEN}"
}

HASHTAGS = [
    "#صدر_حديثًا",
    "#صدر_حديثا",
    "#جديد_الكتب"
]

def get_tweets(hashtag):
    url = "https://api.twitter.com/2/tweets/search/recent"

    params = {
        "query": f"{hashtag} -is:retweet has:images",
        "max_results": 10,
        "expansions": "attachments.media_keys",
        "media.fields": "url",
        "tweet.fields": "text"
    }

    res = requests.get(url, headers=HEADERS, params=params)

    if res.status_code != 200:
        print("خطأ:", res.text)
        return []

    data = res.json()

    tweets = data.get("data", [])
    media = data.get("includes", {}).get("media", [])

    media_dict = {}
    for m in media:
        if m.get("type") == "photo":
            media_dict[m["media_key"]] = m.get("url")

    results = []

    for tweet in tweets:
        text = tweet.get("text", "")
        media_keys = tweet.get("attachments", {}).get("media_keys", [])

        image_url = None
        for key in media_keys:
            if key in media_dict:
                image_url = media_dict[key]
                break

        if image_url:
            results.append((text, image_url))

    return results


def main():
    for tag in HASHTAGS:
        print(f"\n===== {tag} =====")

        tweets = get_tweets(tag)

        if not tweets:
            print("لا يوجد نتائج")
            continue

        for text, img in tweets[:3]:
            print("📌 النص:")
            print(text)
            print("🖼 الصورة:")
            print(img)
            print("-" * 40)


if __name__ == "__main__":
    main()
