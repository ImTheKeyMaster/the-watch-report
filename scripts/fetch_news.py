import feedparser
import json
import nltk
nltk.download('punkt', quiet=True, download_dir='/tmp/nltk_data')
import os
os.environ['NLTK_DATA'] = '/tmp/nltk_data'
from datetime import datetime, timezone
from newspaper import Article, Config
from slugify import slugify
import requests

# RSS feeds to parse
rss_feeds = [
    "https://www.hodinkee.com/articles/rss",
    "https://monochrome-watches.com/feed/",
    "https://wornandwound.com/feed/",
    "https://www.watchtime.com/feed/",
    "https://www.fratellowatches.com/feed/",
    "https://watchclicker.com/feed/",
    "https://www.timeandwatches.com/feeds/posts/default",
    "https://www.revolution.watch/feed/"
]

youtube_channels = [
    "UCPsgQZxEACESR0ogWm0dUFw",  # Teddy Baldassarre
    "UCvIIb5YF8sUnm1D62jCvVVw",  # BarkandJack
    "UCpGAs9xB__Y3W5d2WPC6wVw",  # Jenni Elle
    "UC-IVpEe1GQYclVEGLgPd82Q",  # Nico Leonard
    "UCt4id9K_t9zu-O23182P4vQ",  # The Time Teller
    "UCOu5VKZIHDXS-cHn9TOC0Qg",  # Andrew Morgan
    "UCF0mZ8eOx3ie5yCErYRoT5A",  # WatchFinder
    "UCZnVGL3UzxeC1LMrJGcI0Cg",  # Hodinkee
    "UCqRdOESEo9GGB1zh4YW1iKw",  # AboutEffingTime
    "UC0E08avdHIH-7AMeVcBGRPQ"   # Horological Society of New York
]

max_articles_per_feed = 3

# Configure user-agent for newspaper3k
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
config = Config()
config.browser_user_agent = user_agent

def is_valid_image_url(url):
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return response.status_code == 200
    except Exception as e:
        print(f"Invalid image URL: {url} - {e}")
        return False

all_articles = []

for url in rss_feeds:
    feed = feedparser.parse(url)
    print(f"Fetched {len(feed.entries)} entries from {url}")
    for entry in feed.entries[:max_articles_per_feed]:
        try:
            article = Article(entry.link, config=config)
            article.download()
            article.parse()
            published = entry.get("published_parsed") or entry.get("updated_parsed")
            published_date = datetime.fromtimestamp(0, tz=timezone.utc)
            if published:
                published_date = datetime(*published[:6], tzinfo=timezone.utc)

            thumbnail = ""
            if article.top_image and is_valid_image_url(article.top_image):
                thumbnail = article.top_image

            all_articles.append({
                "title": article.title,
                "link": entry.link,
                "source": feed.feed.get("title", ""),
                "published": published_date.isoformat(),
                "thumbnail": thumbnail
            })
        except Exception as e:
            print(f"Error processing article: {entry.link}\n{e}")

for channel_id in youtube_channels:
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    print(f"Fetched {len(feed.entries)} entries from {feed_url}")
    
    feed_channel_url = feed.feed.get("link", "")
    if not feed_channel_url.endswith(channel_id):
        print(f"❌ Skipping feed that doesn't match channel: {feed_channel_url}")
        continue

    for entry in feed.entries[:1]:  # Only latest video
        try:
            published = entry.get("published_parsed")
            published_date = datetime.fromtimestamp(0, tz=timezone.utc)
            if published:
                published_date = datetime(*published[:6], tzinfo=timezone.utc)
            media_thumbnail = entry.get("media_thumbnail", [{}])[0].get("url", "")
            if media_thumbnail and not is_valid_image_url(media_thumbnail):
                media_thumbnail = ""
            all_articles.append({
                "title": f"(VIDEO) {entry.title}",
                "link": entry.link,
                "source": feed.feed.get("title", "YouTube"),
                "published": published_date.isoformat(),
                "thumbnail": media_thumbnail
            })
        except Exception as e:
            print(f"Error processing YouTube entry: {entry.get('link', 'N/A')}\n{e}")

def parse_date(article):
    try:
        return datetime.fromisoformat(article["published"])
    except:
        return datetime.now(timezone.utc)

all_articles = sorted(all_articles, key=parse_date, reverse=True)

output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "news.json"), "w", encoding="utf-8") as f:
    json.dump(all_articles, f, indent=2, ensure_ascii=False)
