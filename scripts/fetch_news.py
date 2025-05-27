import feedparser, json, openai, os
from datetime import datetime
from bs4 import BeautifulSoup

# Replace this with your actual OpenAI key or use GitHub secrets
openai.api_key = os.getenv("OPENAI_API_KEY")

FEEDS = [
    "https://www.hodinkee.com/feed",
    "https://www.watchtime.com/feed/",
    "https://www.revolution.watch/feed/",
    "https://www.europastar.com/spip.php?page=backend",
]

def summarize(title, link, description):
    prompt = f"Summarize this watch-related article:\nTitle: {title}\nDescription: {description}\nURL: {link}\n\nSummary:"
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return ""

def fetch_image(entry):
    soup = BeautifulSoup(entry.get("summary", ""), "html.parser")
    img = soup.find("img")
    return img["src"] if img else ""

def fetch_all():
    all_items = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:
            all_items.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summarize(entry.title, entry.link, entry.get("description", "")),
                "image": fetch_image(entry)
            })
    all_items.sort(key=lambda x: len(x['summary']), reverse=True)
    return {
        "main": all_items[0],
        "others": all_items[1:10]
    }

if __name__ == "__main__":
    news = fetch_all()
    os.makedirs("data", exist_ok=True)
    with open("data/latest.json", "w", encoding="utf-8") as f:
        json.dump(news, f, ensure_ascii=False, indent=2)
