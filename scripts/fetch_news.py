import feedparser
import json
import os
from bs4 import BeautifulSoup
import requests

# Feed URLs and priority (lower number = higher priority)
FEEDS = [
    ("https://www.hodinkee.com/articles/rss", 1),
    ("https://www.watchtime.com/feed/", 2),
    ("https://www.revolution.watch/feed/", 3),
    ("https://europastar.com/spip.php?page=backend", 4),
]

def extract_image(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.content, "html.parser")
        for img in soup.find_all("img"):
            src = img.get("src")
            if src and src.startswith("http"):
                return src
    except Exception as e:
        print(f"Error fetching image from {url}: {e}")
    return None

articles = []

# Collect articles, ranked by feed priority and date
for feed_url, priority in FEEDS:
    d = feedparser.parse(feed_url)
    for entry in d.entries:
        image = extract_image(entry.link)
        if not image:
            continue  # Skip if no usable image
        article = {
            "title": entry.title,
            "link": entry.link,
            "image": image,
            "source_priority": priority,
            "published": entry.get("published_parsed")
        }
        articles.append(article)

# Sort by source priority first, then by published date (descending)
articles.sort(key=lambda x: (x["source_priority"], x["published"] if x["published"] else 0), reverse=False)

# Write to data/news.json
os.makedirs("data", exist_ok=True)
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(articles, f, ensure_ascii=False, indent=2)

