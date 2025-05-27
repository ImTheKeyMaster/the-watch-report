import feedparser
import json
from datetime import datetime

RSS_FEEDS = [
    "https://www.hodinkee.com/rss",
    "https://www.watchtime.com/feed/",
    "https://revolutionwatch.com/feed/"
]

articles = []

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries[:5]:  # Limit per source
        articles.append({
            "title": entry.title,
            "link": entry.link,
            "image": entry.get("media_content", [{}])[0].get("url", "")  # Some feeds include media
        })

# Save to JSON
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2, ensure_ascii=False)
