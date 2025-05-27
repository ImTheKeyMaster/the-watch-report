import feedparser
import json
import os
from datetime import datetime
from urllib.parse import urlparse

# RSS feed sources
feeds = {
    "Hodinkee": "https://www.hodinkee.com/articles/rss",
    "WatchTime": "https://www.watchtime.com/feed/",
    "Revolution": "https://revolutionwatch.com/feed/",
    "Europa Star": "https://www.europastar.com/spip.php?page=backend",
    "Worn & Wound": "https://wornandwound.com/feed/",
    "Teddy Baldassarre": "https://www.youtube.com/feeds/videos.xml?channel_id=UCVZ1uCTyU9nQ6vDZ9kQPLiA",
    "Jenni Elle": "https://www.youtube.com/feeds/videos.xml?channel_id=UCtOkz3tT5rZLMV0H1GhOQrA",
    "Nico Leonard": "https://www.youtube.com/feeds/videos.xml?channel_id=UCdK4zjJzI9bUPc9zLrF7K0w",
    "The Time Teller": "https://www.youtube.com/feeds/videos.xml?channel_id=UCroA-g2IlNNSrZpM1n_Exow",
    "Andrew Morgan": "https://www.youtube.com/feeds/videos.xml?channel_id=UCwV7vMbMWH4-V0ZXdmDpPBA",
    "HSNY": "https://www.youtube.com/feeds/videos.xml?channel_id=UCVGjv7rnV_1w8AeOYKNVD3w"
}

def get_thumbnail(entry):
    if "media_thumbnail" in entry:
        return entry.media_thumbnail[0]["url"]
    elif "media_content" in entry:
        return entry.media_content[0]["url"]
    elif "summary" in entry and "img" in entry["summary"]:
        # Fallback: try to parse an image from summary HTML
        import re
        match = re.search(r'<img[^>]+src="([^"]+)"', entry["summary"])
        if match:
            return match.group(1)
    return None

def parse_feed(source, url):
    parsed = feedparser.parse(url)
    articles = []

    for entry in parsed.entries:
        thumbnail = get_thumbnail(entry)
        if not thumbnail:
            continue

        try:
            published = entry.get("published_parsed")
            published_dt = datetime(*published[:6]) if published else datetime.utcnow()
        except Exception:
            published_dt = datetime.utcnow()

        articles.append({
            "title": entry.get("title", "Untitled"),
            "link": entry.get("link", ""),
            "published": published_dt.isoformat(),
            "thumbnail": thumbnail,
            "source": source
        })
    return articles

# Aggregate all articles
all_articles = []
for source, url in feeds.items():
    try:
        articles = parse_feed(source, url)
        all_articles.extend(articles)
    except Exception as e:
        print(f"Failed to parse {source}: {e}")

# Sort by published date, descending
all_articles.sort(key=lambda x: x["published"], reverse=True)

# Save to JSON
output_path = os.path.join("data", "news.json")
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_articles, f, indent=2)

print(f"Saved {len(all_articles)} articles to {output_path}")
