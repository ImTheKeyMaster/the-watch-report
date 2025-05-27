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
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCp8M8IFaC6bjY5h3WDtHTaQ",  # Teddy Baldassarre
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC_wWGvT2ot2I4V8ADqdbR-w",  # Jenni Elle
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCk4z2uN4BFlF0U4uIUXwq3w",  # Nico Leonard
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCOpnj96gJqFHiyXBNz8ZpwA",  # The Time Teller
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCCaRjME-9QwGeq8vVNYG7og",  # Andrew Morgan
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCMcwrlH82Gr2gFh_vyHD6_w"   # Horological Society of New York
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
