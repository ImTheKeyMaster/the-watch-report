import feedparser
import json
import datetime
from bs4 import BeautifulSoup
import requests
import os

# Create the data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# RSS feeds from watch-related websites
rss_feeds = [
    "https://www.hodinkee.com/articles/rss",
    "https://www.watchtime.com/feed/",
    "https://revolutionwatch.com/feed/",
    "https://europastar.com/spip.php?page=backend"
]

# YouTube channel RSS feeds
youtube_feeds = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCPsgQZxEACESR0ogWm0dUFw",  # Teddy Baldassarre
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCvIIb5YF8sUnm1D62jCvVVw",  # Jenni Elle
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC-IVpEe1GQYclVEGLgPd82Q",  # Nico Leonard
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCt4id9K_t9zu-O23182P4vQ",  # The Time Teller
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCOu5VKZIHDXS-cHn9TOC0Qg",  # Andrew Morgan
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC0E08avdHIH-7AMeVcBGRPQ"   # Horological Society of New York
]

all_articles = []

def get_image_from_article(link):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(link, timeout=10, headers=headers)
        soup = BeautifulSoup(res.content, "html.parser")
        og = soup.find("meta", property="og:image")
        if og and og["content"]:
            return og["content"]
    except Exception:
        pass
    return ""

# Process regular RSS feeds
for url in rss_feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        published = entry.get("published", "")
        source = feed.feed.get("title", "Unknown")
        image = get_image_from_article(link)

        article = {
            "title": title,
            "link": link,
            "published": published,
            "source": source,
            "thumbnail": image
        }

        all_articles.append(article)

# Process YouTube RSS feeds
for url in youtube_feeds:
    feed = feedparser.parse(url)
    print(f"Fetched {len(feed.entries)} entries from {url}")
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        published = entry.get("published", "")
        thumbnail = ""
        if "media_thumbnail" in entry:
            thumbnail = entry.media_thumbnail[0]["url"]

        article = {
            "title": title,
            "link": link,
            "published": published,
            "source": "YouTube",
            "thumbnail": thumbnail
        }

        all_articles.append(article)

# Sort by published date, newest first
def parse_date(article):
    try:
        return datetime.datetime.strptime(article["published"], "%a, %d %b %Y %H:%M:%S %z")
    except Exception:
        return datetime.datetime.min

all_articles = sorted(all_articles, key=parse_date, reverse=True)

# Save to JSON
with open("data/news.json", "w", encoding="utf-8") as f:
    json.dump(all_articles, f, indent=2, ensure_ascii=False)
